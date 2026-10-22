"""The `- **Contents:**` manifest must match the body after diagrams are re-added.

create_reproducibility_record counts the diagrams it rendered; when some were skipped and later
re-added by the okn-report-style scripts, the header kept the old count (an MS record shipped
"17 queries · 13 query diagrams" over 17 diagrams). expand() now resyncs it, and
readd_query_diagrams --check fails on a stale one."""

import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "skills/okn-report-style/scripts")
)
import expand_query_diagrams as eqd
import readd_query_diagrams as rqd

Q1 = "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/x> { ?s ?p ?o } }"
Q2 = "SELECT ?o WHERE { GRAPH <https://purl.org/okn/frink/kg/y> { ?s ?p ?o } }"
DIAGRAM = 'graph TD\n  subgraph g0["GRAPH x"]\n  v1(["?s"])\n  end'


def _record(contents: str, with_diagram_2: bool = False) -> str:
    second = f"\n\n```mermaid\n{DIAGRAM}\n```" if with_diagram_2 else ""
    return (
        "# Record\n\n- **Date:** 2026-10-21\n"
        f"- **Contents:** {contents}\n\n"
        f"## Query 1\n\n```sparql\n{Q1}\n```\n\n```mermaid\n{DIAGRAM}\n```\n\n"
        f"## Query 2\n\n```sparql\n{Q2}\n```{second}\n"
    )


def test_expand_updates_contents_after_readding():
    text = _record("2 queries · 1 query diagram")
    new, st = eqd.expand(text, lambda q: DIAGRAM)
    assert st["added"] == 1 and st["contents_synced"]
    assert "- **Contents:** 2 queries · 2 query diagrams\n" in new


def test_expand_adds_diagram_part_when_header_had_none():
    text = _record("2 queries").replace(f"```mermaid\n{DIAGRAM}\n```\n\n", "", 1)
    new, _ = eqd.expand(text, lambda q: DIAGRAM)
    assert "- **Contents:** 2 queries · 2 query diagrams\n" in new


def test_schema_diagram_count_is_preserved():
    text = _record("2 queries · 1 query diagram · 1 schema diagram")
    new, _ = eqd.expand(text, lambda q: DIAGRAM)
    assert "2 queries · 2 query diagrams · 1 schema diagram" in new


def test_accurate_contents_is_left_alone():
    text = _record("2 queries · 2 query diagrams", with_diagram_2=True)
    assert eqd.sync_contents(text) == (text, False)


def test_check_fails_on_stale_contents(tmp_path, capsys):
    p = tmp_path / "r.md"
    text = _record("2 queries · 1 query diagram", with_diagram_2=True)
    assert rqd.check(p, text) == 1
    assert "Contents counts don't match" in capsys.readouterr().out


def test_check_passes_on_accurate_contents(tmp_path):
    p = tmp_path / "r.md"
    assert rqd.check(p, _record("2 queries · 2 query diagrams", True)) == 0


def test_readd_main_fixes_stale_contents_when_all_diagrams_present(tmp_path):
    p = tmp_path / "r.md"
    p.write_text(_record("2 queries · 1 query diagram", with_diagram_2=True))
    rqd.main([str(p), "--diagrams", str(_empty_diagrams(tmp_path))])
    assert "- **Contents:** 2 queries · 2 query diagrams\n" in p.read_text()
    assert rqd.check(p, p.read_text()) == 0


def _empty_diagrams(tmp_path: Path) -> Path:
    d = tmp_path / "diagrams.json"
    d.write_text("[]")
    return d


def test_queries_quoted_above_the_logged_body_are_not_counted():
    # A hand-inserted section (Diabetes: "Branch queries NOT in the logged record") quotes extra
    # sparql above "## SPARQL queries"; the manifest counts only the server's logged body.
    text = _record("2 queries · 1 query diagram").replace(
        "## Query 1",
        f"## Replicator specification\n\n```sparql\n{Q2}\n```\n\n## SPARQL queries\n\n## Query 1",
        1,
    )
    new, _ = eqd.expand(text, lambda q: DIAGRAM)
    assert "- **Contents:** 2 queries · 2 query diagrams\n" in new
