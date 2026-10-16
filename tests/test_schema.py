import httpx
import pytest

import mcp_okn.schema as schema_mod
from mcp_okn.schema import (
    _build_schema_from_metadata,
    _generate_query_template,
    _member_type,
    _should_exclude_uri,
    build_mermaid_diagram,
    infer_edge_labels,
    parse_entity_metadata,
    usage_notes,
    void_is_stale,
)


def _parse(csv_text: str) -> dict[str, dict]:
    """fetch_entity_metadata's CSV parsing, without the network."""
    return parse_entity_metadata(csv_text)


SIMPLE_CSV = """\
URI,Label,Description,Type
http://schema.org/Person,Person,A human being.,Class
http://schema.org/name,name,The name of the thing.,Predicate
"""

EDGE_CSV = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
https://ex.org/schema/Gene,Gene,A gene.,Class,,,
https://ex.org/schema/Sample,Sample,A sample.,Class,,,
https://ex.org/schema/MEASURED_EXPR,MEASURED_EXPR,Expression edge.,Predicate,,Sample,Gene
https://ex.org/schema/log2fc,log2fc,Log2 fold change (float).,EdgeProperty,MEASURED_EXPR,,
https://ex.org/schema/pval,pval,P-value (float).,EdgeProperty,MEASURED_EXPR,,
"""


def test_build_schema_classes_and_predicates():
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    assert schema["classes"]["count"] == 1
    assert schema["classes"]["data"][0][0] == "http://schema.org/Person"
    assert schema["predicates"]["count"] == 1
    # No edge properties -> the predicate is not flagged.
    pred_row = schema["predicates"]["data"][0]
    has_edge_props = pred_row[
        schema["predicates"]["columns"].index("has_edge_properties")
    ]
    assert has_edge_props is False
    assert schema["edge_properties"] == {}
    # Compact omits the summary.
    assert "edge_property_summary" not in schema


def test_build_schema_edge_properties_and_template():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=False)
    edges = schema["edge_properties"]
    assert "MEASURED_EXPR" in edges
    edge = edges["MEASURED_EXPR"]
    assert edge["source_class"] == "Sample"
    assert edge["target_class"] == "Gene"
    assert {p["label"] for p in edge["properties"]} == {"log2fc", "pval"}
    # The predicate carrying edge properties is flagged.
    pred_row = next(
        r for r in schema["predicates"]["data"] if r[0].endswith("MEASURED_EXPR")
    )
    idx = schema["predicates"]["columns"].index("has_edge_properties")
    assert pred_row[idx] is True
    # Non-compact prepends the edge-property summary.
    assert "edge_property_summary" in schema
    # The generated template uses RDF reification scoped to the KG schema NS.
    tmpl = edge["query_template"]
    assert "rdf:subject" in tmpl
    # The relationship's own IRI, not schema:<label> in the KG's purl namespace
    # (wildlifekn's https://wildlife.proto-okn.net/kg/OBSERVED_AT was mis-templated).
    assert "rdf:predicate <https://ex.org/schema/MEASURED_EXPR>" in tmpl
    assert "purl.org/okn/frink/kg/demo/schema/" in tmpl


def test_edge_property_of_accumulates_multiple_parents():
    csv_text = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
https://ex.org/schema/adj_p,adj_p,Adjusted p-value.,EdgeProperty,EXPRESSION,,
https://ex.org/schema/adj_p,adj_p,Adjusted p-value.,EdgeProperty,ABUNDANCE,,
"""
    meta = _parse(csv_text)
    assert (
        meta["https://ex.org/schema/adj_p"]["edge_property_of"]
        == "EXPRESSION;ABUNDANCE"
    )


def test_generate_query_template_shape():
    props = [
        {"uri": "https://purl.org/okn/frink/kg/demo/schema/score", "label": "score"}
    ]
    tmpl = _generate_query_template("demo", "RELATES", "Foo", "Bar", props)
    assert "SELECT ?foo ?bar ?score" in tmpl
    assert "schema:RELATES" in tmpl
    assert "GRAPH <https://purl.org/okn/frink/kg/demo>" in tmpl
    assert tmpl.rstrip().endswith("}")


def test_generate_query_template_properties_optional_by_local_name():
    # Edge properties are sparse, so each must be OPTIONAL; a prose label must
    # not leak into the predicate or variable (spoke-okn "Activity Sources").
    ns = "https://purl.org/okn/frink/kg/demo/schema/"
    props = [
        {"uri": ns + "act_sources", "label": "Activity Sources"},
        {"uri": ns + "phase", "label": "Phase"},
    ]
    tmpl = _generate_query_template("demo", "TREATS", "Chem", "Disease", props)
    assert "OPTIONAL { ?stmt schema:act_sources ?act_sources }" in tmpl
    assert "OPTIONAL { ?stmt schema:phase ?phase }" in tmpl
    assert "Activity Sources" not in tmpl
    assert "rdf:object ?disease ." in tmpl


def test_generate_query_template_same_class_gets_distinct_vars():
    props = [{"uri": "https://purl.org/okn/frink/kg/demo/schema/odds", "label": "Odds"}]
    tmpl = _generate_query_template("demo", "RESEMBLES", "Disease", "Disease", props)
    assert "rdf:subject ?disease_1" in tmpl
    assert "rdf:object ?disease_2" in tmpl


def test_should_exclude_rdf_syntax_uris():
    assert _should_exclude_uri("http://www.w3.org/1999/02/22-rdf-syntax-ns#_1")
    assert not _should_exclude_uri("http://schema.org/Person")


def test_member_type_extracts_trailing_parenthetical():
    assert _member_type("Log2 fold change (float)") == "float"
    assert _member_type("Adjusted p-value (FDR-corrected). (float)") == "float"
    # No usable type -> empty (don't treat a sentence in parens as a type).
    assert _member_type("Some prose (with several words)") == ""
    assert _member_type("plain description") == ""


def test_build_mermaid_diagram_edges_and_intermediary_classes():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    diagram = build_mermaid_diagram("demo", schema)
    assert diagram.startswith("classDiagram")
    assert "direction TB" in diagram
    # Node classes appear as boxes.
    assert "class Gene" in diagram
    assert "class Sample" in diagram
    # The edge-property predicate becomes an intermediary class with typed fields,
    # wired source --> edge --> target.
    assert "class MEASURED_EXPR {" in diagram
    assert "float log2fc" in diagram
    assert "Sample --> MEASURED_EXPR" in diagram
    assert "MEASURED_EXPR --> Gene" in diagram
    # Node classes are light blue; the edge class is orange.
    assert "style Gene fill:#BBDEFB" in diagram
    assert "style Sample fill:#BBDEFB" in diagram
    assert "style MEASURED_EXPR fill:#FFE0B2" in diagram
    # A two-entry legend (node + edge) is included.
    assert 'class LegendNodeClass["Node class"]' in diagram
    assert 'class LegendEdgeClass["Edge (relationship) class"]' in diagram
    assert "style LegendNodeClass fill:#BBDEFB" in diagram
    assert "style LegendEdgeClass fill:#FFE0B2" in diagram


def test_build_mermaid_diagram_lists_undrawn_predicates():
    # Predicates without source/target metadata are listed as comments, not edges.
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    diagram = build_mermaid_diagram("demo", schema)
    assert "class Person" in diagram
    assert "%%   - name" in diagram
    assert "-->" not in diagram  # no endpoints, so nothing is drawn as an edge
    # No edge classes -> legend has the node entry only.
    assert 'class LegendNodeClass["Node class"]' in diagram
    assert "LegendEdgeClass" not in diagram


def test_inferred_edges_drawn_and_excluded_from_undrawn():
    # SIMPLE_CSV has class Person and predicate `name` with no endpoints — `name`
    # is normally listed as undrawn. An inferred edge draws it and drops the note.
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)
    diagram = build_mermaid_diagram(
        "demo", schema, inferred_edges=[("Person", "name", "Person")]
    )
    assert "Person --> Person : name" in diagram
    assert "%%   - name" not in diagram


async def test_infer_edge_labels_skips_when_curated_edges_exist():
    # EDGE_CSV declares source/target — inference must be a no-op (and make no
    # network call, since it returns before querying).
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    assert await infer_edge_labels("demo", schema) == []


async def test_infer_edge_labels_maps_uris_to_labels(monkeypatch):
    schema = _build_schema_from_metadata("demo", _parse(SIMPLE_CSV), compact=True)

    async def fake_infer(shortname, class_uris, pred_uris, limit=400):
        return [
            (
                "http://schema.org/name",
                "http://schema.org/Person",
                "http://schema.org/Person",
            )
        ]

    monkeypatch.setattr(schema_mod, "infer_curated_edges", fake_infer)
    assert await infer_edge_labels("demo", schema) == [("Person", "name", "Person")]


def test_usage_notes_spoke_genelab_carries_both_rules():
    notes = usage_notes("spoke-genelab")
    assert notes is not None
    assert set(notes) == {"guidance", "query_snippet"}
    guidance = notes["guidance"]
    snippet = notes["query_snippet"]
    # Rule 1 (direction) pins SF arm 1 vs GC arm 2.
    assert 'schema:factor_space_1 "Space Flight"' in snippet
    assert 'schema:factor_space_2 "Ground Control"' in snippet
    # Rule 2 (comparability) strips the spelled-out condition labels (incl. the
    # in-vitro one), case-insensitively...
    for label in (
        "space flight",
        "ground control",
        "basal control",
        "vivarium control",
        "cell culture control",
    ):
        assert label in snippet
    # ...and the short group codes via the anchored regex (GC, FLT_C1, VIV_C2, …).
    assert "^(GC|FLT|VIV|BSL|CC)(_C[0-9]+)?$" in snippet
    assert "material_id_1" in snippet and "material_id_2" in snippet
    # Rule 2 is the WITHIN-assay test: a covariate present on one arm but absent
    # on the other (factors_1 vs factors_2) disqualifies the assay. The snippet
    # must cross-reference the two arms, not just emit two separate signatures.
    assert "schema:factors_1 ?x" in snippet
    assert "FILTER NOT EXISTS { ?assay schema:factors_2 ?x }" in snippet
    assert "schema:factors_2 ?y" in snippet
    assert "FILTER NOT EXISTS { ?assay schema:factors_1 ?y }" in snippet
    # It steers to the vetted-contrast tool rather than the hand-written self-join.
    assert "get_valid_contrasts" in snippet
    # Guidance states both rules, leads with the within-assay case, sign convention.
    assert "DIRECTION" in guidance and "COMPARABILITY" in guidance
    assert "GROUP CODES" in guidance
    assert "WITHIN-assay" in guidance or "within-assay" in guidance


def test_condition_code_regex_matches_codes_not_real_factors():
    import re

    from mcp_okn.contrasts import (
        SPOKE_GENELAB_CONDITION_CODE_REGEX,
        SPOKE_GENELAB_CONDITION_LABELS,
        SPOKE_GENELAB_CONTRAST_SNIPPET,
    )

    assert "Cell Culture Control" in SPOKE_GENELAB_CONDITION_LABELS
    # The snippet uses the same regex constant (no drift).
    assert SPOKE_GENELAB_CONDITION_CODE_REGEX in SPOKE_GENELAB_CONTRAST_SNIPPET
    pat = re.compile(SPOKE_GENELAB_CONDITION_CODE_REGEX)
    # Group codes (with/without cohort suffix) match.
    for code in ("GC", "FLT", "VIV_C2", "BSL_C1", "CC_C1", "GC_C2", "FLT_C1"):
        assert pat.match(code), code
    # Real factors that merely contain a control word must NOT match.
    for real in (
        "Hardware 1G Ground Control",
        "HLU_IR",
        "Euth_C_DI",
        "GCN2 KO",
        "FLTbox",
    ):
        assert not pat.match(real), real


def test_usage_notes_glygenkg_carries_the_record_to_protein_rule():
    """glygenkg's central class is a glycosylation RECORD with no edge to its
    protein; the notes must hand over the PR_ -> UniProt rewrite and warn about the
    two FALDO namespaces, both of which return 0 rows silently when missed."""
    notes = usage_notes("glygenkg")
    assert notes is not None
    guidance, snippet = notes["guidance"], notes["query_snippet"]
    assert "RECORD, NOT A PROTEIN" in guidance
    assert "gly:has_pro_entry" in guidance
    assert "http://www.biohackathon.org/resource/faldo#" in guidance
    assert "http://biohackathon.org/resource/faldo#" in guidance
    assert "get_join_strategy" in guidance
    # the snippet applies the rewrite it describes, in the right FALDO namespace
    assert "http://purl.obolibrary.org/obo/PR_" in snippet
    assert "<http://www.biohackathon.org/resource/faldo#>" in snippet
    assert "/kg/glygenkg>" in snippet


def test_usage_notes_absent_for_other_kgs():
    assert usage_notes("prokn") is None
    assert usage_notes("spoke-okn") is None


def test_instructions_include_spaceflight_contrast_section():
    from mcp_okn.app import INSTRUCTIONS

    assert "SPOKE-GENELAB SPACEFLIGHT CONTRASTS" in INSTRUCTIONS
    for label in (
        "Space Flight",
        "Ground Control",
        "Basal Control",
        "Vivarium Control",
    ):
        assert label in INSTRUCTIONS


def test_build_mermaid_diagram_probe_shape_classes_only():
    # Probe-shape schema (bare uri columns) -> class boxes from local names.
    schema = {
        "classes": {
            "columns": ["uri"],
            "data": [["http://schema.org/Person"]],
            "count": 1,
        },
        "predicates": {
            "columns": ["uri"],
            "data": [["http://schema.org/name"]],
            "count": 1,
        },
        "edge_properties": {},
        "node_properties": {"columns": ["uri"], "data": [], "count": 0},
    }
    diagram = build_mermaid_diagram("demo", schema)
    assert "class Person" in diagram
    assert "%%   - name" in diagram


# ── _probe_schema (the fallback for KGs with no curated metadata) ─────────────


def _stub_probe(monkeypatch, by_var, fail=None):
    """Stub run_sparql for _probe_schema, recording the queries it issues.

    `by_var` maps the projected variable ("class"/"predicate") to rows; the two
    class queries are told apart by whether the query asks for declared classes.
    `fail` is an exception raised for the query whose text contains that substring.
    """
    sent = []

    async def fake_run_sparql(query, *a, **kw):
        sent.append(query)
        if fail and fail[0] in query:
            raise fail[1]
        if "?predicate" in query:
            return {"rows": [{"predicate": p} for p in by_var.get("predicate", [])]}
        key = "declared" if "rdf-schema#Class" in query else "instance"
        return {"rows": [{"class": c} for c in by_var.get(key, [])]}

    monkeypatch.setattr(schema_mod, "run_sparql", fake_run_sparql)
    return sent


async def test_probe_schema_merges_both_class_queries(monkeypatch):
    """Instantiated and merely-DECLARED classes are probed separately — combining
    them in one UNION made QLever try to allocate 37.9 GB and fail on every graph.
    The two result sets are merged, de-duplicated, and sorted here instead.
    """
    sent = _stub_probe(
        monkeypatch,
        {
            "instance": ["http://ex.org/Gene", "http://ex.org/Drug"],
            "declared": ["http://ex.org/Drug", "http://ex.org/Unused"],
            "predicate": ["http://ex.org/treats", "http://ex.org/name"],
        },
    )
    out = await schema_mod._probe_schema("demo")

    assert len(sent) == 3  # instance types, declared classes, predicates
    assert not any("UNION" in q and "?s a ?class" in q for q in sent)
    assert out["classes"]["data"] == [
        ["http://ex.org/Drug"],  # in both results, listed once
        ["http://ex.org/Gene"],
        ["http://ex.org/Unused"],  # declared but never instantiated
    ]
    assert out["classes"]["count"] == 3
    assert out["predicates"]["data"] == [
        ["http://ex.org/name"],
        ["http://ex.org/treats"],
    ]


async def test_probe_schema_excludes_rdf_syntax_uris(monkeypatch):
    _stub_probe(
        monkeypatch,
        {
            "instance": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"],
            "declared": ["http://ex.org/Real"],
            "predicate": ["http://www.w3.org/1999/02/22-rdf-syntax-ns#_1"],
        },
    )
    out = await schema_mod._probe_schema("demo")
    assert out["classes"]["data"] == [["http://ex.org/Real"]]
    assert out["predicates"]["data"] == []


async def test_probe_schema_propagates_a_failed_probe(monkeypatch):
    """The probes run concurrently with return_exceptions=True, so a failure must
    still reach the caller rather than being swallowed with the sibling's result."""
    boom = RuntimeError("endpoint said no")
    _stub_probe(
        monkeypatch, {"instance": ["http://ex.org/A"]}, fail=("?predicate", boom)
    )
    with pytest.raises(RuntimeError, match="endpoint said no"):
        await schema_mod._probe_schema("demo")


# ── VoID-built entity files (metadata/void_entities) ─────────────────────────

SG = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"
DE = SG + "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"
STMT = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement"
XSD = "http://www.w3.org/2001/XMLSchema#"

#: Trimmed from metadata/void_entities/spoke-genelab_entities.csv (2026-10-15).
VOID_CSV = f"""\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
{SG}Assay,Assay,,Class,,,,13146,
{DE},DE,,Predicate,,http://purl.obolibrary.org/obo/OBI_0000070,https://w3id.org/biolink/vocab/Gene,50208066,direct;reified
{SG}taxonomy,taxonomy,,Predicate,,{SG}Study,,212,direct
{SG}name,name,,Predicate,,{SG}Study,{XSD}string,10,direct
{SG}name,name,,Predicate,,{SG}Mission,{XSD}string,40,direct
{SG}name,name,,Predicate,,{SG}Gene,{XSD}string,30,direct
{SG}name,name,,Predicate,,{SG}Assay,{XSD}string,20,direct
{SG}name,name,,Predicate,,{SG}Organism,{XSD}string,5,direct
{SG}log2fc,log2fc,,Predicate,{DE},{STMT},{XSD}double,50208066,
{SG}log2fc,log2fc,,Predicate,{DE},{STMT},{XSD}string,2,
"""


def test_parse_void_layout_rolls_pairs_up_per_uri():
    meta = parse_entity_metadata(VOID_CSV)
    name = meta[SG + "name"]
    assert name["triples"] == 105
    assert (name["source_class"], name["target_class"]) == (
        SG + "Mission",
        XSD + "string",
    )
    assert [p[2] for p in name["pairs"]] == [40, 30, 20, 10, 5]
    assert meta[SG + "Assay"]["triples"] == 13146


def test_void_edge_property_rows_become_edge_properties_with_iri_parent():
    meta = parse_entity_metadata(VOID_CSV)
    log2fc = meta[SG + "log2fc"]
    assert log2fc["type"] == "EdgeProperty"
    assert log2fc["edge_property_of"] == DE  # deduplicated across datatype rows
    schema = _build_schema_from_metadata("spoke-genelab", meta, compact=True)
    edge = schema["edge_properties"]["MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"]
    assert [p["label"] for p in edge["properties"]] == ["log2fc"]
    assert (
        "rdf:predicate schema:MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"
        in (edge["query_template"])
    )
    preds = schema["predicates"]
    flag = preds["columns"].index("has_edge_properties")
    (de_row,) = [r for r in preds["data"] if r[0] == DE]
    assert de_row[flag] is True


def test_void_rollup_adds_counts_and_extra_pairs():
    schema = _build_schema_from_metadata(
        "spoke-genelab", parse_entity_metadata(VOID_CSV), compact=True
    )
    assert schema["classes"]["columns"][-1] == "instances"
    preds = schema["predicates"]
    cols = preds["columns"]
    assert cols[-3:] == ["pattern", "triples", "other_pairs"]
    rows = {r[0]: dict(zip(cols, r, strict=True)) for r in preds["data"]}
    assert rows[SG + "name"]["triples"] == 105
    assert rows[SG + "name"]["other_pairs"] == (
        "Gene → string (30); Assay → string (20); Study → string (10); +1 more"
    )
    assert rows[SG + "taxonomy"]["other_pairs"] == ""
    assert rows[DE]["pattern"] == "direct;reified"
    assert rows[SG + "name"]["pattern"] == "direct"


def test_curated_layout_output_has_no_new_columns():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    assert schema["classes"]["columns"] == ["uri", "label", "description", "type"]
    assert schema["predicates"]["columns"][-1] == "has_edge_properties"


@pytest.mark.parametrize(
    ("fresh", "stale"),
    [
        (None, False),
        ({"matches": True}, False),
        ({"matches": None, "void_triples": 5, "served_triples": None}, False),
        # sawgraph 2026-10-15: 279 triples of 161M — use it.
        (
            {"matches": False, "void_triples": 161265076, "served_triples": 161264797},
            False,
        ),
        # biomarkerkg 2026-10-14: VoID describes another release.
        ({"matches": False, "void_triples": 1820793, "served_triples": 1215057}, True),
        ({"matches": False, "void_triples": 95913, "served_triples": 0}, True),
    ],
)
def test_void_is_stale(fresh, stale):
    assert void_is_stale(fresh) is stale


CURATED_CSV = "URI,Label,Description,Type\nhttps://ex.org/C,C,curated,Class\n"


@pytest.fixture
def curated_client():
    """An httpx client that serves CURATED_CSV for every curated-file URL."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url).startswith(schema_mod.ENTITY_METADATA_BASE)
        return httpx.Response(200, text=CURATED_CSV)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_override_dir_used_then_curated_fallback(tmp_path, curated_client):
    (tmp_path / "fresh_entities.csv").write_text(VOID_CSV)
    (tmp_path / "stale_entities.csv").write_text(VOID_CSV)
    (tmp_path / "build_notes.json").write_text(
        '{"freshness": {"stale": {"matches": false, "void_triples": 100,'
        ' "served_triples": 50}}}'
    )
    schema_mod._notes_cache.clear()
    got = {}
    for kg in ("fresh", "stale", "absent"):
        meta = await schema_mod.fetch_entity_metadata(
            kg, client=curated_client, refresh=True, override=str(tmp_path)
        )
        got[kg] = (schema_mod.metadata_source(kg), len(meta))
    assert got["fresh"] == (str(tmp_path), len(parse_entity_metadata(VOID_CSV)))
    assert got["stale"] == (schema_mod.ENTITY_METADATA_BASE, 1)
    assert got["absent"] == (schema_mod.ENTITY_METADATA_BASE, 1)


def test_edge_property_of_on_a_node_class_stays_a_predicate():
    """oard-kg: result-node properties, not reified-edge properties (no rdf:predicate)."""
    bl = "https://w3id.org/biolink/vocab/"
    meta = parse_entity_metadata(
        "URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass\n"
        f"{bl}has_study_results,hsr,,Predicate,,{bl}Study,{bl}LogOddsAnalysisResult\n"
        f"{bl}log_odds_ratio,lor,,Predicate,{bl}has_study_results,"
        f"{bl}LogOddsAnalysisResult,\n"
    )
    assert meta[bl + "log_odds_ratio"]["type"] == "Predicate"
    assert meta[bl + "log_odds_ratio"]["edge_property_of"] == ""
    schema = _build_schema_from_metadata("oard-kg", meta, compact=True)
    assert schema["edge_properties"] == {}


#: Shapes from the curated wildlifekn and scales files (2026-10-15).
MIXED_CSV = """\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass
https://ex.org/OBSERVED_AT,OBSERVED_AT,Seen at.,Predicate,,https://ex.org/Bird,https://ex.org/Location
https://ex.org/OBSERVED_AT,OBSERVED_AT,Seen at.,Predicate,,https://ex.org/Frog,https://ex.org/Location
https://ex.org/date,date,Observation date.,EdgeProperty,OBSERVED_AT,,
https://ex.org/date,date,Date of an observation.,NodeProperty,,https://ex.org/Observation,
https://ex.org/Arrest,Arrest,An arrest.,Class,,,
https://ex.org/Arrest,Arrest,Has arrest.,Predicate,,https://ex.org/Person,https://ex.org/Arrest
"""


def test_uri_with_several_kinds_keeps_each():
    schema = _build_schema_from_metadata("demo", _parse(MIXED_CSV), compact=True)
    classes = [r[0] for r in schema["classes"]["data"]]
    preds = [r[0] for r in schema["predicates"]["data"]]
    assert "https://ex.org/Arrest" in classes and "https://ex.org/Arrest" in preds
    edge = schema["edge_properties"]["OBSERVED_AT"]
    assert [p["label"] for p in edge["properties"]] == ["date"]
    node = schema["node_properties"]["data"]
    assert [(r[0], r[-1]) for r in node] == [
        ("https://ex.org/date", "https://ex.org/Observation")
    ]


def test_curated_repeats_keep_last_row_primary_and_list_the_rest():
    schema = _build_schema_from_metadata("demo", _parse(MIXED_CSV), compact=True)
    cols = schema["predicates"]["columns"]
    assert "triples" not in cols and "pattern" not in cols  # curated file
    rows = {r[0]: dict(zip(cols, r, strict=True)) for r in schema["predicates"]["data"]}
    obs = rows["https://ex.org/OBSERVED_AT"]
    assert obs["source_class"] == "https://ex.org/Frog"
    assert obs["other_pairs"] == "Bird → Location"


AURA = "http://www.projecthalo.com/aura#"

#: bio101 shapes (2026-10-15): axiom-only relations, a declared-only one, structure.
OWL_CSV = f"""\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
{AURA}has-oxidized-form,has-oxidized-form,Axiom only.,Predicate,,{AURA}Chemical-Entity,{AURA}Chemical-Entity,0,axiom
{AURA}latitude,latitude,Unused.,Predicate,,,,0,declared
http://www.w3.org/2000/01/rdf-schema#subClassOf,subClassOf,,Predicate,,http://www.w3.org/2002/07/owl#Class,http://www.w3.org/2002/07/owl#Class,27760,direct
"""


def test_pattern_guidance_for_direct_and_reified_edges():
    schema = _build_schema_from_metadata(
        "spoke-genelab", parse_entity_metadata(VOID_CSV), compact=True
    )
    edge = schema["edge_properties"]["MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"]
    assert edge["pattern"] == "direct;reified"
    assert edge["usage"] == (
        f"Also a direct triple: use `?s <{DE}> ?o` unless you need edge properties."
    )
    guide = schema["pattern_guidance"]
    assert set(guide) == {"direct;reified"}  # plain direct gets no note
    assert guide["direct;reified"]["guidance"].startswith("Stored twice, one-to-one")
    assert guide["direct;reified"]["count"] == 1
    assert "predicates" not in guide["direct;reified"]  # listed in edge_properties


def test_pattern_guidance_axiom_template_and_compact_declared():
    compact = _build_schema_from_metadata("bio101", _parse(OWL_CSV), compact=True)
    preds = [r[0] for r in compact["predicates"]["data"]]
    assert AURA + "latitude" not in preds and compact["predicates"]["count"] == 2
    guide = compact["pattern_guidance"]
    assert guide["declared"]["predicates"] == [AURA + "latitude"]
    assert "Left out of the predicates table" in guide["declared"]["guidance"]
    tmpl = guide["axiom"]["query_template"]
    assert f"?r owl:onProperty <{AURA}has-oxidized-form>" in tmpl
    assert "rdfs:subClassOf|owl:equivalentClass" in tmpl
    assert "GROUP_CONCAT(DISTINCT STR(?subject)" in tmpl  # QLever drops bare IRIs
    assert "See usage_notes" in guide["axiom"]["guidance"]  # bio101 has notes

    full = _build_schema_from_metadata("bio101", _parse(OWL_CSV), compact=False)
    assert AURA + "latitude" in [r[0] for r in full["predicates"]["data"]]
    assert "predicates" not in full["pattern_guidance"]["declared"]


def test_curated_file_gets_no_pattern_guidance():
    schema = _build_schema_from_metadata("demo", _parse(EDGE_CSV), compact=True)
    assert "pattern_guidance" not in schema
    assert "pattern" not in schema["edge_properties"]["MEASURED_EXPR"]


def test_diagram_schema_draws_void_files_by_label_with_typed_members():
    """spoke-genelab VoID shapes: IRI endpoints, literal targets, reification wiring."""
    obi = "http://purl.obolibrary.org/obo/OBI_0000070"
    bl = "https://w3id.org/biolink/vocab/"
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    csv_text = f"""\
URI,Label,Description,Type,EdgePropertyOf,SourceClass,TargetClass,Triples,Pattern
{obi},Assay,,Class,,,,13146,
{bl}Gene,Gene,,Class,,,,139719,
{STMT},Statement,,Class,,,,50235713,
{DE},DE,,Predicate,,{obi},{bl}Gene,50208066,direct;reified
{SG}symbol,symbol,,Predicate,,{bl}Gene,{XSD}string,139719,direct
{SG}taxonomy,taxonomy,,Predicate,,{bl}Gene,,138948,direct
{rdf}subject,subject,,Predicate,,{STMT},{obi},50235713,direct
{SG}log2fc,log2fc,,Predicate,{DE},{STMT},{XSD}double,50208066,
"""
    meta = parse_entity_metadata(csv_text)
    diagram = build_mermaid_diagram(
        "spoke-genelab", schema_mod.diagram_schema("spoke-genelab", meta)
    )
    assert "Assay --> MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG" in diagram
    assert "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG --> Gene" in diagram
    assert "string symbol" in diagram and "iri taxonomy" in diagram
    assert "double log2fc" in diagram
    for absent in ("OBI_0000070", "Statement", "subject", "--> string"):
        assert absent not in diagram
    assert schema_mod._is_void_metadata(meta)
    assert not schema_mod._is_void_metadata(_parse(EDGE_CSV))  # curated: old path
