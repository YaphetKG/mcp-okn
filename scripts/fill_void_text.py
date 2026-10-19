"""Fill Label/Description in metadata/void_entities/*_entities.csv (see mcp_okn.void_text).

Order per row: the KG's own ontology release where it supersedes the curated files
(``RELEASES``: ContaminOSO for the SAWGraph graphs), else the curated text in
``curated_text.csv``, else the text already there (the KG's own, or ubergraph's), else another
ontology — for the SAWGraph graphs their project's other modules
(``SAWGRAPH_MODULES``), then the vocabulary's own published
document, the federation graph that defines the term, OLS, or for SUDOKN's NAICS
industry classes the U.S. Census Bureau's NAICS definitions — tagged
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
import io
import json
import re
import xml.etree.ElementTree as ET
import zipfile
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
#: Hand-written labels and descriptions, owned here (see :mod:`mcp_okn.void_text`).
CURATED_TEXT = "curated_text.csv"

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
    # Industrial Ontologies Foundry (SUDOKN builds on these; okn-registry: sudokn).
    # Pinned to Release_202401: later releases moved the annotation vocabulary to
    # …/ontology/annotation/, so the IRIs SUDOKN uses are no longer described.
    "https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/": (
        "IOF Annotation Vocabulary, Release 202401",
        [
            "https://raw.githubusercontent.com/iofoundry/ontology/Release_202401/"
            "core/meta/AnnotationVocabulary.rdf"
        ],
    ),
    "https://spec.industrialontologies.org/ontology/core/Core/": (
        "IOF Core, Release 202401",
        [
            "https://raw.githubusercontent.com/iofoundry/ontology/Release_202401/"
            "core/Core.rdf"
        ],
    ),
    "https://spec.industrialontologies.org/ontology/supplychain/SupplyChain/": (
        "IOF Supply Chain",
        ["https://spec.industrialontologies.org/ontology/supplychain/SupplyChain/"],
    ),
    "http://semanticscience.org/resource/": (
        "SIO",
        ["http://semanticscience.org/ontology/sio.owl"],
    ),
}

#: Ontology releases that supersede the curated text for their terms, in
#: the KGs built on them: namespace → (name, KGs, module documents). The modules
#: are read together, since an extension defines terms the core lacks.
#: ContaminOSO v1 (core modified 2026-04-20): the core changes DetectQuantityValue
#: ("Quantified Detect Quantity Value"); the DSSTox extension defines
#: ofDSSToxSubstance / ofDatasetSubstance; the material-sample extension gives
#: the sample classes labels but no descriptions, so their curated text stays.
_COSO = "https://raw.githubusercontent.com/SAWGraph/contaminoso/refs/heads/main/v1/"
RELEASES: dict[str, tuple[str, frozenset[str], list[str]]] = {
    "http://w3id.org/coso/v1/contaminoso#": (
        "ContaminOSO v1",
        frozenset({"sawgraph", "fiokg", "hydrologykg", "spatialkg"}),
        [
            _COSO + "contaminoso_core.ttl",
            _COSO + "contaminoso_dsstox_ext.ttl",
            _COSO + "contaminoso_materialSample_ext.ttl",
        ],
    ),
}

#: The SAWGraph project's other ontology modules, one repo each, tried in order to
#: fill descriptions nothing else supplies (tagged ``(source: …)``). They do NOT
#: supersede curated text: checked 2026-10-16, they agree with it except where
#: theirs is worse — a citation instead of a definition (wqp TaxonGroup.FishNekton),
#: typos ("regoins"), or machine labels (``hasCASRN``, ``(kwg) sfContains``).
#: water-kg's us-sdwis-schema.ttl parses since its 2026-05-21 revision declared
#: dcterms:, but (checked 2026-10-18) describes only PublicWaterSystem.
#: STAD v2 core (the lab's statistical-data ontology) names its terms ``…/core#X``;
#: the SAWGraph graphs use ``…/core/X``, so :data:`MODULE_ALIASES` maps them.
_SAW = "https://raw.githubusercontent.com/SAWGraph/{}/refs/heads/main/{}"
SAWGRAPH_MODULES: tuple[frozenset[str], list[tuple[str, list[str]]]] = (
    frozenset({"sawgraph", "fiokg", "hydrologykg", "spatialkg"}),
    [
        (
            "SAWGraph FIO",
            [
                _SAW.format("fio", p)
                for p in (
                    "ontology/fio.ttl",
                    "datasets/federal/us-frs/ontology/epa-frs.ttl",
                    "datasets/federal/us-frs/ontology/epa-frs-controlledVocab.ttl",
                    "datasets/federal/us-frs/ontology/epa-frs-recordTypes.ttl",
                )
            ],
        ),
        (
            "SAWGraph water ontology",
            [
                _SAW.format("water-kg", p)
                for p in (
                    "ontologies/sawgraph-water-ontology.ttl",
                    "ontologies/reused-imported/hyf.ttl",
                    "datasets/sdwis/us-sdwis-schema.ttl",
                )
            ],
        ),
        (
            "SAWGraph spatial ontology",
            [_SAW.format("geospatial-kg", "ontologies/sawgraph-spatial-ontology.ttl")],
        ),
        (
            "SAWGraph PFAS KG schemas",
            [
                _SAW.format("pfas-kg", p)
                for p in (
                    "datasets/federal/us-wqp/ontology/wqp_schema.ttl",
                    "datasets/maine/egad/ontology/egad-sites-samples-schema.ttl",
                )
            ],
        ),
        (
            "SAWGraph DSSTox ontology V3",
            [_SAW.format("comptox-ontology", "V3/DSSToxOntology_PFAS_as_instance.ttl")],
        ),
        ("STAD v2 core", ["https://theskailab.github.io/STAD/core/ontology.ttl"]),
    ],
)

#: Namespace the graphs use → namespace a module document defines the terms in.
MODULE_ALIASES = {
    "http://purl.org/spatialai/stad/v2/core/": "http://purl.org/spatialai/stad/v2/core#",
}

#: Census Bureau NAICS definitions, newest first. SUDOKN uses NAICS 2022 (16 of its
#: codes exist only there, none only in 2017); 11 SUDOKN codes were dropped in 2017
#: and need the 2012 definitions, which Census publishes only behind a search page
#: that refuses scripted requests, so those stay unfilled.
CENSUS_NAICS = {
    "2022": "https://www.census.gov/naics/2022NAICS/2022_NAICS_Descriptions.xlsx",
    "2017": "https://www.census.gov/naics/2017NAICS/2017_NAICS_Descriptions.xlsx",
}

#: Vocabulary-specific description predicates: LinkML describes its own terms with
#: linkml:description and PROV-O with prov:definition, not rdfs:comment.
VOCAB_DESCRIPTION_PREDICATES = (
    "https://w3id.org/linkml/description",
    "http://www.w3.org/ns/prov#definition",
)

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
    name, urls = VOCABS[namespace]
    graph = None
    for url in urls:
        graph = await _parse_doc(url, name, client)
        if graph is not None:
            break
    return {} if graph is None else _graph_text(graph, uris, name)


async def release_text(
    namespace: str, uris: list[str], client: httpx.AsyncClient
) -> dict[str, vt.TextHit]:
    """Text for ``uris`` from every module document of an ontology release."""

    name, _kgs, urls = RELEASES[namespace]
    return await module_text(name, urls, uris, client) or {}


async def module_text(
    name: str, urls: list[str], uris: list[str], client: httpx.AsyncClient
) -> dict[str, vt.TextHit] | None:
    """Text for ``uris`` from module documents read together; None if any fails."""
    import rdflib

    graph = rdflib.Graph()
    for url in urls:
        module = await _parse_doc(url, name, client)
        if module is None:
            return None  # a partial release would silently fall back to other text
        graph += module
    return _graph_text(graph, uris, name)


async def _parse_doc(url: str, name: str, client: httpx.AsyncClient) -> Any:
    """One RDF document parsed with rdflib, or None if it cannot be fetched or read."""
    import rdflib  # transitive dependency (sparql-to-mermaid); only this script uses it

    try:
        resp = await client.get(url, headers={"Accept": _ACCEPT})
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "").split(";")[0].strip()
        fmt = _FORMATS.get(ctype) or ("turtle" if url.endswith(".ttl") else "xml")
        graph = rdflib.Graph()
        graph.parse(data=resp.content, format=fmt)
        return graph
    except Exception as exc:  # any fetch or parse failure
        print(f"  {name}: {url} unusable ({type(exc).__name__})")
        return None


def _graph_text(graph: Any, uris: list[str], name: str) -> dict[str, vt.TextHit]:
    """The English label and description of each of ``uris`` in ``graph``."""
    import rdflib

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

    def first(subject: Any, preds: list[Any]) -> str:
        for p in preds:
            vals = sorted(
                vs._clean(str(o))
                for o in graph.objects(subject, p)
                if isinstance(o, rdflib.Literal)
                and (o.language is None or o.language.lower().split("-")[0] == "en")
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


_XLSX = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_xlsx_rows(data: bytes) -> list[dict[str, str]]:
    """The first sheet of an .xlsx as ``{column letter: text}`` rows (stdlib only)."""
    book = zipfile.ZipFile(io.BytesIO(data))
    shared: list[str] = []
    if "xl/sharedStrings.xml" in book.namelist():
        for si in ET.fromstring(book.read("xl/sharedStrings.xml")).iter(f"{_XLSX}si"):
            shared.append("".join(t.text or "" for t in si.iter(f"{_XLSX}t")))
    rows = []
    for row in ET.fromstring(book.read("xl/worksheets/sheet1.xml")).iter(f"{_XLSX}row"):
        cells = {}
        for c in row.iter(f"{_XLSX}c"):
            col = re.match(r"[A-Z]+", c.get("r", "")).group(0)  # type: ignore[union-attr]
            v = c.find(f"{_XLSX}v")
            if c.get("t") == "s" and v is not None and v.text:
                cells[col] = shared[int(v.text)]
            elif c.get("t") == "inlineStr":
                cells[col] = "".join(t.text or "" for t in c.iter(f"{_XLSX}t"))
            else:
                cells[col] = v.text if v is not None and v.text else ""
        rows.append(cells)
    return rows


async def census_naics_text(
    uris: list[str], client: httpx.AsyncClient
) -> dict[str, vt.TextHit]:
    """Census definitions for SUDOKN NAICS IRIs, from the newest edition that has them."""
    editions: dict[str, dict[str, tuple[str, str]]] = {}
    for edition, url in CENSUS_NAICS.items():
        resp = await client.get(url)
        if resp.status_code != 200:
            print(f"  Census NAICS {edition}: HTTP {resp.status_code}")
            continue
        rows = read_xlsx_rows(resp.content)
        editions[edition] = {
            re.sub(r"\.0$", "", r.get("A", "").strip()): (
                r.get("B", ""),
                r.get("C", ""),
            )
            for r in rows[1:]
        }
    out = {}
    for u in uris:
        code = vt.naics_code(u)
        for edition, table in editions.items():
            if code and code in table:
                out[u] = vt.naics_hit(code, *table[code], edition)
                break
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
                    vt.federation_text_query(batch),
                    client=None,
                    timeout=300,
                    normalize_schema=False,  # keep the data's https schema.org IRIs
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

    naics_cache = {} if refresh else cache.setdefault("census_naics", {})
    naics_todo = [u for u in all_uris if vt.naics_code(u) and u not in naics_cache]
    if naics_todo:
        print(f"  Census NAICS: {len(naics_todo)} code(s)")
        hits = await census_naics_text(naics_todo, client)
        for u in naics_todo:
            naics_cache[u] = _hit_to_json(hits.get(u))

    cache.update(
        vocab=vocab_cache, federation=fed_cache, ols=ols_cache, census_naics=naics_cache
    )
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
            naics = naics_cache.get(u)
            merged = _merge(
                vt.TextHit(**voc) if voc else None,
                fed.get(u),
                vt.TextHit(**ols) if ols else None,
                vt.TextHit(**naics) if naics else None,
            )
            if merged:
                per[u] = merged
        out[kg] = per
    return out


async def resolve_releases(
    files: dict[str, tuple[list[str], list[dict[str, str]]]],
    cache: dict[str, Any],
    refresh: bool,
    client: httpx.AsyncClient,
) -> dict[str, dict[str, vt.TextHit]]:
    """Per KG, ``{uri: TextHit}`` from the ontology releases in :data:`RELEASES`."""
    release_cache = {} if refresh else cache.setdefault("release", {})
    out: dict[str, dict[str, vt.TextHit]] = {}
    for ns, (name, kgs, _urls) in sorted(RELEASES.items()):
        used = {
            kg: {r["URI"] for r in records if r["URI"].startswith(ns)}
            for kg, (_header, records) in files.items()
            if kg in kgs
        }
        todo = sorted({u for us in used.values() for u in us} - set(release_cache))
        if todo:
            print(f"  release {name}: {len(todo)} term(s)")
            hits = await release_text(ns, todo, client)
            if not hits:
                print(f"  release {name}: unavailable, curated text kept")
                continue  # don't cache a failed fetch as "no text"
            for u in todo:
                release_cache[u] = _hit_to_json(hits.get(u))
        for kg, us in used.items():
            out.setdefault(kg, {}).update(
                {u: vt.TextHit(**release_cache[u]) for u in us if release_cache.get(u)}
            )
    cache["release"] = release_cache
    return out


async def resolve_modules(
    needed: dict[str, set[str]],
    cache: dict[str, Any],
    refresh: bool,
    client: httpx.AsyncClient,
) -> dict[str, dict[str, vt.TextHit]]:
    """Per KG, gap-filling text from :data:`SAWGRAPH_MODULES` (first module wins)."""
    kgs, modules = SAWGRAPH_MODULES
    module_cache = {} if refresh else cache.setdefault("sawgraph_modules", {})
    uris = sorted({u for kg, us in needed.items() if kg in kgs for u in us})
    todo = [u for u in uris if u not in module_cache]
    if todo:
        found: dict[str, vt.TextHit] = {}
        alias = {_alias(u): u for u in todo if _alias(u) != u}
        for name, urls in modules:
            print(f"  {name}: {len(todo)} term(s)")
            hits = await module_text(name, urls, [*todo, *alias], client)
            if hits is None:
                print(f"  {name}: unavailable, not cached")
                todo = []  # retry everything next run rather than cache gaps
                break
            for u, h in sorted(hits.items(), key=lambda kv: kv[0] in alias):
                u = alias.get(u, u)
                # Descriptions only: their labels for reused terms are prefixed
                # names (qudt:Quantity, hyf:realizedCatchment), not real labels.
                if h.description:
                    found.setdefault(u, vt.TextHit("", h.description, h.source))
        for u in todo:
            module_cache[u] = _hit_to_json(found.get(u))
    cache["sawgraph_modules"] = module_cache
    return {
        kg: {u: vt.TextHit(**module_cache[u]) for u in us if module_cache.get(u)}
        for kg, us in needed.items()
        if kg in kgs
    }


def _alias(uri: str) -> str:
    """``uri`` in the namespace a module document defines it in (:data:`MODULE_ALIASES`)."""
    ns = next((n for n in MODULE_ALIASES if uri.startswith(n)), None)
    return uri if ns is None else MODULE_ALIASES[ns] + uri[len(ns) :]


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
        "Generated by `scripts/fill_void_text.py`. Per row: the KG's own ontology "
        "release where one supersedes the curated text (ContaminOSO v1 for the "
        "SAWGraph graphs), else the curated text in `curated_text.csv`, "
        "else the KG's own text already present, else another ontology or graph "
        "(tagged `(source: …)` in the description), else left empty. Counts are "
        "rows; a URI repeats once per source/target pair.",
        "",
        "| KG | rows | release | curated | existing | other ontology | unfilled "
        "| labels: release / curated / existing / ontology / local name |",
        "|---|---|---|---|---|---|---|---|",
    ]
    totals: Counter[str] = Counter()
    for kg, rep in sorted(reports.items()):
        s, lab = rep.sources, rep.labels
        rows = sum(s.values())
        totals.update(s)
        totals["rows"] += rows
        lines.append(
            f"| {kg} | {rows:,} | {s['release']:,} | {s['curated']:,} | "
            f"{s['existing']:,} | "
            f"{s['ontology']:,} | {s['unfilled']:,} | {lab['release']:,} / "
            f"{lab['curated']:,} / "
            f"{lab['existing']:,} / {lab['ontology']:,} / {lab['local name']:,} |"
        )
        unfilled_all += [{"KG": kg, **u} for u in vt.dedupe_unfilled(rep.unfilled)]
    lines.append(
        f"| **total** | {totals['rows']:,} | {totals['release']:,} | "
        f"{totals['curated']:,} | "
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

    curated = vt.read_curated_text(out / CURATED_TEXT)
    files: dict[str, tuple[list[str], list[dict[str, str]]]] = {}
    indexes: dict[str, dict[tuple[str, ...], tuple[str, str]]] = {}
    needed: dict[str, set[str]] = {}
    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        for path in paths:
            kg = path.name.removesuffix(SUFFIX)
            files[kg] = _read(path)
            indexes[kg] = vt.curated_index(curated.get(kg, []))
            needed[kg] = vt.needs_lookup(files[kg][1], indexes[kg])
        print(f"lookups needed: {sum(map(len, needed.values())):,} (KG, URI) pairs")
        hits = await resolve(needed, cache, refresh, client)
        releases = await resolve_releases(files, cache, refresh, client)
        modules = await resolve_modules(needed, cache, refresh, client)
    for kg, per in modules.items():
        # The KG's own project ontologies come before generic vocabularies and OLS.
        for u, hit in per.items():
            merged = _merge(hit, hits.get(kg, {}).get(u))
            if merged:
                hits.setdefault(kg, {})[u] = merged

    reports = {}
    for kg, (header, records) in files.items():
        reports[kg] = vt.fill_records(
            records, indexes[kg], hits.get(kg, {}), releases.get(kg)
        )
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
