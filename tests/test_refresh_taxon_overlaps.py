"""`refresh_taxon_overlaps.py --inject` must change counts and nothing else.

It used to rebuild each re-measured row from its three counts, which silently
deleted the curated ``science_question`` / ``note`` and re-sorted the table. The
loss surfaced only when a refreshed pair's example question went missing from the
inventory.
"""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "refresh_taxon_overlaps", ROOT / "scripts" / "refresh_taxon_overlaps.py"
)
assert _spec and _spec.loader
refresh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(refresh)


def _row(a, b, exact, a_in_b, b_in_a, **extra):
    return {
        "kg_a": a,
        "kg_b": b,
        "exact_id": exact,
        "clade_a_in_b": a_in_b,
        "clade_b_in_a": b_in_a,
        **extra,
    }


#: Deliberately NOT in (kg_a, kg_b) order, and with a label-bridged row the script
#: never measures, so a re-sort or a rebuild would both show.
PAIRWISE = [
    _row("nde", "sawgraph", 73, 1727, 538, science_question="Which organisms…?"),
    {
        "kg_a": "biohealth",
        "kg_b": "sawgraph",
        "label_match": 377,
        "kg_b_taxa": 538,
        "match_type": "label",
        "note": "label-bridged",
        "science_question": "Which organisms biohealth names…?",
    },
    _row("biobricks-aopwiki", "nde", 5, 9, 11, science_question="AOPs vs NDE?"),
    _row(
        "sawgraph", "wildlifekn", 2, 2, 339, note="label-bridged", science_question="Q?"
    ),
]


@pytest.fixture
def table(tmp_path, monkeypatch):
    src = tmp_path / "crosswalks.json"
    src.write_text(
        json.dumps({"taxon_hub": {"pairwise": PAIRWISE, "verified_on": "2026-01-01"}})
    )
    monkeypatch.setattr(refresh, "SRC", src)
    return lambda: json.loads(src.read_text())["taxon_hub"]["pairwise"]


def test_remeasured_pair_keeps_its_prose_and_position(table):
    refresh.inject([_row("nde", "sawgraph", 26, 34, 86)])
    rows = table()
    assert [(r["kg_a"], r["kg_b"]) for r in rows] == [
        (r["kg_a"], r["kg_b"]) for r in PAIRWISE
    ], "a refresh must not reorder the table"
    assert rows[0] == _row(
        "nde", "sawgraph", 26, 34, 86, science_question="Which organisms…?"
    )
    # every row not measured in this run is byte-for-byte what it was
    assert rows[1:] == PAIRWISE[1:]


def test_note_survives_alongside_the_question(table):
    refresh.inject([_row("sawgraph", "wildlifekn", 3, 3, 4)])
    row = table()[3]
    assert (row["exact_id"], row["clade_a_in_b"], row["clade_b_in_a"]) == (3, 3, 4)
    assert row["note"] == "label-bridged" and row["science_question"] == "Q?"


def test_all_zero_pair_is_dropped_and_others_are_untouched(table):
    refresh.inject([_row("biobricks-aopwiki", "nde", 0, 0, 0)])
    assert table() == [PAIRWISE[0], PAIRWISE[1], PAIRWISE[3]]


def test_errored_pair_is_left_exactly_as_stored(table):
    refresh.inject([_row("nde", "sawgraph", 26, None, 86)])
    assert table() == PAIRWISE


def test_new_pair_is_appended_not_sorted_in(table):
    refresh.inject([_row("nde", "spoke-okn", 1, 2, 3)])
    rows = table()
    assert rows[:-1] == PAIRWISE
    assert rows[-1] == _row("nde", "spoke-okn", 1, 2, 3)


def test_run_reports_rows_whose_prose_needs_a_human_read(table, capsys):
    refresh.inject(
        [
            _row("nde", "sawgraph", 26, 34, 86),  # counts moved under a question
            _row("biobricks-aopwiki", "nde", 5, 9, 11),  # unchanged: not reported
            _row("nde", "spoke-okn", 1, 2, 3),  # new: has no question yet
            _row("sawgraph", "wildlifekn", 0, 0, 0),  # dropped
        ]
    )
    out = capsys.readouterr().out
    assert "COUNTS MOVED" in out and "('nde', 'sawgraph')" in out
    assert "('biobricks-aopwiki', 'nde')" not in out
    assert "ADDED without a science_question" in out and "('nde', 'spoke-okn')" in out
    assert "DROPPED" in out and "('sawgraph', 'wildlifekn')" in out
