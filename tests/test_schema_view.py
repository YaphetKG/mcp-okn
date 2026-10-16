import json

import mcp_okn.server as srv
from mcp_okn.schema import _generate_query_template
from mcp_okn.schema_view import (
    compact_iris,
    fit_to_budget,
    match_schema,
    reply_size,
)

NS = "https://purl.org/okn/frink/kg/demo/schema/"
BIOLINK = "https://w3id.org/biolink/vocab/"


def _reply(n_classes=5, desc="x" * 40):
    """A get_schema reply shaped like a VoID-built one: IRIs, counts, edges."""
    classes = [
        [f"{BIOLINK}C{i}", f"C{i}", desc, "Class", 1000 - i] for i in range(n_classes)
    ]
    preds = [
        [
            f"{NS}p{i}",
            f"p{i}",
            desc,
            "Predicate",
            f"{BIOLINK}C0",
            f"{BIOLINK}C1",
            i == 0,
            "direct",
            10 * i,
            "",
        ]
        for i in range(20)
    ]
    edge = {
        "uri": f"{NS}p0",
        "label": "p0",
        "description": desc,
        "source_class": f"{BIOLINK}C0",
        "target_class": f"{BIOLINK}C1",
        "properties": [
            {
                "uri": f"{NS}state_abbr",
                "label": "State Abbreviation",
                "description": "two-letter state",
                "type": "EdgeProperty",
            }
        ],
        "query_template": "SELECT * WHERE { ?s ?p ?o }" * 5,
    }
    return {
        "shortname": "demo",
        "schema": {
            "classes": {
                "columns": ["uri", "label", "description", "type", "instances"],
                "data": classes,
                "count": len(classes),
            },
            "predicates": {
                "columns": [
                    "uri",
                    "label",
                    "description",
                    "type",
                    "source_class",
                    "target_class",
                    "has_edge_properties",
                    "pattern",
                    "triples",
                    "other_pairs",
                ],
                "data": preds,
                "count": len(preds),
            },
            "edge_properties": {"p0": edge},
            "node_properties": {
                "columns": ["uri", "label", "description", "type", "class"],
                "data": [],
                "count": 0,
            },
        },
        "next_step": "probe_namespaces before joining",
    }


def test_a_reply_that_fits_is_returned_unchanged():
    reply = _reply()
    assert fit_to_budget(reply, "demo", budget=100_000) is reply


def test_over_budget_trims_detail_before_rows_and_says_what_it_did():
    reply = _reply()
    budget = reply_size(reply) - 200  # just over: lossless steps suffice
    out = fit_to_budget(reply, "demo", budget=budget)
    assert reply_size(out) <= budget
    view = out["schema_view"]
    assert view["budget_chars"] == budget
    assert "edge_properties query_template" in view["trimmed"]
    assert "omitted" not in view  # no row was cut
    assert out["schema"]["predicates"]["count"] == 20
    assert "match=" in view["how_to_get_more"]
    assert out["next_step"] == reply["next_step"]
    # The input is not modified.
    assert "query_template" in reply["schema"]["edge_properties"]["p0"]


def test_short_iris_expand_back_exactly():
    reply = _reply()
    out = fit_to_budget(reply, "demo", budget=reply_size(reply) // 2)
    prefixes = out["schema_view"]["prefixes"]
    assert prefixes["kg"] == NS  # the KG's own namespace is kg:, not schema:
    assert prefixes["biolink"] == BIOLINK
    assert f"PREFIX kg: <{NS}>" in out["schema_view"]["sparql_prefixes"]
    cols = out["schema"]["predicates"]["columns"]
    row = out["schema"]["predicates"]["data"][0]
    name, local = row[cols.index("uri")].split(":", 1)
    original = {r[0] for r in reply["schema"]["predicates"]["data"]}
    assert prefixes[name] + local in original


def test_rows_go_last_largest_first_and_are_counted():
    reply = _reply(n_classes=400)
    budget = 12_000
    out = fit_to_budget(reply, "demo", budget=budget)
    assert reply_size(out) <= budget
    classes = out["schema"]["classes"]
    cut = out["schema_view"]["omitted"]["classes"]
    assert cut > 0 and classes["count"] + cut == 400 == classes["total"]
    counts = [row[classes["columns"].index("instances")] for row in classes["data"]]
    assert counts == sorted(counts, reverse=True)
    # Every predicate survives: classes were cut instead.
    assert out["schema"]["predicates"]["count"] == 20


def test_schema_org_prefix_keeps_its_scheme():
    schema = {
        "classes": {
            "columns": ["uri"],
            "data": [[f"https://schema.org/T{i}"] for i in range(3)]
            + [[f"http://schema.org/T{i}"] for i in range(3)]
            + [[f"https://www.w3.org/2002/07/owl#K{i}"] for i in range(3)]
            + [[f"http://example.org/{i}/schema/T"] for i in range(1)],
        }
    }
    prefixes = compact_iris(schema)
    assert prefixes["schema"] == "http://schema.org/"
    assert prefixes["schema_https"] == "https://schema.org/"
    assert prefixes["owl_https"] == "https://www.w3.org/2002/07/owl#"
    # A namespace used fewer than three times keeps its full IRIs.
    assert ["http://example.org/0/schema/T"] in schema["classes"]["data"]


def test_match_finds_a_relationship_by_its_edge_property():
    out = match_schema(_reply(), "state abbreviation|nothing-like-this")
    preds = [row[0] for row in out["schema"]["predicates"]["data"]]
    assert preds == [f"{NS}p0"]
    assert list(out["schema"]["edge_properties"]) == ["p0"]
    assert "query_template" in out["schema"]["edge_properties"]["p0"]
    # The classes it connects come with it.
    classes = {row[0] for row in out["schema"]["classes"]["data"]}
    assert classes == {f"{BIOLINK}C0", f"{BIOLINK}C1"}
    view = out["schema_view"]
    assert view["found"]["predicates"] == 1 and view["of"]["predicates"] == 20


def test_match_on_a_class_brings_its_predicates():
    out = match_schema(_reply(), "c0")
    assert out["schema"]["predicates"]["count"] == 20  # all run C0 -> C1


def test_match_with_no_hit_says_so():
    out = match_schema(_reply(), "zzz")
    assert not any(out["schema_view"]["found"].values())
    assert "Nothing" in out["schema_view"]["note"]


def test_template_variables_use_the_local_name_of_an_iri_class():
    tmpl = _generate_query_template(
        "demo", "RELATES", f"{BIOLINK}Disease", "https://schema.org/Place", []
    )
    assert "?disease ?place" in tmpl
    assert "httpsw3id" not in tmpl


async def test_tool_applies_match_and_budget(monkeypatch):
    async def fake_schema(shortname, compact=True):
        return _reply(n_classes=2000)

    monkeypatch.setattr(srv.schema, "get_schema", fake_schema)
    monkeypatch.setattr(srv.schema, "usage_notes", lambda kg: None)
    full = await srv.get_schema("demo")
    assert len(json.dumps(full, separators=(",", ":"))) <= 40_000
    assert full["schema_view"]["omitted"]["classes"] > 0
    found = await srv.get_schema("demo", match="C1999")
    rows = found["schema"]["classes"]["data"]
    assert [r[0] for r in rows] == [f"{BIOLINK}C1999"]
