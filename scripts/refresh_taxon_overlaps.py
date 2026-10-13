"""Materialize the pairwise NCBITaxon overlap counts for the taxon-hub members.

The taxonomy crosswalks are a HUB: each member KG maps organisms to ubergraph, so a
pairwise overlap between two members is COMPOSED from their two hub spokes and is
two-valued (exact NCBITaxon id vs directional clade membership via subClassOf*).
This script runs those skeletons (from ``mcp_okn.taxon``) LIVE against the OKN
federation for every unordered pair of ``TAXON_HUB_KGS`` and materializes the
non-zero results into ``metadata/crosswalks.json`` ``taxon_hub.pairwise`` — the
counts ``list_crosswalks`` then surfaces inline. Re-run it whenever a member KG is
updated.

    uv run python scripts/refresh_taxon_overlaps.py             # dry run, print table
    uv run python scripts/refresh_taxon_overlaps.py --inject    # write counts back
    uv run python scripts/refresh_taxon_overlaps.py --pair spoke-okn nde
    uv run python scripts/refresh_taxon_overlaps.py --pair spoke-okn nde --inject

After ``--inject``, run ``scripts/refresh_snapshot.py`` to sync the bundled copy.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import date
from itertools import combinations
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from mcp_okn import taxon
from mcp_okn.sparql import run_sparql

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "metadata" / "crosswalks.json"

# Composed taxonomy joins fan out over ubergraph's full subClassOf* closure, so
# allow more headroom than the simple-skeleton verifier.
TIMEOUT = 180.0


async def _count(query: str, client: httpx.AsyncClient) -> int | None:
    """Run a COUNT skeleton; return the integer, or None on error/timeout."""
    try:
        r = await run_sparql(query, timeout=TIMEOUT, client=client)
    except Exception as exc:
        print(f"      ERR {str(exc)[:120]}")
        return None
    rows = r.get("rows") or []
    if not rows:
        return 0
    return int(rows[0]["shared"])


async def measure_pair(
    kg_a: str, kg_b: str, client: httpx.AsyncClient
) -> dict[str, int | None]:
    """Exact-id + both-direction clade counts for the sorted pair ``(kg_a, kg_b)``.

    ``clade_a_in_b`` counts kg_a's taxa nested under kg_b's clades (build the clade
    skeleton with kg_b as the clade root), and ``clade_b_in_a`` the reverse.
    """
    exact_id = await _count(taxon.build_exact_skeleton(kg_a, kg_b), client)
    clade_a_in_b = await _count(taxon.build_clade_skeleton(kg_b, kg_a), client)
    clade_b_in_a = await _count(taxon.build_clade_skeleton(kg_a, kg_b), client)
    return {
        "kg_a": kg_a,
        "kg_b": kg_b,
        "exact_id": exact_id,
        "clade_a_in_b": clade_a_in_b,
        "clade_b_in_a": clade_b_in_a,
    }


_COUNTS = ("exact_id", "clade_a_in_b", "clade_b_in_a")


def _fully_measured(rec: dict[str, int | None]) -> bool:
    """True only when ALL three counts came back as integers (no error/timeout)."""
    return all(isinstance(rec.get(k), int) for k in _COUNTS)


def _is_nonzero(rec: dict[str, int | None]) -> bool:
    """True when at least one measured count is a positive integer."""
    return any(isinstance(rec.get(k), int) and rec[k] > 0 for k in _COUNTS)


def inject(records: list[dict[str, int | None]]) -> None:
    """Merge fully-measured pairs into ``metadata/crosswalks.json``
    ``taxon_hub.pairwise``.

    A non-zero pair has its three COUNTS updated in place: every other field on the
    stored row — the curated ``science_question`` and ``note`` above all — is kept,
    and so is the row's position, so a refresh diffs as a change of numbers and
    nothing else. (This used to rebuild the row from the counts alone, which
    silently deleted that prose and re-sorted the table.) A pair seen for the first
    time is appended. A pair that measured all-zero is dropped, row and prose
    together, so a KG update that removes an overlap is reflected. A pair where any
    skeleton errored/timed out is LEFT UNTOUCHED (the table never stores a null
    count) and a warning is printed — re-run it with ``--pair``. Rows for pairs not
    measured in this run stay exactly as they were, so ``--pair`` refreshes
    incrementally. ``verified_on`` is stamped to today.

    Prose cannot be re-measured, so the run ends by naming the rows that need a
    human read: those whose counts moved under an existing note or question, those
    appended without a question, and those dropped.
    """
    data = json.loads(SRC.read_text(encoding="utf-8"))
    hub = data.setdefault("taxon_hub", {})
    pairwise: list[dict] = list(hub.get("pairwise", []))
    index = {frozenset((r["kg_a"], r["kg_b"])): i for i, r in enumerate(pairwise)}
    skipped: list[tuple[str, str]] = []
    added: list[tuple[str, str]] = []
    moved: list[tuple[str, str]] = []
    dropped: list[tuple[str, str]] = []
    drop_at: set[int] = set()
    for rec in records:
        pair = (rec["kg_a"], rec["kg_b"])
        if not _fully_measured(rec):
            skipped.append(pair)
            continue
        counts = {k: rec[k] for k in _COUNTS}
        at = index.get(frozenset(pair))
        if not _is_nonzero(rec):
            if at is not None:
                drop_at.add(at)
                dropped.append(pair)
            continue
        if at is None:
            index[frozenset(pair)] = len(pairwise)
            pairwise.append({"kg_a": pair[0], "kg_b": pair[1], **counts})
            added.append(pair)
            continue
        old = pairwise[at]
        if any(old.get(k) != counts[k] for k in _COUNTS) and (
            old.get("note") or old.get("science_question")
        ):
            moved.append(pair)
        # The counts are directional and oriented to rec's kg_a/kg_b, so restate
        # the pair alongside them rather than trust the stored orientation.
        pairwise[at] = {**old, "kg_a": pair[0], "kg_b": pair[1], **counts}
    hub["pairwise"] = [r for i, r in enumerate(pairwise) if i not in drop_at]
    hub["verified_on"] = date.today().isoformat()
    SRC.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(
        f"\ninjected {len(records) - len(skipped)} fully-measured pair(s); "
        f"{len(hub['pairwise'])} non-zero pair(s) now in {SRC}.\n"
        "Run scripts/refresh_snapshot.py to sync the bundled copy."
    )
    if skipped:
        print(f"SKIPPED (a skeleton errored/timed out, left untouched): {skipped}")
    if moved:
        print(
            "COUNTS MOVED under curated prose — re-read each row's note / "
            f"science_question, which may quote the old figures: {moved}"
        )
    if added:
        print(f"ADDED without a science_question — write one: {added}")
    if dropped:
        print(f"DROPPED (all-zero), note and science_question with them: {dropped}")


async def main() -> None:
    args = sys.argv[1:]
    do_inject = "--inject" in args
    if "--pair" in args:
        i = args.index("--pair")
        pair = tuple(sorted(args[i + 1 : i + 3]))
        if len(pair) != 2:
            sys.exit("--pair needs two KG shortnames")
        pairs = [pair]
    else:
        pairs = [tuple(sorted(p)) for p in combinations(sorted(taxon.TAXON_HUB_KGS), 2)]

    bad = [kg for p in pairs for kg in p if not taxon.in_taxon_hub(kg)]
    if bad:
        sys.exit(
            f"not in the taxon hub: {sorted(set(bad))}; members={taxon.TAXON_HUB_KGS}"
        )

    print(f"measuring {len(pairs)} pair(s) (timeout {TIMEOUT:.0f}s each skeleton)\n")
    records: list[dict[str, int | None]] = []
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        for kg_a, kg_b in pairs:
            print(f"  {kg_a} <-> {kg_b}")
            rec = await measure_pair(kg_a, kg_b, client)
            mark = "  *" if _is_nonzero(rec) else ""
            print(
                f"      exact_id={rec['exact_id']} "
                f"clade({kg_a} in {kg_b})={rec['clade_a_in_b']} "
                f"clade({kg_b} in {kg_a})={rec['clade_b_in_a']}{mark}"
            )
            records.append(rec)

    nonzero = [r for r in records if _is_nonzero(r)]
    print(f"\n{len(nonzero)} of {len(records)} pair(s) have a non-zero overlap.")
    if do_inject:
        inject(records)
    else:
        print("dry run — pass --inject to write counts into metadata/crosswalks.json")


if __name__ == "__main__":
    asyncio.run(main())
