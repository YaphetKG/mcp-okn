"""Fill Label/Description in metadata/void_entities/*_entities.csv (see mcp_okn.void_text).

Order per row: the curated proto-okn text, else the text already there (the KG's
own, or ubergraph's), else another ontology — the vocabulary's own published
document, the federation graph that defines the term, or OLS — tagged
``(source: …)``. Anything else stays empty and is listed in ``TEXT_FILL.md`` and
``unfilled_descriptions.csv``.

External answers are cached in ``text_cache.json`` (committed) so a rebuild is
stable and offline; ``--refresh`` re-fetches them. Run automatically at the end of
``build_void_schema.py``; also safe to run on its own (filling is idempotent).

Usage:
    uv run python scripts/fill_void_text.py               # every file in the dir
    uv run python scripts/fill_void_text.py --kg bio101   # one KG (repeatable)
    uv run python scripts/fill_void_text.py --refresh     # ignore the cache
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import httpx

from mcp_okn import void_schema as vs
from mcp_okn import void_text as vt

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "metadata" / "void_entities"
SUFFIX = "_entities.csv"
CACHE = "text_cache.json"

#: Vocabularies whose own published document is the authority for their terms:
#: namespace → (name for the source tag, document URLs to try in order).
#: Verified 2026-10-16: each parses. Coverage of the terms the files use varies
#: (OWL 60/64, schema.org 17/18, oboInOwl 7/88: its document omits most of the
#: properties OBO files use); what a document lacks falls through to OLS or stays
#: unfilled.
VOCABS: dict[str, tuple[str, list[str]]] = {
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#": (
        "RDF",
        ["http://www.w3.org/1999/02/22-rdf-syntax-ns"],
    ),
    "http://www.w3.org/2000/01/rdf-schema#": (
        "RDFS",
        ["http://www.w3.org/2000/01/rdf-schema"],
    ),
    "http://www.w3.org/2002/07/owl#": ("OWL", ["http://www.w3.org/2002/07/owl"]),
    "http://www.w3.org/2004/02/skos/core#": (
        "SKOS",
        ["http://www.w3.org/2004/02/skos/core"],
    ),
    "http://purl.org/dc/terms/": (
        "DCMI Terms",
        [
            "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/"
            "dublin_core_terms.ttl"
        ],
    ),
    "http://purl.org/dc/elements/1.1/": (
        "Dublin Core Elements",
        [
            "https://www.dublincore.org/specifications/dublin-core/dcmi-terms/"
            "dublin_core_elements.ttl"
        ],
    ),
    "http://www.w3.org/2003/11/swrl#": (
        "SWRL",
        ["http://www.w3.org/Submission/SWRL/swrl.owl"],
    ),
    "http://www.w3.org/2006/time#": ("OWL-Time", ["http://www.w3.org/2006/time"]),
    "http://schema.org/": (
        "schema.org",
        ["https://schema.org/version/latest/schemaorg-current-http.ttl"],
    ),
    "https://schema.org/": (
        "schema.org",
        ["https://schema.org/version/latest/schemaorg-current-https.ttl"],
    ),
    "http://www.w3.org/ns/sparql-service-description#": (
        "SPARQL Service Description",
        ["http://www.w3.org/ns/sparql-service-description"],
    ),
    "http://www.w3.org/ns/prov#": ("PROV-O", ["http://www.w3.org/ns/prov-o"]),
    "http://www.w3.org/ns/shacl#": ("SHACL", ["http://www.w3.org/ns/shacl.ttl"]),
    "http://xmlns.com/foaf/0.1/": ("FOAF", ["http://xmlns.com/foaf/spec/index.rdf"]),
    "http://usefulinc.com/ns/doap#": (
        "DOAP",
        ["https://raw.githubusercontent.com/ewilderj/doap/master/schema/doap.rdf"],
    ),
    "http://purl.org/vocab/vann/": (
        "VANN",
        ["https://vocab.org/vann/vann-vocab-20100607.rdf"],
    ),
    "http://www.geneontology.org/formats/oboInOwl#": (
        "oboInOwl",
        [
            "https://raw.githubusercontent.com/geneontology/go-ontology/master/"
            "contrib/oboInOwl.owl"
        ],
    ),
    "https://w3id.org/linkml/": ("LinkML", ["https://w3id.org/linkml/meta"]),
    "http://qudt.org/schema/qudt/": ("QUDT", ["http://qudt.org/schema/qudt/"]),
    "http://semanticscience.org/resource/": (
        "SIO",
        ["http://semanticscience.org/ontology/sio.owl"],
    ),
}

#: Vocabulary-specific description predicates: LinkML describes its own terms with
#: linkml:description, not rdfs:comment.
VOCAB_DESCRIPTION_PREDICATES = ("https://w3id.org/linkml/description",)

#: Unfilled terms sampled per namespace before asking OLS about the rest of it, so
#: KG-local namespaces OLS does not index (SUDOKN, aura) cost three calls, not 700.
OLS_SAMPLE = 3

_ACCEPT = "text/turtle, application/rdf+xml;q=0.9, application/ld+json;q=0.8, */*;q=0.1"
_FORMATS = {
    "text/turtle": "turtle",
    "application/rdf+xml": "xml",
    "application/ld+json": "json-ld",
    "application/n-triples": "nt",
}


def _namespace(uri: str) -> str:
    return uri.rsplit("#", 1)[0] + "#" if "#" in uri else uri.rsplit("/", 1)[0] + "/"


def _vocab_of(uri: str) -> str | None:
    return next((ns for ns in VOCABS if uri.startswith(ns)), None)


async def vocab_text(
    namespace: str, uris: list[str], client: httpx.AsyncClient
) -> dict[str, vt.TextHit]:
    """Text for ``uris`` from the vocabulary's own document (parsed with rdflib)."""
    import rdflib  # transitive dependency (sparql-to-mermaid); only this script uses it

    name, urls = VOCABS[namespace]
    labels = [
        rdflib.URIRef(p) for p in (*vs.LABEL_PREDICATES, *vt.EXTRA_LABEL_PREDICATES)
    ]
    descs = [
        rdflib.URIRef(p)
        for p in (
            *vs.DESCRIPTION_PREDICATES,
            *vt.EXTRA_DESCRIPTION_PREDICATES,
            *VOCAB_DESCRIPTION_PREDICATES,
        )
    ]
    graph = None
    for url in urls:
        try:
            resp = await client.get(url, headers={"Accept": _ACCEPT})
            ctype = resp.headers.get("content-type", "").split(";")[0].strip()
            fmt = _FORMATS.get(ctype) or ("turtle" if url.endswith(".ttl") else "xml")
            graph = rdflib.Graph()
            graph.parse(data=resp.content, format=fmt)
            break
        except Exception as exc:  # any fetch or parse failure: try the next URL
            print(f"  {name}: {url} unusable ({type(exc).__name__})")
            graph = None
    if graph is None:
        return {}

    def first(subject: Any, preds: list[Any]) -> str:
        for p in preds:
            vals = sorted(
                vs._clean(str(o))
                for o in graph.objects(subject, p)
                if isinstance(o, rdflib.Literal) and o.language in (None, "en")
            )
            if vals:
                return vals[0]
        return ""

    out = {}
    for u in uris:
        ref = rdflib.URIRef(u)
        label, desc = first(ref, labels), first(ref, descs)
        if label or desc:
            out[u] = vt.TextHit(
                label=label, description=desc, source=name if desc else ""
            )
    return out


def _hit_to_json(hit: vt.TextHit | None) -> dict[str, str] | None:
    return None if hit is None else vars(hit)


def _merge(*hits: vt.TextHit | None) -> vt.TextHit | None:
    """Label from the first hit that has one; description (and its source) likewise."""
    present = [h for h in hits if h]
    if not present:
        return None
    out = vt.TextHit()
    for h in present:
        out.label = out.label or h.label
        if not out.description and h.description:
            out.description, out.source = h.description, h.source
    return out


async def resolve(
    needed: dict[str, set[str]],
    cache: dict[str, Any],
    refresh: bool,
    client: httpx.AsyncClient,
) -> dict[str, dict[str, vt.TextHit]]:
    """Per KG, ``{uri: TextHit}`` for the URIs that need text.

    Vocabulary documents and OLS answers do not depend on the KG, so they are
    cached per URI. Federation rows are cached raw, because which graph counts as
    "the KG's own" (no tag) depends on the KG being filled.
    """
    all_uris = sorted({u for us in needed.values() for u in us})
    vocab_cache = {} if refresh else cache.setdefault("vocab", {})
    fed_cache = {} if refresh else cache.setdefault("federation", {})
    ols_cache = {} if refresh else cache.setdefault("ols", {})

    by_ns: dict[str, list[str]] = {}
    for u in all_uris:
        ns = _vocab_of(u)
        if ns and u not in vocab_cache:
            by_ns.setdefault(ns, []).append(u)
    for ns, uris in sorted(by_ns.items()):
        print(f"  vocabulary {VOCABS[ns][0]}: {len(uris)} term(s)")
        hits = await vocab_text(ns, uris, client)
        for u in uris:
            vocab_cache[u] = _hit_to_json(hits.get(u))

    fed_todo = [u for u in all_uris if u not in fed_cache]
    if fed_todo:
        print(f"  federation: {len(fed_todo)} URI(s)")
        for i in range(0, len(fed_todo), 50):
            batch = fed_todo[i : i + 50]
            try:
                res = await vs.run_sparql(
                    vt.federation_text_query(batch), client=None, timeout=300
                )
            except vs.SparqlError as exc:
                print(f"  federation batch failed: {str(exc)[:100]}")
                continue
            rows: dict[str, list[dict[str, str]]] = {u: [] for u in batch}
            for r in res["rows"]:
                rows.setdefault(r["u"], []).append(
                    {"u": r["u"], "g": r["g"], "p": r["p"], "o": str(r["o"])}
                )
            fed_cache.update(rows)

    # OLS: every OBO term (labels too: OBO ids are opaque), then any other term
    # still undescribed, namespace by namespace, if a sample shows OLS knows it.
    obo = [u for u in all_uris if u.startswith("http://purl.obolibrary.org/obo/")]
    ols_todo = [u for u in obo if u not in ols_cache]
    if ols_todo:
        print(f"  OLS: {len(ols_todo)} OBO term(s)")
        hits = await vt.ols_text(ols_todo, client)
        for u in ols_todo:
            ols_cache[u] = _hit_to_json(hits.get(u))

    def described(u: str) -> bool:
        voc = vocab_cache.get(u)
        rows = fed_cache.get(u) or []
        desc_preds = {*vs.DESCRIPTION_PREDICATES, *vt.EXTRA_DESCRIPTION_PREDICATES}
        return bool(
            (voc and voc.get("description")) or any(r["p"] in desc_preds for r in rows)
        )

    by_ns: dict[str, list[str]] = {}
    for u in all_uris:
        if u not in obo and not described(u):
            by_ns.setdefault(_namespace(u), []).append(u)
    for ns, uris in sorted(by_ns.items()):
        sample = uris[:OLS_SAMPLE]
        todo = [u for u in sample if u not in ols_cache]
        if todo:
            hits = await vt.ols_text(todo, client, log=lambda _m: None)
            for u in todo:
                ols_cache[u] = _hit_to_json(hits.get(u))
        if not any(ols_cache.get(u) for u in sample):
            continue
        rest = [u for u in uris[OLS_SAMPLE:] if u not in ols_cache]
        if rest:
            print(f"  OLS: {len(rest)} more term(s) in {ns}")
            hits = await vt.ols_text(rest, client)
            for u in rest:
                ols_cache[u] = _hit_to_json(hits.get(u))

    cache.update(vocab=vocab_cache, federation=fed_cache, ols=ols_cache)
    out: dict[str, dict[str, vt.TextHit]] = {}
    for kg, uris in needed.items():
        own = {u: vs.kg_iri(kg) for u in uris}
        fed = vt.pick_federation_hits(
            [row for u in uris for row in fed_cache.get(u) or []], own
        )
        per: dict[str, vt.TextHit] = {}
        for u in uris:
            voc = vocab_cache.get(u)
            ols = ols_cache.get(u)
            merged = _merge(
                vt.TextHit(**voc) if voc else None,
                fed.get(u),
                vt.TextHit(**ols) if ols else None,
            )
            if merged:
                per[u] = merged
        out[kg] = per
    return out


def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        return list(reader.fieldnames or []), list(reader)


def _write(path: Path, header: list[str], records: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=header, lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def _report(out: Path, reports: dict[str, vt.FillReport], cap: int = 40) -> None:
    unfilled_all: list[dict[str, str]] = []
    lines = [
        "# Label / description fill",
        "",
        "Generated by `scripts/fill_void_text.py`. Per row: curated proto-okn text, "
        "else the KG's own text already present, else another ontology or graph "
        "(tagged `(source: …)` in the description), else left empty. Counts are "
        "rows; a URI repeats once per source/target pair.",
        "",
        "| KG | rows | curated | existing | other ontology | unfilled "
        "| labels: curated / existing / ontology / local name |",
        "|---|---|---|---|---|---|---|",
    ]
    totals: Counter[str] = Counter()
    for kg, rep in sorted(reports.items()):
        s, lab = rep.sources, rep.labels
        rows = sum(s.values())
        totals.update(s)
        totals["rows"] += rows
        lines.append(
            f"| {kg} | {rows:,} | {s['curated']:,} | {s['existing']:,} | "
            f"{s['ontology']:,} | {s['unfilled']:,} | {lab['curated']:,} / "
            f"{lab['existing']:,} / {lab['ontology']:,} / {lab['local name']:,} |"
        )
        unfilled_all += [{"KG": kg, **u} for u in vt.dedupe_unfilled(rep.unfilled)]
    lines.append(
        f"| **total** | {totals['rows']:,} | {totals['curated']:,} | "
        f"{totals['existing']:,} | {totals['ontology']:,} | {totals['unfilled']:,} | |"
    )
    mismatches = [m for rep in reports.values() for m in rep.count_mismatches]
    if mismatches:
        lines += ["", "## Curated restriction counts that differ from the graph", ""]
        lines += [f"- {m}" for m in sorted(set(mismatches))]
    lines += [
        "",
        f"## Descriptions that could not be filled ({len(unfilled_all):,} entities)",
        "",
        "No curated text, no text in any federation graph, and none in the "
        "vocabulary or OLS. Full list: `unfilled_descriptions.csv`.",
    ]
    by_kg: dict[str, list[dict[str, str]]] = {}
    for u in unfilled_all:
        by_kg.setdefault(u["KG"], []).append(u)
    for kg, items in sorted(by_kg.items()):
        lines += ["", f"### {kg} ({len(items):,})", ""]
        ns = Counter(
            u["URI"].rsplit("#", 1)[0] + "#"
            if "#" in u["URI"]
            else u["URI"].rsplit("/", 1)[0] + "/"
            for u in items
        )
        lines.append(
            "By namespace: " + ", ".join(f"`{n}` {c}" for n, c in ns.most_common(6))
        )
        lines.append("")
        for u in items[:cap]:
            lines.append(f"- `{u['URI']}` ({u['Type']}) — {u['Label']}")
        if len(items) > cap:
            lines.append(f"- … {len(items) - cap:,} more")
    (out / "TEXT_FILL.md").write_text("\n".join(lines) + "\n")
    _write(
        out / "unfilled_descriptions.csv",
        ["KG", "URI", "Type", "EdgePropertyOf", "Label"],
        unfilled_all,
    )


async def fill_all(
    out: Path = OUT, kgs: list[str] | None = None, refresh: bool = False
) -> dict[str, vt.FillReport]:
    """Fill every (or the named) entity file in ``out``; write the report."""
    paths = sorted(out.glob(f"*{SUFFIX}"))
    if kgs:
        paths = [p for p in paths if p.name.removesuffix(SUFFIX) in kgs]
    cache_path = out / CACHE
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    files: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    indexes: dict[str, dict[tuple[str, ...], tuple[str, str]]] = {}
    needed: dict[str, set[str]] = {}
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        for path in paths:
            kg = path.name.removesuffix(SUFFIX)
            files[kg] = _read(path)
            curated = await vs.fetch_curated_csv(kg, client=client)
            indexes[kg] = vt.curated_index(curated) if curated else {}
            needed[kg] = vt.needs_lookup(files[kg][1], indexes[kg])
        print(f"lookups needed: {sum(map(len, needed.values())):,} (KG, URI) pairs")
        hits = await resolve(needed, cache, refresh, client)

    reports = {}
    for kg, (header, records) in files.items():
        reports[kg] = vt.fill_records(records, indexes[kg], hits.get(kg, {}))
        _write(out / f"{kg}{SUFFIX}", header, records)
    cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True) + "\n")
    if not kgs:
        _report(out, reports)
    total = Counter[str]()
    for rep in reports.values():
        total.update(rep.sources)
    print(f"filled {len(reports)} file(s): {dict(total)}")
    return reports


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--kg", action="append", default=[], help="KG shortname")
    parser.add_argument("--refresh", action="store_true", help="ignore the cache")
    parser.add_argument("--out", type=Path, default=OUT, help="entity file directory")
    args = parser.parse_args()
    await fill_all(args.out, args.kg or None, args.refresh)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
