"""Tests for the VoID provenance tool (mcp_okn.void + get_kg_version).

run_sparql is patched on the `void` module (where the code looks it up), and a
capturing fake records the SPARQL it was handed so the generated query can be
asserted on without hitting the network.
"""

from mcp_okn import registry, void
from mcp_okn.tools.discovery import get_kg_version


def _capturing(rows):
    captured = {}

    async def fake(q, client=None, **kw):
        captured["query"] = q
        return {"vars": ["s", "version", "last_updated"], "rows": rows}

    return fake, captured


_PROKN_ROW = {
    "s": "https://purl.org/okn/frink/kg/prokn",
    "version": "v0.0.5",
    "last_updated": "2026-06-23T14:26:02.126+00:00",
}


def test_version_query_targets_okn_void_and_pav_predicates():
    q = void._version_query(None)
    assert "kg/okn-void" in q
    assert "http://purl.org/pav/version" in q
    assert "http://purl.org/pav/lastUpdatedOn" in q
    # No-shortname form scans all subjects.
    assert "?s <http://purl.org/pav/version>" in q


def test_version_query_for_one_kg_anchors_on_its_named_graph():
    q = void._version_query("prokn")
    assert "<https://purl.org/okn/frink/kg/prokn> <http://purl.org/pav/version>" in q


def test_shortname_from_iri_strips_prefix():
    assert (
        void._shortname_from_iri("https://purl.org/okn/frink/kg/spoke-okn")
        == "spoke-okn"
    )


async def test_get_kg_version_single_returns_record(monkeypatch):
    fake, _ = _capturing([_PROKN_ROW])
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("prokn")
    assert out["shortname"] == "prokn"
    assert out["version"] == "v0.0.5"
    assert out["last_updated"].startswith("2026-06-23")
    assert "modified" not in out
    assert out["named_graph"] == "https://purl.org/okn/frink/kg/prokn"


async def test_get_kg_version_missing_kg_returns_note(monkeypatch):
    fake, _ = _capturing([])
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("nestkg")
    assert out["shortname"] == "nestkg"
    assert out["version"] is None
    assert "No VoID provenance" in out["note"]


async def test_get_kg_version_all_sorted_and_counted(monkeypatch):
    rows = [
        {
            "s": "https://purl.org/okn/frink/kg/spoke-okn",
            "version": "v0.0.6",
            "last_updated": "2026-03-16T02:27:00.564+00:00",
        },
        _PROKN_ROW,
    ]
    fake, _ = _capturing(rows)
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version()
    assert out["count"] == 2
    # Sorted by shortname regardless of result order.
    assert [r["shortname"] for r in out["versions"]] == ["prokn", "spoke-okn"]


async def test_get_kg_version_filters_excluded_kgs(monkeypatch):
    rows = [
        _PROKN_ROW,
        {
            "s": "https://purl.org/okn/frink/kg/semopenalex",
            "version": "v9",
            "last_updated": None,
        },
    ]
    fake, _ = _capturing(rows)
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version()
    assert [r["shortname"] for r in out["versions"]] == ["prokn"]


async def test_get_kg_version_handles_missing_optional_dates(monkeypatch):
    fake, _ = _capturing(
        [{"s": "https://purl.org/okn/frink/kg/medical-device-kg", "version": "v0.0.1"}]
    )
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("medical-device-kg")
    assert out["version"] == "v0.0.1"
    assert out["last_updated"] is None
    assert "modified" not in out


_STALE_ROW = {
    "s": "https://purl.org/okn/frink/kg/maudekg",
    "version": "v0.0.1",
    "last_updated": "2026-03-16T02:27:00.564+00:00",
}


async def test_get_kg_version_drops_unregistered_from_versions(monkeypatch):
    # A stale VoID entry must not surface as an extra KG: it is kept out of
    # `versions` / `count` and reported separately.
    fake, _ = _capturing([_STALE_ROW, _PROKN_ROW])
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version()
    assert out["count"] == 1
    assert [r["shortname"] for r in out["versions"]] == ["prokn"]
    assert [r["shortname"] for r in out["unregistered"]] == ["maudekg"]


async def test_get_kg_version_omits_unregistered_key_when_clean(monkeypatch):
    fake, _ = _capturing([_PROKN_ROW])
    monkeypatch.setattr(void, "run_sparql", fake)
    assert "unregistered" not in await get_kg_version()


async def test_get_kg_version_single_flags_unregistered(monkeypatch):
    fake, _ = _capturing([_STALE_ROW])
    monkeypatch.setattr(void, "run_sparql", fake)
    out = await get_kg_version("maudekg")
    assert out["version"] == "v0.0.1"
    assert out["registered"] is False
    assert "not in the KG registry" in out["note"]


async def test_get_kg_version_keeps_everything_without_a_registry(monkeypatch):
    # Fail open: an unavailable registry must not turn every KG into a stale one.
    async def no_registry(refresh=False):
        return []

    fake, _ = _capturing([_STALE_ROW, _PROKN_ROW])
    monkeypatch.setattr(void, "run_sparql", fake)
    monkeypatch.setattr(registry, "list_kgs", no_registry)
    out = await get_kg_version()
    assert out["count"] == 2
    assert "unregistered" not in out
