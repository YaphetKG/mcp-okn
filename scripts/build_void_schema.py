"""Generate per-KG schema files from the ``okn-void`` VoID data and diff them.

Writes one ``<kg>_entities.csv`` per KG into ``metadata/void_entities/`` with the
columns ``URI, Label, Description, Type, EdgePropertyOf, SourceClass, TargetClass,
Triples`` (see :mod:`mcp_okn.void_schema` for how each is derived), then compares
every written file against the curated ``sbl-sdsc/mcp-proto-okn`` file of the same
KG and writes:

* ``COMPARISON.md``          — human-readable report (lists capped per section);
* ``comparison.json``        — the full, uncapped comparison;
* ``manual_definitions.csv`` — curated descriptions with no machine-accessible
  source (the hand-written knowledge the VoID files cannot reproduce);
* ``build_notes.json``       — per-KG build notes, skips and failures.

Nothing reads these files yet — this is an exploration of VoID as a schema source.

Usage:
    uv run python scripts/build_void_schema.py --kg spoke-genelab    # one KG (repeatable)
    uv run python scripts/build_void_schema.py --all                 # every VoID KG
    uv run python scripts/build_void_schema.py --compare-only        # re-diff written files
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import time
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from mcp_okn import registry
from mcp_okn import void_schema as vs
from mcp_okn.sparql import SparqlError

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "metadata" / "void_entities"
SUFFIX = "_entities.csv"

#: Above this many VoID edge partitions a KG's per-edge table is too large to commit
#: (wikidata has ~684K); skipped unless ``--include-large``.
MAX_EDGE_PARTITIONS = 100_000

#: Items shown per list in COMPARISON.md (comparison.json has them all).
CAP = 25


#: Prefixes used to shorten URIs in COMPARISON.md (the CSV/JSON keep full URIs).
#: ``kg:`` is the KG's own ``https://purl.org/okn/frink/kg/{kg}/`` namespace.
PREFIXES = {
    "rdf:": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs:": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd:": "http://www.w3.org/2001/XMLSchema#",
    "owl:": "http://www.w3.org/2002/07/owl#",
    "skos:": "http://www.w3.org/2004/02/skos/core#",
    "obo:": "http://purl.obolibrary.org/obo/",
    "biolink:": "https://w3id.org/biolink/vocab/",
    "schema:": "http://schema.org/",
    "dct:": "http://purl.org/dc/terms/",
}


def _curie(uri: str, kg: str) -> str:
    own = f"https://purl.org/okn/frink/kg/{kg}/"
    if uri.startswith(own):
        return "kg:" + uri.removeprefix(own)
    for prefix, ns in PREFIXES.items():
        if uri.startswith(ns):
            return prefix + uri.removeprefix(ns)
    return uri


def _fmt(item: Any, kg: str) -> str:
    if isinstance(item, (tuple, list)):
        return " → ".join(f"`{_curie(x, kg)}`" if x else "∅" for x in item)
    return f"`{_curie(item, kg)}`"


def _list(title: str, items: list[Any], kg: str) -> list[str]:
    if not items:
        return []
    lines = [f"**{title}** ({len(items)})", ""]
    lines += [f"- {_fmt(i, kg)}" for i in items[:CAP]]
    if len(items) > CAP:
        lines.append(f"- … {len(items) - CAP} more (see comparison.json)")
    return [*lines, ""]


async def build(kgs: list[str], include_large: bool, out: Path) -> dict[str, Any]:
    """Build and write each KG's file. Returns the build notes."""
    notes: dict[str, Any] = {
        "skipped_large": {},
        "failed": {},
        "notes": {},
        "timing_s": {},
        "freshness": {},
    }
    sizes = await vs.fetch_edge_partition_counts()
    for kg in kgs:
        size = sizes.get(kg, 0)
        if size > MAX_EDGE_PARTITIONS and not include_large:
            print(f"{kg}: SKIPPED ({size:,} edge partitions; --include-large to build)")
            notes["skipped_large"][kg] = size
            continue
        print(f"{kg}: building ({size:,} edge partitions)")
        start = time.monotonic()
        try:
            rows, kg_notes = await vs.build_kg_schema(kg)
        except (SparqlError, httpx.HTTPError) as exc:
            print(f"  FAILED: {str(exc)[:200]}")
            notes["failed"][kg] = str(exc)[:500]
            continue
        path = out / f"{kg}{SUFFIX}"
        vs.write_csv(rows, path)
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            problems = vs.validate_rows(list(reader), list(reader.fieldnames or []))
        if problems:
            kg_notes.extend(f"validation: {p}" for p in problems[:20])
            print(f"  VALIDATION: {problems[:5]}")
        elapsed = round(time.monotonic() - start, 1)
        notes["timing_s"][kg] = elapsed
        notes["freshness"][kg] = fresh = await vs.check_freshness(kg)
        if fresh["matches"] is False:
            print(
                f"  STALE VOID: void:triples {fresh['void_triples']:,} != served "
                f"{fresh['served_triples']:,}"
            )
        if kg_notes:
            notes["notes"][kg] = kg_notes
        n_cls = sum(r.type == "Class" for r in rows)
        print(f"  {n_cls} classes, {len(rows) - n_cls} predicate rows, {elapsed}s")
    return notes


def _merge_notes(out: Path, fresh: dict[str, Any], built: list[str]) -> dict[str, Any]:
    """Fold this run's notes into build_notes.json, replacing the KGs just processed."""
    path = out / "build_notes.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    merged: dict[str, Any] = {}
    for key in ("skipped_large", "failed", "notes", "timing_s", "freshness"):
        section = {k: v for k, v in old.get(key, {}).items() if k not in built}
        section.update(fresh.get(key, {}))
        merged[key] = dict(sorted(section.items()))
    path.write_text(json.dumps(merged, indent=2) + "\n")
    return merged


async def compare(out: Path, notes: dict[str, Any]) -> None:
    """Diff every written file against its curated counterpart and write the reports."""
    files = sorted(out.glob(f"*{SUFFIX}"))
    servable = {k["shortname"] for k in registry.load_snapshot()}
    results: dict[str, Any] = {}
    no_curated: list[str] = []
    manual: list[list[str]] = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for path in files:
            kg = path.name.removesuffix(SUFFIX)
            curated = await vs.fetch_curated_csv(kg, client)
            if curated is None:
                no_curated.append(kg)
                continue
            result = vs.compare_with_curated(vs.read_csv(path), curated)
            results[kg] = result
            manual.extend(vs.manual_definitions(kg, result["text"]))
        built = {p.name.removesuffix(SUFFIX) for p in files}
        curated_without_void = []
        for kg in sorted(servable - built - set(notes.get("skipped_large", {}))):
            if await vs.fetch_curated_csv(kg, client) is not None:
                curated_without_void.append(kg)

    (out / "comparison.json").write_text(
        json.dumps(
            {
                "kgs": results,
                "no_curated_file": no_curated,
                "curated_without_void_file": curated_without_void,
            },
            indent=2,
            default=list,
        )
        + "\n"
    )
    with (out / "manual_definitions.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(vs.MANUAL_COLUMNS)
        writer.writerows(manual)
    (out / "COMPARISON.md").write_text(
        _report(
            results, no_curated, curated_without_void, notes, len(manual), len(files)
        )
    )
    print(
        f"compared {len(results)} KG(s); {len(manual)} manual definitions; wrote {out}"
    )


def _report(
    results: dict[str, Any],
    no_curated: list[str],
    curated_without_void: list[str],
    notes: dict[str, Any],
    n_manual: int,
    n_files: int,
) -> str:
    desc_keys = ["match", "differs", "curated-only", "machine-only", vs.NOT_IN_VOID]
    lines = [
        "# VoID-derived schemas vs curated proto-okn schemas",
        "",
        f"Generated {date.today().isoformat()} by `scripts/build_void_schema.py`. "
        f"{n_files} VoID-derived file(s) in this directory; {len(results)} have a curated "
        "counterpart in `sbl-sdsc/mcp-proto-okn/metadata/entities/`.",
        "",
        "How to read this:",
        "",
        "- Curated files are normalized before comparing: Source/TargetClass labels → "
        "class URIs (via the file's own Class rows), EdgePropertyOf short names → "
        "predicate URIs, `EdgeProperty`/`NodeProperty` → `Predicate`.",
        "- **only VoID**: in the served graph but missing from the curated file. "
        "**only curated**: in the curated file but not in the served graph (phantom, "
        "renamed, or not yet deployed).",
        "- **Edges only curated** over-reports: a curated predicate row holds "
        "`|`-joined source and target lists with no pairing, so it is expanded as "
        "every source × target combination, some of which the curators never meant "
        "(e.g. oard-kg `subject`). Use it to find candidates, not as a list of errors; "
        "VoID's per-edge rows give the real pairings with counts.",
        "- Description status per curated row: `match` (same text as the KG/ubergraph), "
        "`differs`, `curated-only` (entity is served but no machine source describes "
        f"it — hand-written), `machine-only`, `{vs.NOT_IN_VOID}` (entity not served).",
        f"- `manual_definitions.csv` holds the {n_manual} `curated-only` / "
        f"`{vs.NOT_IN_VOID}` descriptions — the knowledge VoID cannot reproduce.",
        "- Class counts in the VoID files are instance counts (`void:entities`); "
        "predicate counts are triples per (source class, predicate, target) edge.",
        "- URIs below are shortened: `kg:` = the KG's own "
        "`https://purl.org/okn/frink/kg/{kg}/` namespace; "
        + ", ".join(f"`{p}` = `{ns}`" for p, ns in PREFIXES.items())
        + ". `comparison.json` has full URIs and uncapped lists.",
        "",
        "## Coverage",
        "",
    ]
    if notes.get("skipped_large"):
        lines.append(
            "- Skipped as too large: "
            + ", ".join(
                f"`{k}` ({v:,} edges)" for k, v in notes["skipped_large"].items()
            )
        )
    if notes.get("failed"):
        lines.append("- Build failed: " + ", ".join(f"`{k}`" for k in notes["failed"]))
    if no_curated:
        lines.append(
            "- VoID file but no curated file: "
            + ", ".join(f"`{k}`" for k in no_curated)
        )
    if curated_without_void:
        lines.append(
            "- Curated file but no VoID file: "
            + ", ".join(f"`{k}`" for k in curated_without_void)
        )
    freshness = notes.get("freshness", {})
    stale = {k: f for k, f in freshness.items() if f.get("matches") is False}
    unknown = sorted(k for k, f in freshness.items() if f.get("matches") is None)
    lines += [
        "",
        "## VoID freshness",
        "",
        "VoID is only trustworthy for a KG when it describes the graph actually served. "
        "Each KG's `void:triples` is compared with a live `COUNT(*)` of its named graph.",
        "",
        f"- Checked: {len(freshness)}; match: "
        f"{sum(f.get('matches') is True for f in freshness.values())}; "
        f"**stale: {len(stale)}**; unknown (count timed out): {len(unknown)}",
    ]
    if unknown:
        lines.append("- Unknown: " + ", ".join(f"`{k}`" for k in unknown))
    if stale:
        lines += [
            "",
            "| KG | VoID version | VoID updated | void:triples | served triples |",
            "|---|---|---|---|---|",
        ]
        for k, f in stale.items():
            lines.append(
                f"| {k} | {f.get('version')} | {f.get('last_updated')} | "
                f"{f['void_triples']:,} | {f['served_triples']:,} |"
            )
        lines += [
            "",
            "Treat the structural diff for a stale KG with suspicion: VoID may describe "
            "a different release than the curated file and the served graph.",
        ]
    lines += [
        "",
        "## Summary",
        "",
        "| KG | classes VoID / cur | only VoID | only cur | predicates VoID / cur | "
        "only VoID | only cur | edge props VoID / cur | "
        + " | ".join(f"desc {k}" for k in desc_keys)
        + " |",
        "|---|---|---|---|---|---|---|---|" + "---|" * len(desc_keys),
    ]
    for kg, r in results.items():
        c, p, e, d = (
            r["classes"],
            r["predicates"],
            r["edge_properties"],
            r["description_status"],
        )
        lines.append(
            f"| {kg}{' ⚠ stale' if kg in stale else ''} | {c['new']} / {c['curated']} | {len(c['only_new'])} | "
            f"{len(c['only_curated'])} | {p['new']} / {p['curated']} | {len(p['only_new'])} | "
            f"{len(p['only_curated'])} | {e['new']} / {e['curated']} | "
            + " | ".join(str(d.get(k, 0)) for k in desc_keys)
            + " |"
        )
    lines.append("")
    for kg, r in results.items():
        lines += [f"## {kg}", ""]
        lines.append(f"Curated row types: {r['curated_types']}")
        lines.append("")
        lines += _list("Classes only in VoID", r["classes"]["only_new"], kg)
        lines += _list("Classes only curated", r["classes"]["only_curated"], kg)
        lines += _list("Predicates only in VoID", r["predicates"]["only_new"], kg)
        lines += _list("Predicates only curated", r["predicates"]["only_curated"], kg)
        lines += _list(
            "(source class, predicate) only in VoID",
            r["source_predicate_pairs"]["only_new"],
            kg,
        )
        lines += _list(
            "(source class, predicate) only curated",
            r["source_predicate_pairs"]["only_curated"],
            kg,
        )
        lines += _list("Edges only in VoID", r["edges"]["only_new"], kg)
        lines += _list("Edges only curated", r["edges"]["only_curated"], kg)
        lines += _list(
            "Edge properties (predicate, property) only in VoID",
            r["edge_properties"]["only_new"],
            kg,
        )
        lines += _list(
            "Edge properties (predicate, property) only curated",
            r["edge_properties"]["only_curated"],
            kg,
        )
        lines += _list(
            "Curated class labels that resolve to no URI",
            r["unresolved_curated_labels"],
            kg,
        )
        differs = [t for t in r["text"] if t["description_status"] == "differs"]
        if differs:
            lines += [f"**Descriptions that differ** ({len(differs)})", ""]
            for t in differs[:10]:
                lines.append(
                    f"- `{_curie(t['uri'], kg)}`<br>curated: {t['curated_description'][:200]}"
                    f"<br>KG: {t['new_description'][:200]}"
                )
            if len(differs) > 10:
                lines.append(f"- … {len(differs) - 10} more (see comparison.json)")
            lines.append("")
        lines += _list("Build notes", notes.get("notes", {}).get(kg, []), kg)
    return "\n".join(lines).rstrip() + "\n"


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--kg", action="append", default=[], help="KG shortname (repeatable)"
    )
    parser.add_argument("--all", action="store_true", help="build every KG with VoID")
    parser.add_argument(
        "--compare-only", action="store_true", help="only re-run the diff"
    )
    parser.add_argument(
        "--freshness-only",
        action="store_true",
        help="re-check VoID vs served triple counts for written files, then re-diff",
    )
    parser.add_argument(
        "--include-large", action="store_true", help="also build huge KGs"
    )
    parser.add_argument("--out", type=Path, default=OUT, help="output directory")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.compare_only or args.freshness_only:
        path = args.out / "build_notes.json"
        notes = json.loads(path.read_text()) if path.exists() else {}
        if args.freshness_only:
            kgs = args.kg or sorted(
                p.name.removesuffix(SUFFIX) for p in args.out.glob(f"*{SUFFIX}")
            )
            fresh: dict[str, Any] = {"freshness": {}}
            for kg in kgs:
                fresh["freshness"][kg] = f = await vs.check_freshness(kg)
                print(f"{kg}: void {f['void_triples']} served {f['served_triples']}")
            notes = _merge_notes(args.out, fresh, [])
    else:
        if not args.kg and not args.all:
            parser.error("pass --kg NAME, --all, or --compare-only")
        kgs = args.kg or await vs.list_void_kgs()
        fresh = await build(kgs, args.include_large, args.out)
        notes = _merge_notes(args.out, fresh, kgs)
    await compare(args.out, notes)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
