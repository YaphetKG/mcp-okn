"""Keep a ``get_schema`` reply readable: a size budget and a ``match`` filter.

Clients cap the size of a tool reply. Claude Code saves anything over its limit
(25,000 tokens by default) to a file and hands the agent a pointer instead, so a
too-large schema reaches the agent as no schema at all. In the 2026-10-16
single-graph benchmark, spoke-okn's 65K-character schema went that way on every
attempt, and each agent fell back to scanning every predicate in the live graph
by name, which timed out after 120 s.

:func:`fit_to_budget` therefore trims DETAIL, never silently: it drops the
repeated parts first, then descriptions, and only then rows (largest kept, by
instance or triple count), recording each step and every omitted count under
``schema_view``. :func:`match_schema` is how the rest stays reachable: it keeps
full detail for the entries a term finds, from the same metadata, with no
endpoint round trip.
"""

from __future__ import annotations

import copy
import json
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

#: Characters of compact JSON a reply may use. Claude Code delivered a 43,920-
#: character schema and spilled a 49,800-character one; 40,000 leaves room for
#: clients that count more conservatively.
SCHEMA_CHAR_BUDGET = 40_000

#: Rows each table keeps before the last-resort pass may cut it further.
ROW_FLOORS = {"classes": 50, "node_properties": 50, "edge_properties": 20}

MATCH_HINT = (
    "Call get_schema({kg!r}, match='<term>') for full detail (descriptions, edge "
    "properties, query templates) on every class, predicate or property whose IRI, "
    "label or description contains the term; separate alternatives with '|', e.g. "
    "match='prevalence|population'. It reads the same schema metadata, so it is "
    "instant, unlike scanning the live graph."
)


def reply_size(reply: dict[str, Any]) -> int:
    """Length of ``reply`` as compact JSON, the form a client receives."""
    return len(json.dumps(reply, separators=(",", ":")))


# ── tables ───────────────────────────────────────────────────────────────────


def _rows(table: dict[str, Any]) -> list[dict[str, Any]]:
    cols = table.get("columns", [])
    return [dict(zip(cols, row, strict=False)) for row in table.get("data", [])]


def _set_rows(table: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    cols = table.get("columns", [])
    table["data"] = [[r.get(c) for c in cols] for r in rows]
    table["count"] = len(rows)


def _drop_column(table: dict[str, Any] | None, col: str) -> bool:
    if not table or col not in table.get("columns", []):
        return False
    if not any(row[table["columns"].index(col)] for row in table.get("data", [])):
        return False
    i = table["columns"].index(col)
    table["columns"] = table["columns"][:i] + table["columns"][i + 1 :]
    table["data"] = [row[:i] + row[i + 1 :] for row in table["data"]]
    return True


def _by_size(table: dict[str, Any]) -> None:
    """Order rows largest first by ``instances``/``triples``, when either exists."""
    cols = table.get("columns", [])
    key = next((c for c in ("instances", "triples") if c in cols), None)
    if key is not None:
        i = cols.index(key)
        table["data"].sort(key=lambda row: -(row[i] or 0))


def _drop_constant_columns(schema: dict[str, Any]) -> bool:
    """Drop ``type`` where every row says the same (``Predicate``, ``Class``)."""
    hit = False
    for name in ("classes", "predicates", "node_properties"):
        table = schema.get(name)
        if not isinstance(table, dict) or "type" not in table.get("columns", []):
            continue
        i = table["columns"].index("type")
        if len({row[i] for row in table["data"]}) <= 1:
            hit = _drop_column(table, "type") or hit
    return hit


# ── prefixes ─────────────────────────────────────────────────────────────────

#: Names for namespaces common across the KGs; others are named from the IRI.
KNOWN_PREFIXES = {
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
    "http://www.w3.org/2002/07/owl#": "owl",
    "http://www.w3.org/2001/XMLSchema#": "xsd",
    "http://www.w3.org/2004/02/skos/core#": "skos",
    "http://purl.org/dc/terms/": "dcterms",
    "http://purl.obolibrary.org/obo/": "obo",
    "https://w3id.org/biolink/vocab/": "biolink",
    "http://www.opengis.net/ont/geosparql#": "geo",
    # The scheme stays visible: some graphs store the https form, which an
    # http IRI never matches (nikg, ruralkg, ufokn, spoke-okn).
    "http://purl.uniprot.org/core/": "up",
    "http://purl.org/dc/elements/1.1/": "dc",
    "http://www.w3.org/ns/prov#": "prov",
    "http://www.w3.org/ns/sosa/": "sosa",
    "http://www.w3.org/2006/time#": "time",
    "http://qudt.org/schema/qudt/": "qudt",
    "http://semanticscience.org/resource/": "sio",
    "http://schema.org/": "schema",
    "https://schema.org/": "schema_https",
}

#: A KG's own schema namespace is ``kg:`` (not ``schema:``, which reads as
#: schema.org).
_KG_NS = re.compile(r"^https?://purl\.org/okn/frink/kg/[^/]+/schema/$")

_IRI = re.compile(r"^(https?://.*[/#])([^/#]*)$")
#: A local part SPARQL accepts after ``prefix:`` without escaping.
_LOCAL = re.compile(r"^[A-Za-z0-9_](?:[A-Za-z0-9_.\-]*[A-Za-z0-9_\-])?$")


def _split(iri: str) -> tuple[str, str] | None:
    m = _IRI.match(iri)
    if not m or not _LOCAL.match(m.group(2)):
        return None
    return m.group(1), m.group(2)


#: Path segments too generic to name a namespace by (``…/ontology/``, ``…/rdf/``).
_GENERIC_SEGMENTS = {
    "ontology",
    "ontologies",
    "schema",
    "rdf",
    "core",
    "resource",
    "id",
    "vocab",
    "ns",
    "lod",
    "owl",
    "def",
    "terms",
}


def _prefix_name(ns: str, taken: set[str]) -> str:
    name = KNOWN_PREFIXES.get(ns) or ("kg" if _KG_NS.match(ns) else None)
    if name is None:
        # A known namespace under the other scheme (prokn types nodes with
        # https://www.w3.org/2002/07/owl#Class): owl_https, not a fresh name.
        scheme, _, rest = ns.partition("://")
        other = KNOWN_PREFIXES.get(
            ("http" if scheme == "https" else "https") + "://" + rest
        )
        if other:
            name = f"{other}_{scheme}"
    if name is None:
        host, _, path = ns.split("://", 1)[-1].partition("/")
        words = [
            w
            for w in re.split(r"[/#]", path)
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", w)
            and w.lower() not in _GENERIC_SEGMENTS
            and not re.fullmatch(r"[vV]\d+", w)
        ]
        labels = [h for h in host.split(".") if h not in ("www", "w3id", "purl")]
        word = words[-1] if words else (labels[-2] if len(labels) > 1 else "ns")
        name = word.lower().replace("-", "_")
        if name in {"kg", *KNOWN_PREFIXES.values()}:
            # Keep the well-known names unambiguous: a derived `schema` must not
            # be read as schema.org.
            name = f"{name}_ns"
    base, n = name, 2
    while name in taken:
        name, n = f"{base}{n}", n + 1
    return name


def _iri_cells(schema: dict[str, Any]) -> list[tuple[Any, Any]]:
    """Every (container, key) holding IRIs: table cells, edge entries, guidance."""
    cells: list[tuple[Any, Any]] = []
    iri_cols = {"uri", "source_class", "target_class", "class"}
    for name in ("classes", "predicates", "node_properties"):
        table = schema.get(name)
        if not isinstance(table, dict):
            continue
        idx = [i for i, c in enumerate(table.get("columns", [])) if c in iri_cols]
        cells += [(row, i) for row in table["data"] for i in idx]
    for entry in (schema.get("edge_properties") or {}).values():
        cells += [(entry, k) for k in ("uri", "source_class", "target_class")]
        cells += [(p, "uri") for p in entry.get("properties", [])]
    for entry in (schema.get("pattern_guidance") or {}).values():
        uris = entry.get("predicates")
        if isinstance(uris, list):
            cells += [(uris, i) for i in range(len(uris))]
    return cells


def _values(cell: Any) -> list[str]:
    return cell.split("|") if isinstance(cell, str) else []


def compact_iris(schema: dict[str, Any]) -> dict[str, str]:
    """Rewrite IRIs as ``prefix:local`` in place; return ``{prefix: namespace}``.

    Only namespaces used at least three times get a prefix, and a local part
    SPARQL would need escaped keeps its full IRI, so every short form expands
    back exactly. ``|``-joined lists (curated multi-class cells) are rewritten
    item by item.
    """
    cells = _iri_cells(schema)
    counts: Counter[str] = Counter()
    for container, key in cells:
        for v in _values(container[key]):
            parts = _split(v)
            if parts:
                counts[parts[0]] += 1
    taken: set[str] = set()
    prefixes: dict[str, str] = {}
    for ns, n in counts.most_common():
        if n >= 3:
            name = _prefix_name(ns, taken)
            taken.add(name)
            prefixes[ns] = name
    if not prefixes:
        return {}

    def short(v: str) -> str:
        parts = _split(v)
        if parts and parts[0] in prefixes:
            return f"{prefixes[parts[0]]}:{parts[1]}"
        return v

    for container, key in cells:
        if isinstance(container[key], str):
            container[key] = "|".join(short(v) for v in _values(container[key]))
    return {name: ns for ns, name in prefixes.items()}


# ── budget ───────────────────────────────────────────────────────────────────


def _cap(
    reply: dict[str, Any],
    get: Callable[[], list[Any]],
    put: Callable[[list[Any]], None],
    budget: int,
    floor: int,
) -> int:
    """Keep the longest prefix of ``get()`` (not below ``floor``) that fits.

    Returns how many items were removed.
    """
    items = get()
    if reply_size(reply) <= budget or len(items) <= floor:
        return 0
    lo, hi = floor, len(items)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        put(items[:mid])
        if reply_size(reply) <= budget:
            lo = mid
        else:
            hi = mid - 1
    put(items[:lo])
    return len(items) - lo


def fit_to_budget(
    reply: dict[str, Any], kg: str, budget: int = SCHEMA_CHAR_BUDGET
) -> dict[str, Any]:
    """Trim ``reply`` until it fits ``budget``, recording what was left out.

    A reply that already fits is returned unchanged. ``usage_notes`` and
    ``next_step`` are never trimmed.
    """
    if reply_size(reply) <= budget or "schema" not in reply:
        return reply
    reply = copy.deepcopy(reply)
    schema = reply["schema"]
    view = reply.setdefault("schema_view", {})
    view["budget_chars"] = budget
    trimmed: list[str] = view.setdefault("trimmed", [])
    omitted: dict[str, int] = view.setdefault("omitted", {})
    view["how_to_get_more"] = MATCH_HINT.format(kg=kg)
    edges: dict[str, Any] = schema.get("edge_properties") or {}

    def drop_summary() -> bool:
        return schema.pop("edge_property_summary", None) is not None

    def drop_templates() -> bool:
        hit = False
        for entry in edges.values():
            hit = entry.pop("query_template", None) is not None or hit
        return hit

    def drop_edge_text() -> bool:
        hit = False
        for entry in edges.values():
            for prop in entry.get("properties", []):
                hit = prop.pop("description", None) is not None or hit
                prop.pop("type", None)
        return hit

    def prefix_iris() -> bool:
        prefixes = compact_iris(schema)
        if prefixes:
            view["prefixes"] = prefixes
            view["sparql_prefixes"] = "\n".join(
                f"PREFIX {name}: <{ns}>" for name, ns in prefixes.items()
            )
        return bool(prefixes)

    steps: list[tuple[str, Callable[[], bool]]] = [
        ("edge_property_summary (repeats edge_properties)", drop_summary),
        ("edge_properties query_template", drop_templates),
        ("constant type column", lambda: _drop_constant_columns(schema)),
        (
            "predicates has_edge_properties (edge_properties lists them)",
            lambda: _drop_column(schema.get("predicates"), "has_edge_properties"),
        ),
        ("IRIs written as prefix:local (see schema_view.prefixes)", prefix_iris),
        ("edge property descriptions", drop_edge_text),
        (
            "node_properties descriptions",
            lambda: _drop_column(schema.get("node_properties"), "description"),
        ),
        (
            "classes descriptions",
            lambda: _drop_column(schema.get("classes"), "description"),
        ),
        (
            "predicates other_pairs",
            lambda: _drop_column(schema.get("predicates"), "other_pairs"),
        ),
        (
            "predicates descriptions",
            lambda: _drop_column(schema.get("predicates"), "description"),
        ),
    ]
    for label, step in steps:
        if reply_size(reply) <= budget:
            break
        if step():
            trimmed.append(label)

    for table_name in ("classes", "node_properties", "predicates"):
        if isinstance(schema.get(table_name), dict):
            _by_size(schema[table_name])

    def table_cap(name: str, floor: int) -> None:
        table = schema.get(name)
        if not isinstance(table, dict) or reply_size(reply) <= budget:
            return
        total = table.get("count", len(table.get("data", [])))

        def put(rows: list[Any]) -> None:
            table["data"] = rows
            table["count"] = len(rows)

        # The notes a cut adds are sized in before cutting, at an upper bound
        # (the real count is never longer), so they cannot push the reply over.
        before = omitted.get(name, 0)
        omitted[name] = before + len(table.get("data", []))
        table.setdefault("total", total)
        cut = _cap(reply, lambda: list(table["data"]), put, budget, floor)
        omitted[name] = before + cut
        if not cut and table["total"] == table["count"]:
            del table["total"]

    def edge_cap(floor: int) -> None:
        if reply_size(reply) <= budget:
            return
        names = list(edges)
        snapshot = dict(edges)

        def put_from_snapshot(keep: list[str]) -> None:
            edges.clear()
            edges.update({k: snapshot[k] for k in keep})

        before = omitted.get("edge_properties", 0)
        omitted["edge_properties"] = before + len(names)
        cut = _cap(reply, lambda: names, put_from_snapshot, budget, floor)
        omitted["edge_properties"] = before + cut

    # Rows go last, longest lists first, each down to a floor; then, only if
    # that still does not fit, below it (predicates included).
    view["rows_kept"] = "largest first, by instance or triple count"
    # Below the floors, edge-property entries go first: each one's relationship
    # keeps its row in the predicates table, and match brings the entry back.
    table_cap("classes", ROW_FLOORS["classes"])
    table_cap("node_properties", ROW_FLOORS["node_properties"])
    edge_cap(ROW_FLOORS["edge_properties"])
    edge_cap(0)
    table_cap("node_properties", 0)
    table_cap("classes", 0)
    table_cap("predicates", 0)

    for name in [k for k, v in omitted.items() if not v]:
        del omitted[name]
    if not omitted:
        view.pop("omitted")
        view.pop("rows_kept")
    return reply


# ── match ────────────────────────────────────────────────────────────────────


def match_schema(reply: dict[str, Any], term: str) -> dict[str, Any]:
    """Keep only the schema entries ``term`` finds, with their full detail.

    ``term`` is a case-insensitive substring tested against each entry's IRI,
    label and description; ``|`` separates alternatives. A predicate is kept
    when it matches, when its source or target class matches, or when one of
    its edge properties matches; the classes those predicates connect are kept
    with them, so the reply is a usable neighbourhood rather than a word list.
    """
    if "schema" not in reply:
        return reply
    terms = [t.strip().lower() for t in term.split("|") if t.strip()]
    reply = copy.deepcopy(reply)
    schema = reply["schema"]

    def hit(*values: Any) -> bool:
        text = " ".join(str(v) for v in values if v).lower()
        return any(t in text for t in terms)

    classes = _rows(schema.get("classes") or {})
    preds = _rows(schema.get("predicates") or {})
    nodes = _rows(schema.get("node_properties") or {})
    edges: dict[str, Any] = schema.get("edge_properties") or {}

    matched_classes = {
        key
        for c in classes
        if hit(c.get("uri"), c.get("label"), c.get("description"))
        for key in (c.get("uri"), c.get("label"))
        if key
    }
    edge_hits = {
        entry.get("uri")
        for name, entry in edges.items()
        if hit(name, entry.get("uri"), entry.get("description"))
        or any(
            hit(p.get("uri"), p.get("label"), p.get("description"))
            for p in entry.get("properties", [])
        )
    }
    kept_preds = [
        p
        for p in preds
        if hit(p.get("uri"), p.get("label"), p.get("description"))
        or p.get("source_class") in matched_classes
        or p.get("target_class") in matched_classes
        or p.get("uri") in edge_hits
    ]
    kept_pred_uris = {p.get("uri") for p in kept_preds}
    kept_nodes = [
        n
        for n in nodes
        if hit(n.get("uri"), n.get("label"), n.get("description"))
        or n.get("class") in matched_classes
    ]
    linked = (
        matched_classes
        | {p.get("source_class") for p in kept_preds}
        | {p.get("target_class") for p in kept_preds}
        | {n.get("class") for n in kept_nodes}
    )
    kept_classes = [
        c for c in classes if c.get("uri") in linked or c.get("label") in linked
    ]
    kept_edges = {
        name: entry
        for name, entry in edges.items()
        if entry.get("uri") in kept_pred_uris or entry.get("uri") in edge_hits
    }

    totals = {
        "classes": len(classes),
        "predicates": len(preds),
        "node_properties": len(nodes),
        "edge_properties": len(edges),
    }
    for name, rows in (
        ("classes", kept_classes),
        ("predicates", kept_preds),
        ("node_properties", kept_nodes),
    ):
        if isinstance(schema.get(name), dict):
            _set_rows(schema[name], rows)
    if "edge_properties" in schema:
        schema["edge_properties"] = kept_edges
    summary = schema.get("edge_property_summary")
    if isinstance(summary, dict):
        summary["edges_with_properties"] = [
            e
            for e in summary.get("edges_with_properties", [])
            if e.get("relationship") in kept_edges
        ]

    found = {
        "classes": len(kept_classes),
        "predicates": len(kept_preds),
        "node_properties": len(kept_nodes),
        "edge_properties": len(kept_edges),
    }
    view: dict[str, Any] = {"match": term, "found": found, "of": totals}
    if not any(found.values()):
        view["note"] = (
            "Nothing in this KG's schema metadata matches. Try a broader or "
            "different term (a synonym, a fragment of the IRI), or call get_schema "
            "without match to see the overview."
        )
    reply["schema_view"] = view
    return reply
