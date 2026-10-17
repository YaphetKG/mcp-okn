"""Generate per-KG schema files from the ``okn-void`` VoID data, or the live graph.

Writes one ``<kg>_entities.csv`` per KG into ``metadata/void_entities/`` with the
columns ``URI, Label, Description, Type, EdgePropertyOf, SourceClass, TargetClass,
Triples, Pattern`` (see :mod:`mcp_okn.void_schema` for how each is derived; Pattern
is how a predicate is stored — direct / reified / axiom / declared).

VoID is used only when it describes the release being served: each KG's
``void:triples`` is checked against a live ``COUNT(*)`` first. When they differ by
more than ``void_schema.STALE_VOID_TOLERANCE`` the same statistics are counted from
the served graph instead (``schema_source: graph`` in ``build_notes.json``); once the
VoID is refreshed, the next build goes back to it. A KG whose graph is empty is not
written (and an old file for it is removed). Nothing is read from the legacy curated
``sbl-sdsc/mcp-proto-okn`` files.

``build_notes.json`` records per KG the freshness check, the schema source, build
notes, skips and failures. Afterwards ``fill_void_text.py`` fills Label/Description
in place (the repo's ``curated_text.csv`` first, then other ontologies tagged
``(source: …)``) and writes ``TEXT_FILL.md`` / ``unfilled_descriptions.csv``. Pass
``--no-fill`` to keep the raw text.

``get_schema`` reads these files by default; they ship with the server (see
:mod:`mcp_okn.schema`). Re-run ``scripts/check_payload_drift.py`` after a rebuild.

Usage:
    uv run python scripts/build_void_schema.py --kg spoke-genelab    # one KG (repeatable)
    uv run python scripts/build_void_schema.py --all                 # every VoID KG
    uv run python scripts/build_void_schema.py --freshness-only      # which KGs are stale
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
import time
from pathlib import Path
from typing import Any

import httpx

from mcp_okn import void_schema as vs
from mcp_okn.sparql import SparqlError

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "metadata" / "void_entities"
SUFFIX = "_entities.csv"

#: Above this many VoID edge partitions a KG's per-edge table is too large to commit
#: (wikidata has ~684K); skipped unless ``--include-large``.
MAX_EDGE_PARTITIONS = 100_000

NOTE_SECTIONS = (
    "skipped_large",
    "not_served",
    "failed",
    "notes",
    "timing_s",
    "freshness",
    "schema_source",
)


async def build(kgs: list[str], include_large: bool, out: Path) -> dict[str, Any]:
    """Build and write each KG's file. Returns the build notes."""
    notes: dict[str, Any] = {key: {} for key in NOTE_SECTIONS}
    sizes = await vs.fetch_edge_partition_counts()
    for kg in kgs:
        size = sizes.get(kg, 0)
        if size > MAX_EDGE_PARTITIONS and not include_large:
            print(f"{kg}: SKIPPED ({size:,} edge partitions; --include-large to build)")
            notes["skipped_large"][kg] = size
            continue
        path = out / f"{kg}{SUFFIX}"
        notes["freshness"][kg] = fresh = await vs.check_freshness(kg)
        if fresh["served_triples"] == 0:
            print(f"{kg}: NOT SERVED (empty graph); no file written")
            notes["not_served"][kg] = fresh.get("void_triples")
            path.unlink(missing_ok=True)
            continue
        source = "graph" if vs.void_is_stale(fresh) else "void"
        notes["schema_source"][kg] = source
        if source == "graph":
            print(
                f"{kg}: STALE VOID (void:triples {fresh['void_triples']:,} != served "
                f"{fresh['served_triples']:,}); counting the served graph"
            )
        print(f"{kg}: building from {source} ({size:,} VoID edge partitions)")
        start = time.monotonic()
        try:
            rows, kg_notes = await vs.build_kg_schema(kg, source=source)
        except (SparqlError, httpx.HTTPError) as exc:
            print(f"  FAILED: {str(exc)[:200]}")
            notes["failed"][kg] = str(exc)[:500]
            continue
        vs.write_csv(rows, path)
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            problems = vs.validate_rows(list(reader), list(reader.fieldnames or []))
        if problems:
            kg_notes.extend(f"validation: {p}" for p in problems[:20])
            print(f"  VALIDATION: {problems[:5]}")
        elapsed = round(time.monotonic() - start, 1)
        notes["timing_s"][kg] = elapsed
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
    for key in NOTE_SECTIONS:
        section = {k: v for k, v in old.get(key, {}).items() if k not in built}
        section.update(fresh.get(key, {}))
        merged[key] = dict(sorted(section.items()))
    path.write_text(json.dumps(merged, indent=2) + "\n")
    return merged


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--kg", action="append", default=[], help="KG shortname (repeatable)"
    )
    parser.add_argument("--all", action="store_true", help="build every KG with VoID")
    parser.add_argument(
        "--freshness-only",
        action="store_true",
        help="re-check VoID vs served triple counts for written files; build nothing",
    )
    parser.add_argument(
        "--include-large", action="store_true", help="also build huge KGs"
    )
    parser.add_argument("--out", type=Path, default=OUT, help="output directory")
    parser.add_argument(
        "--no-fill", action="store_true", help="skip the label/description fill"
    )
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    if args.freshness_only:
        path = args.out / "build_notes.json"
        notes = json.loads(path.read_text()) if path.exists() else {}
        kgs = args.kg or sorted(
            p.name.removesuffix(SUFFIX) for p in args.out.glob(f"*{SUFFIX}")
        )
        fresh: dict[str, Any] = {"freshness": {}}
        for kg in kgs:
            fresh["freshness"][kg] = f = await vs.check_freshness(kg)
            want = "graph" if vs.void_is_stale(f) else "void"
            have = notes.get("schema_source", {}).get(kg, "void")
            flag = "" if want == have else f"  <- rebuild (built from {have})"
            print(
                f"{kg}: void {f['void_triples']} served {f['served_triples']} "
                f"-> {want}{flag}"
            )
        _merge_notes(args.out, fresh, [])
        return 0

    if not args.kg and not args.all:
        parser.error("pass --kg NAME, --all, or --freshness-only")
    kgs = args.kg or await vs.list_void_kgs()
    fresh = await build(kgs, args.include_large, args.out)
    _merge_notes(args.out, fresh, kgs)
    if not args.no_fill:
        from fill_void_text import fill_all  # sibling script

        await fill_all(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
