"""Fill Label/Description in the VoID-built ``<kg>_entities.csv`` files.

:mod:`mcp_okn.void_schema` writes each row's text from the KG's own graph (and
ubergraph for OBO terms). This module fills what is still missing, in order:

0. **The KG's own ontology release**, for vocabularies whose maintainers publish a
   newer release than the curated files describe (ContaminOSO for the SAWGraph
   graphs). Where the release has a label or description it wins, untagged.
1. **Curated text** from the ``sbl-sdsc/mcp-proto-okn`` file of the same KG,
   matched by URI, kind (Class / Predicate) and, for edge properties, the parent
   relationship. It is the primary source and replaces machine text.
2. **Existing text** already in the row (the KG's own, or ubergraph's) is kept.
3. **Another ontology or graph** — the vocabulary's own published document, the
   federation graph that defines the term, or the EBI Ontology Lookup Service —
   supplies the rest, tagged ``(source: …)``.
4. Nothing reliable found: the description stays empty and is reported. Nothing is
   invented; a label falls back to the IRI's local name, as before.

The usage notes the builder appends (``Used only inside class axioms, …``) are
data-derived facts, so they survive whichever text wins. Filling is idempotent:
run on an already-filled file, curated text is re-applied and everything else is
kept as existing text.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import httpx

from .schema import _is_provenance_uri
from .sparql import SparqlError, run_sparql
from .void_schema import (
    DESCRIPTION_PREDICATES,
    LABEL_PREDICATES,
    _clean,
    local_label,
    normalize_curated,
    obo_ontology,
    source_tag,
)

#: The usage sentences :func:`mcp_okn.void_schema.axiom_property_rows` and
#: :func:`~mcp_okn.void_schema.add_patterns` append, so they can be split off and
#: re-attached after the text that wins.
USAGE_NOTE_RE = re.compile(
    r"\s*((?:Used only|Also used) inside class axioms, as owl:onProperty of [\d,]+ "
    r"owl:Restrictions?(?:; never asserted as a direct triple)?\."
    r"|Declared in the schema but used in no triple or class axiom\."
    # The curated proto-okn files' own wording for the same fact (sawgraph).
    r"|Declared in the schema but not populated in the current release\.)\s*$"
)

#: Phrases showing a curated description already states how the predicate is used,
#: so the builder's note would only repeat it.
_CURATED_USAGE = ("owl:onProperty", "never asserted", "not populated")

_RESTRICTION_COUNT = re.compile(r"owl:onProperty of ([\d,]+)")

#: Extra text predicates for the cross-graph lookup (on top of the builder's).
EXTRA_LABEL_PREDICATES = ("http://www.w3.org/2004/02/skos/core#prefLabel",)

#: skos:altLabel is a label only where a KG's okn-registry entry says so (sudokn's
#: ``label`` role lists it). Elsewhere it holds synonyms: LinkML's altLabel for
#: ClassDefinition is "message", for class_uri "public ID".
ALT_LABEL = "http://www.w3.org/2004/02/skos/core#altLabel"
ALT_LABEL_GRAPHS = frozenset({"sudokn"})
EXTRA_DESCRIPTION_PREDICATES = (
    "http://www.w3.org/2004/02/skos/core#scopeNote",
    "http://schema.org/description",
    "https://schema.org/description",
)

#: SUDOKN names NAICS industries ``…/SUDOKN/NAICS311111.0`` (and ``NAICS111``).
NAICS_IRI = re.compile(r"^http://asu\.edu/semantics/SUDOKN/NAICS(\d{2,6})(?:\.0)?$")

#: Census marks a title "T" when the US, Canada and Mexico define it the same way.
_NAICS_TRILATERAL = re.compile(r"(?<=[a-z)])T$")
_NAICS_SECTIONS = re.compile(r"\b(?:Illustrative Examples|Cross-References)\b")

OLS_API = "https://www.ebi.ac.uk/ols4/api"
#: OLS keeps relations and annotation properties apart from classes.
OLS_KINDS = ("terms", "properties", "individuals")

_KG_PREFIX = "https://purl.org/okn/frink/kg/"


@dataclass
class TextHit:
    """Text for one URI from a non-curated source."""

    label: str = ""
    description: str = ""
    source: str = ""  # shown in the (source: …) tag; "" = the KG's own text


@dataclass
class FillReport:
    """What :func:`fill_records` did to one file."""

    sources: Counter[str] = field(default_factory=Counter)
    labels: Counter[str] = field(default_factory=Counter)
    unfilled: list[dict[str, str]] = field(default_factory=list)
    count_mismatches: list[str] = field(default_factory=list)


def split_note(description: str) -> tuple[str, str]:
    """``(text, usage note)`` — the builder's note split off the end."""
    m = USAGE_NOTE_RE.search(description or "")
    if not m:
        return (description or "").strip(), ""
    return description[: m.start()].strip(), m.group(1)


def join_text(text: str, note: str) -> str:
    """Re-attach a usage note unless the text already states the usage."""
    if note and not any(p in text for p in _CURATED_USAGE):
        return f"{text} {note}".strip()
    return text


_ID_LOCAL_NAME = re.compile(r"[A-Za-z]+[_:]?[A-Za-z]{0,3}\d+")


def id_only_label(label: str, uri: str) -> bool:
    """True when a label just spells out an id-style IRI (``NCIT C48192``)."""
    local = local_label(uri)
    norm = re.sub(r"[^a-z0-9]", "", label.lower())
    return bool(_ID_LOCAL_NAME.fullmatch(local)) and norm == re.sub(
        r"[^a-z0-9]", "", local.lower()
    )


def _kind(row_type: str) -> str:
    return "Class" if row_type == "Class" else "Predicate"


def _parent(value: str) -> str:
    return local_label(value) if value.startswith(("http://", "https://")) else value


def curated_index(
    records: list[dict[str, str]],
) -> dict[tuple[str, ...], tuple[str, str]]:
    """Curated ``(label, description)`` keyed three ways, most specific first.

    ``(uri, kind, parent)`` for edge properties (spoke-genelab's adj_p_value is
    described per relationship), ``(uri, kind)`` and ``(uri,)``. The parent is
    the curated row's OWN value: an IRI stays an exact IRI (``"P", iri``) and only
    a short name as written becomes a name key (``"S", name``). Resolving a short
    name to an IRI picks one arbitrarily when two predicates share a local name
    (prokn: biolink.github.io and w3id.org ``catalyzes``), and reducing an IRI to
    its local name would let one relationship's text land on the other.
    When a curated file repeats a key, the last non-empty value wins.
    """
    entries, _ = normalize_curated(records)
    rows = [
        r for r in records if r.get("URI") and not _is_provenance_uri(r["URI"].strip())
    ]
    index: dict[tuple[str, ...], tuple[str, str]] = {}
    for raw, e in zip(rows, entries, strict=True):
        keys: list[tuple[str, ...]] = [(e.uri, e.type), (e.uri,)]
        parent = (raw.get("EdgePropertyOf") or "").strip()
        if parent:
            tag = "P" if parent.startswith(("http://", "https://")) else "S"
            keys.insert(0, (e.uri, e.type, tag, parent))
        for key in keys:
            old_label, old_desc = index.get(key, ("", ""))
            index[key] = (e.label or old_label, e.description or old_desc)
    return index


def _curated_for(
    row: dict[str, str], index: dict[tuple[str, ...], tuple[str, str]]
) -> tuple[str, str]:
    uri, kind = row["URI"], _kind(row["Type"])
    keys: list[tuple[str, ...]] = [(uri, kind), (uri,)]
    parent = row.get("EdgePropertyOf") or ""
    if parent:
        # The exact parent IRI first; a curated short name applies to any parent
        # with that local name (that is all the curated row says).
        keys[:0] = [(uri, kind, "P", parent), (uri, kind, "S", _parent(parent))]
    label = desc = ""
    for key in keys:
        hit_label, hit_desc = index.get(key, ("", ""))
        label, desc = label or hit_label, desc or hit_desc
    return label, desc


def needs_lookup(
    records: Iterable[dict[str, str]],
    index: dict[tuple[str, ...], tuple[str, str]],
) -> set[str]:
    """URIs with no curated or existing description, or only a local-name label."""
    out = set()
    for r in records:
        label, desc = _curated_for(r, index)
        text, _note = split_note(r["Description"])
        if not (desc or text) or not (label or r["Label"] != local_label(r["URI"])):
            out.add(r["URI"])
    return out


def fill_records(
    records: list[dict[str, str]],
    index: dict[tuple[str, ...], tuple[str, str]],
    hits: dict[str, TextHit],
    release: dict[str, TextHit] | None = None,
) -> FillReport:
    """Fill each record's Label/Description in place (see the module docstring).

    ``release`` is text from the current release of the KG's own ontology
    (ContaminOSO for the SAWGraph graphs). It supersedes the curated text, which
    was written against an earlier release, wherever the release has text.
    """
    report = FillReport()
    release = release or {}
    for r in records:
        cur_label, cur_desc = _curated_for(r, index)
        text, note = split_note(r["Description"])
        hit = hits.get(r["URI"])
        rel = release.get(r["URI"])
        if rel:
            cur_label = rel.label or cur_label

        if rel and rel.description:
            r["Description"] = join_text(rel.description, note)
            report.sources["release"] += 1
        elif cur_desc:
            ours, theirs = (
                _RESTRICTION_COUNT.search(note),
                _RESTRICTION_COUNT.search(cur_desc),
            )
            if ours and theirs and ours.group(1) != theirs.group(1):
                report.count_mismatches.append(
                    f"{r['URI']}: curated says {theirs.group(1)} restrictions, "
                    f"the served graph has {ours.group(1)}"
                )
            r["Description"] = join_text(cur_desc, note)
            report.sources["curated"] += 1
        elif text:
            report.sources["existing" if "(source: " not in text else "ontology"] += 1
        elif hit and hit.description:
            tagged = hit.description + (source_tag(hit.source) if hit.source else "")
            r["Description"] = join_text(tagged, note)
            report.sources["ontology" if hit.source else "existing"] += 1
        else:
            report.sources["unfilled"] += 1
            report.unfilled.append(
                {
                    "URI": r["URI"],
                    "Type": r["Type"],
                    "EdgePropertyOf": r.get("EdgePropertyOf", ""),
                    "Label": cur_label or r["Label"],
                }
            )

        fallback = local_label(r["URI"])
        real_label = r["Label"] and r["Label"] != fallback
        if cur_label and id_only_label(cur_label, r["URI"]) and real_label:
            # A curated label that only spells out the id (aopwiki's "NCIT C48192")
            # must not replace the graph's real name for it ("Importance Weight").
            report.labels["existing"] += 1
        elif cur_label:
            r["Label"] = cur_label
            report.labels["release" if rel and rel.label else "curated"] += 1
        elif r["Label"] and r["Label"] != fallback:
            report.labels["existing"] += 1
        elif hit and hit.label:
            r["Label"] = hit.label
            report.labels["ontology" if hit.source else "existing"] += 1
        else:
            r["Label"] = r["Label"] or fallback
            report.labels["local name"] += 1
    return report


def dedupe_unfilled(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    """One unfilled entry per (URI, Type, EdgePropertyOf), in first-seen order."""
    seen: set[tuple[str, str, str]] = set()
    out = []
    for r in rows:
        key = (r["URI"], r["Type"], r.get("EdgePropertyOf", ""))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def naics_code(uri: str) -> str | None:
    """The NAICS code a SUDOKN IRI names, or None."""
    m = NAICS_IRI.match(uri)
    return m.group(1) if m else None


def naics_hit(code: str, title: str, description: str, edition: str) -> TextHit:
    """Census title + definition for one NAICS code.

    Keeps the definition paragraphs, not the "Illustrative Examples" and
    "Cross-References" lists that follow them, and drops the trailing "T" marker.
    """
    title = _NAICS_TRILATERAL.sub("", (title or "").strip())
    definition = _clean(_NAICS_SECTIONS.split(description or "", maxsplit=1)[0])
    text = f"NAICS {code}: {title}." + (f" {definition}" if definition else "")
    return TextHit(
        label=f"NAICS {code}: {title}",
        description=text,
        source=f"U.S. Census Bureau, NAICS {edition}",
    )


# ------------------------------------------------------------------ live lookups


def federation_text_query(uris: Iterable[str]) -> str:
    """English/untagged label and description literals for URIs, in any graph."""
    values = " ".join(f"<{u}>" for u in uris)
    preds = " ".join(
        f"<{p}>"
        for p in (
            *LABEL_PREDICATES,
            *EXTRA_LABEL_PREDICATES,
            ALT_LABEL,
            *DESCRIPTION_PREDICATES,
            *EXTRA_DESCRIPTION_PREDICATES,
        )
    )
    return f"""\
SELECT ?u ?g ?p ?o WHERE {{
  VALUES ?u {{ {values} }}
  VALUES ?p {{ {preds} }}
  GRAPH ?g {{ ?u ?p ?o }}
  FILTER(isLiteral(?o) && (LANG(?o) = "" || LANGMATCHES(LANG(?o), "en")))
}}"""


def pick_federation_hits(
    rows: Iterable[dict[str, Any]], own_graph: dict[str, str]
) -> dict[str, TextHit]:
    """Best text per URI from :func:`federation_text_query` rows.

    The KG's own graph wins (no tag), then ubergraph, then other graphs by name;
    within a graph, predicates in preference order. ``own_graph`` maps a URI to the
    graph of the KG being filled.
    """
    label_rank = [*LABEL_PREDICATES, *EXTRA_LABEL_PREDICATES, ALT_LABEL]
    desc_rank = [*DESCRIPTION_PREDICATES, *EXTRA_DESCRIPTION_PREDICATES]
    best: dict[str, dict[str, tuple[tuple[int, str, int, str], str]]] = {}
    for r in rows:
        u, g, p, o = r.get("u", ""), r.get("g", ""), r.get("p", ""), r.get("o", "")
        text = _clean(str(o))
        if not (u and g and text):
            continue
        shortname = g.removeprefix(_KG_PREFIX)
        if p == ALT_LABEL and shortname not in ALT_LABEL_GRAPHS:
            continue
        g_rank = 0 if g == own_graph.get(u) else 1 if shortname == "ubergraph" else 2
        for kind, ranking in (("label", label_rank), ("description", desc_rank)):
            if p in ranking:
                key = (g_rank, shortname, ranking.index(p), text)
                cur = best.setdefault(u, {}).get(kind)
                if cur is None or key < cur[0]:
                    best[u][kind] = (key, shortname if g_rank else "")
    out: dict[str, TextHit] = {}
    for u, kinds in best.items():
        hit = TextHit()
        if "label" in kinds:
            hit.label = kinds["label"][0][3]
        if "description" in kinds:
            (_rank, shortname, _p, text), own = kinds["description"]
            hit.description = text
            if own:
                hit.source = (
                    f"{_obo_name(u)} via ubergraph"
                    if shortname == "ubergraph"
                    else f"{shortname} KG"
                )
        out[u] = hit
    return out


def _obo_name(uri: str) -> str:
    return obo_ontology(uri) if "purl.obolibrary.org/obo/" in uri else "ubergraph"


async def federation_text(
    uris: list[str],
    own_graph: dict[str, str],
    client: httpx.AsyncClient | None = None,
    batch: int = 50,
    log: Any = print,
) -> dict[str, TextHit]:
    """Cross-graph text for URIs (see :func:`pick_federation_hits`)."""
    rows: list[dict[str, Any]] = []
    for i in range(0, len(uris), batch):
        try:
            res = await run_sparql(
                federation_text_query(uris[i : i + batch]), client=client, timeout=300
            )
        except SparqlError as exc:
            log(f"  federation text lookup failed for a batch: {str(exc)[:120]}")
            continue
        rows.extend(res["rows"])
    return pick_federation_hits(rows, own_graph)


def pick_ols_hit(kind_results: dict[str, list[dict[str, Any]]]) -> TextHit | None:
    """The defining ontology's entry from OLS ``/terms|/properties|/individuals``."""
    for kind in OLS_KINDS:
        terms = kind_results.get(kind) or []
        if not terms:
            continue
        term = next((t for t in terms if t.get("is_defining_ontology")), terms[0])
        desc = " ".join(_clean(d) for d in (term.get("description") or []) if d)
        prefix = (
            term.get("ontology_prefix") or term.get("ontology_name") or ""
        ).upper()
        return TextHit(
            label=_clean(term.get("label") or ""),
            description=desc,
            source=f"{prefix} via OLS" if desc else "",
        )
    return None


async def ols_text(
    uris: list[str], client: httpx.AsyncClient, log: Any = print
) -> dict[str, TextHit]:
    """OLS text for OBO URIs: classes, then properties, then individuals."""
    out: dict[str, TextHit] = {}
    for uri in uris:
        found: dict[str, list[dict[str, Any]]] = {}
        for kind in OLS_KINDS:
            try:
                resp = await client.get(f"{OLS_API}/{kind}", params={"iri": uri})
                data = resp.json() if resp.status_code == 200 else {}
            except (httpx.HTTPError, ValueError) as exc:
                log(f"  OLS lookup failed for {uri}: {str(exc)[:80]}")
                data = {}
            found[kind] = data.get("_embedded", {}).get(kind, [])
            if found[kind]:
                break
        hit = pick_ols_hit(found)
        if hit:
            out[uri] = hit
    return out
