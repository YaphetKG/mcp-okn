"""Tests for the VoID-derived schema builder (mcp_okn.void_schema).

The canned bindings are trimmed from the live spoke-genelab VoID description
(okn-void, 2026-10-14), so the row mapping is checked against real shapes.
run_sparql is patched on the void_schema module for the driver test.
"""

from mcp_okn import void_schema as vs

SG = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"
BL = "https://w3id.org/biolink/vocab/"
OBI = "http://purl.obolibrary.org/obo/OBI_0000070"
XSD = "http://www.w3.org/2001/XMLSchema#"
STMT = vs.RDF + "Statement"
DE = SG + "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG"

CLASSES = [
    {"cls": BL + "Gene", "entities": 139719},
    {"cls": BL + "Study", "entities": 212},
    {"cls": SG + "Mission", "entities": 42},
    {"cls": STMT, "entities": 50235722},
    {"cls": "http://rdfs.org/ns/void#Dataset", "entities": 1},
]


def _p(cls, prop, kind, n, target=None):
    row = {"cls": cls, "prop": prop, "kind": kind, "n": n}
    if target:
        row["target"] = target
    return row


PARTITIONS = [
    _p(BL + "Study", SG + "PERFORMED_SpAS", "total", 13146),
    _p(BL + "Study", SG + "PERFORMED_SpAS", "class", 13146, OBI),
    _p(BL + "Study", vs.RDF_TYPE, "total", 212),
    _p(BL + "Study", SG + "taxonomy", "total", 212),  # untyped IRI objects
    _p(SG + "Mission", SG + "start_date", "total", 42),
    _p(SG + "Mission", SG + "start_date", "datatype", 42, XSD + "date"),
    _p(SG + "Mission", "http://purl.org/pav/version", "total", 1),
    _p(STMT, vs.RDF_PREDICATE, "total", 50208066),
    _p(STMT, vs.RDF + "subject", "total", 50208066),
    _p(STMT, SG + "log2fc", "total", 50208068),
    _p(STMT, SG + "log2fc", "datatype", 50208066, XSD + "double"),
    _p(STMT, SG + "log2fc", "datatype", 2, XSD + "string"),
]


def _by(rows, uri, **kw):
    return [
        r
        for r in rows
        if r.uri == uri and all(getattr(r, k) == v for k, v in kw.items())
    ]


def test_class_rows_use_instance_counts_and_drop_provenance():
    rows = vs.class_rows(CLASSES)
    gene = _by(rows, BL + "Gene")[0]
    assert (gene.type, gene.triples) == ("Class", 139719)
    assert not _by(rows, "http://rdfs.org/ns/void#Dataset")


def test_predicate_rows_object_datatype_and_untyped_edges():
    rows = vs.predicate_rows(PARTITIONS)
    (perf,) = _by(rows, SG + "PERFORMED_SpAS")
    assert (perf.source_class, perf.target_class, perf.triples) == (
        BL + "Study",
        OBI,
        13146,
    )
    (start,) = _by(rows, SG + "start_date")
    assert (start.target_class, start.triples) == (XSD + "date", 42)
    # Untyped IRI objects: the whole partition total lands on an empty-target row.
    (tax,) = _by(rows, SG + "taxonomy")
    assert (tax.target_class, tax.triples) == ("", 212)


def test_predicate_rows_exclude_rdf_type_and_provenance():
    rows = vs.predicate_rows(PARTITIONS)
    assert not _by(rows, vs.RDF_TYPE)
    assert not _by(rows, "http://purl.org/pav/version")


def test_dataset_only_predicate_gets_unscoped_row():
    rows = vs.predicate_rows(PARTITIONS, [{"prop": SG + "orphan", "n": 7}])
    (orphan,) = _by(rows, SG + "orphan")
    assert (orphan.source_class, orphan.target_class, orphan.triples) == ("", "", 7)


def test_shortnames_from_datasets_skips_partition_nodes_and_excluded():
    rows = [
        {"ds": "https://purl.org/okn/frink/kg/prokn"},
        {"ds": "https://purl.org/okn/frink/kg/prokn/class/abc"},
        {"ds": "https://purl.org/okn/frink/kg/semopenalex"},
    ]
    assert vs.shortnames_from_datasets(rows) == ["prokn"]


def test_edge_property_rows_from_exact_pair_counts():
    reified = {DE: 50208066, SG + "MetaRelationship": 9}
    pairs = {(DE, SG + "log2fc"): 50208066, (DE, vs.RDF + "subject"): 50208066}
    rows, notes = vs.edge_property_rows(PARTITIONS, reified, pairs)
    (log2fc,) = rows  # scaffolding (rdf:subject) is not an edge property
    assert log2fc.uri == SG + "log2fc"
    assert log2fc.edge_property_of == DE
    assert log2fc.source_class == STMT
    # Dominant datatype wins over the pooled minority xsd:string.
    assert log2fc.target_class == XSD + "double"
    assert log2fc.triples == 50208066
    assert notes == []


def test_single_reified_predicate_uses_void_totals():
    rows, _ = vs.edge_property_rows(PARTITIONS, {DE: 50208066}, None)
    assert [(r.uri, r.edge_property_of, r.triples) for r in rows] == [
        (SG + "log2fc", DE, 50208068)
    ]


def test_sampled_fallback_leaves_shared_property_count_blank():
    reified = {DE: 1, SG + "OTHER": 1}
    sampled = {DE: {SG + "log2fc"}, SG + "OTHER": {SG + "log2fc"}}
    rows, notes = vs.edge_property_rows(PARTITIONS, reified, None, sampled)
    assert {r.triples for r in rows} == {None}
    assert len(notes) == 2


def test_aggregated_reifier_rows_replaced_by_edge_rows():
    preds = vs.predicate_rows(PARTITIONS)
    edge_rows, _ = vs.edge_property_rows(PARTITIONS, {DE: 1}, None)
    merged = vs.drop_aggregated_edge_rows(preds, edge_rows, [STMT])
    assert not [r for r in merged if r.uri == SG + "log2fc"]
    assert _by(merged, vs.RDF + "subject")  # scaffolding rows stay


def test_reified_only_rows_fallback_without_classes():
    (row,) = vs.reified_only_rows(SG + "R", [], 5)
    assert (row.source_class, row.target_class, row.triples) == ("", "", 5)


AURA = "http://www.projecthalo.com/aura#"


def test_axiom_property_rows_cover_owl_relations_void_cannot_see():
    """bio101 (live, 2026-10-15): has-oxidized-form has 0 triples, 14 restrictions."""
    axioms = [
        {"prop": AURA + "has-oxidized-form", "n": 14},
        {"prop": AURA + "has-part", "n": 1},
        {"prop": AURA + "in-concept", "n": 3},  # also asserted directly
    ]
    declared = [
        {
            "prop": AURA + "has-oxidized-form",
            "domain": AURA + "Chemical-Entity",
            "range": AURA + "Chemical-Entity",
        },
        {"prop": AURA + "latitude"},  # declared, never used
        {"prop": vs.RDF_TYPE},
    ]
    rows = vs.axiom_property_rows(axioms, declared, {AURA + "in-concept"})
    assert [r.uri for r in rows] == [
        AURA + "has-oxidized-form",
        AURA + "has-part",
        AURA + "latitude",
    ]
    ox, part, lat = rows
    assert (ox.source_class, ox.target_class, ox.triples) == (
        AURA + "Chemical-Entity",
        AURA + "Chemical-Entity",
        0,
    )
    assert "owl:onProperty of 14 owl:Restrictions" in ox.note
    assert "of 1 owl:Restriction;" in part.note
    assert (lat.source_class, lat.triples) == ("", 0)
    assert (ox.pattern, part.pattern, lat.pattern) == ("axiom", "axiom", "declared")
    assert lat.note.startswith("Declared in the schema")


def test_apply_text_appends_usage_note_once():
    row = vs.SchemaRow(AURA + "has-oxidized-form", "Predicate", note="Axiom only.")
    text = {row.uri: {"description": "Relates a chemical to its oxidized state."}}
    vs.apply_text([row], text)
    vs.apply_text([row], text)
    assert row.description == "Relates a chemical to its oxidized state. Axiom only."


async def test_build_kg_schema_adds_owl_axiom_properties(monkeypatch):
    async def fake(q, client=None, **kw):
        if "void:entities" in q:
            return {"rows": [{"cls": vs.OWL + "Restriction", "entities": 15}]}
        if 'BIND("total" AS ?kind)' in q:
            return {
                "rows": [_p(vs.OWL + "Restriction", vs.OWL_ON_PROPERTY, "total", 15)]
            }
        if "void:propertyPartition" in q:
            return {"rows": [{"prop": vs.OWL_ON_PROPERTY, "n": 15}]}
        if "owl:onProperty ?prop" in q:
            return {"rows": [{"prop": AURA + "has-oxidized-form", "n": 14}]}
        if "rdfs:domain" in q:
            return {"rows": [{"prop": AURA + "has-oxidized-form"}]}
        if "VALUES ?u" in q:
            return {"rows": []}
        raise AssertionError(q)

    monkeypatch.setattr(vs, "run_sparql", fake)
    rows, notes = await vs.build_kg_schema("bio101", log=lambda _m: None)
    (ox,) = _by(rows, AURA + "has-oxidized-form")
    assert (ox.type, ox.triples, ox.label) == ("Predicate", 0, "has-oxidized-form")
    assert ox.pattern == "axiom"
    assert "never asserted as a direct triple" in ox.description
    assert notes == []


def test_text_fallback_order_kg_then_ontology_then_local_name():
    rows = [
        vs.SchemaRow(OBI, "Class"),
        vs.SchemaRow(BL + "Gene", "Class"),
        vs.SchemaRow(SG + "Mission", "Class"),
    ]
    kg_text = {SG + "Mission": {"label": "Mission", "description": "A mission."}}
    obo = {OBI: {"label": "assay", "description": "A planned process."}}
    vs.apply_text(rows, kg_text, obo)
    assert (rows[0].label, rows[0].description) == (
        "assay",
        "A planned process. (source: OBI via ubergraph)",
    )
    assert (rows[1].label, rows[1].description) == ("Gene", "")
    assert rows[2].description == "A mission."


def test_pick_text_prefers_rdfs_comment_and_cleans_whitespace():
    rdfs = "http://www.w3.org/2000/01/rdf-schema#"
    skos = "http://www.w3.org/2004/02/skos/core#definition"
    got = vs.pick_text(
        [
            {"u": "u1", "p": skos, "o": "skos def"},
            {"u": "u1", "p": rdfs + "comment", "o": " the\n comment "},
            {"u": "u1", "p": rdfs + "label", "o": "U one"},
        ]
    )
    assert got == {"u1": {"label": "U one", "description": "the comment"}}


def test_text_lookup_query_filters_literals_and_batches_values():
    q = vs.text_lookup_query(
        "https://purl.org/okn/frink/kg/x", ["http://a", "http://b"]
    )
    assert "VALUES ?u { <http://a> <http://b> }" in q
    assert "isLiteral(?o)" in q


def test_validate_rows_flags_bad_type_and_triples():
    rec = dict.fromkeys(vs.COLUMNS, "")
    good = {**rec, "URI": "u", "Type": "Class", "Triples": "3"}
    bad = {**rec, "URI": "u", "Type": "NodeProperty", "Triples": "x"}
    assert vs.validate_rows([good], vs.COLUMNS) == []
    problems = vs.validate_rows([bad], vs.COLUMNS)
    assert any("Type" in p for p in problems)
    assert any("Triples" in p for p in problems)


# ------------------------------------------------------------------ comparison

CURATED = [
    {
        "URI": OBI,
        "Label": "Assay",
        "Description": "Unique identifier for an assay",
        "Type": "Class",
    },
    {"URI": BL + "Gene", "Label": "Gene", "Description": "A gene", "Type": "Class"},
    {
        "URI": DE,
        "Label": "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG",
        "Description": "Assay measured DE",
        "Type": "Predicate",
        "SourceClass": "Assay",
        "TargetClass": "Gene",
    },
    {
        "URI": SG + "group_mean_1",
        "Label": "group_mean_1",
        "Description": "Mean expression level of the gene in the first experimental group (float)",
        "Type": "EdgeProperty",
        "EdgePropertyOf": "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG",
    },
    {
        "URI": SG + "phantom",
        "Label": "phantom",
        "Description": "Never loaded",
        "Type": "NodeProperty",
        "SourceClass": "Gene",
    },
    {"URI": "http://rdfs.org/ns/void#triples", "Label": "triples", "Type": "Predicate"},
]


def _new(uri, type_, label="", desc="", edge_of="", src="", tgt="", n="1"):
    return {
        "URI": uri,
        "Label": label or vs.local_label(uri),
        "Description": desc,
        "Type": type_,
        "EdgePropertyOf": edge_of,
        "SourceClass": src,
        "TargetClass": tgt,
        "Triples": n,
    }


NEW = [
    _new(OBI, "Class", "assay", "A planned process."),
    _new(BL + "Gene", "Class", desc="A gene"),
    _new(STMT, "Class"),
    _new(DE, "Predicate", src=OBI, tgt=BL + "Gene"),
    _new(SG + "group_mean_1", "Predicate", edge_of=DE, src=STMT, tgt=XSD + "double"),
]


def test_normalize_curated_resolves_labels_and_folds_types():
    entries, unresolved = vs.normalize_curated(CURATED)
    by_uri = {e.uri: e for e in entries}
    assert "http://rdfs.org/ns/void#triples" not in by_uri  # provenance dropped
    assert by_uri[DE].sources == [OBI] and by_uri[DE].targets == [BL + "Gene"]
    gm = by_uri[SG + "group_mean_1"]
    assert (gm.type, gm.original_type, gm.edge_property_of) == (
        "Predicate",
        "EdgeProperty",
        DE,
    )
    assert unresolved == []


def test_compare_structure():
    r = vs.compare_with_curated(NEW, CURATED)
    assert r["classes"]["only_new"] == [STMT]
    assert r["predicates"]["only_curated"] == [SG + "phantom"]
    assert r["edges"]["only_new"] == [] and r["edges"]["only_curated"] == []
    assert r["edge_properties"]["only_new"] == [] and r["edge_properties"]["new"] == 1


def test_compare_text_categories_and_manual_definitions():
    r = vs.compare_with_curated(NEW, CURATED)
    status = {
        (t["uri"], t["edge_property_of"]): t["description_status"] for t in r["text"]
    }
    assert status[(BL + "Gene", "")] == "match"
    assert status[(OBI, "")] == "differs"
    assert status[(SG + "group_mean_1", DE)] == "curated-only"
    assert status[(SG + "phantom", "")] == vs.NOT_IN_VOID
    manual = vs.manual_definitions("spoke-genelab", r["text"])
    uris = {(m[1], m[5]) for m in manual}
    assert uris == {
        (DE, "curated-only"),
        (SG + "group_mean_1", "curated-only"),
        (SG + "phantom", vs.NOT_IN_VOID),
    }
    gm = next(m for m in manual if m[1] == SG + "group_mean_1")
    assert gm[2] == DE and gm[4].startswith("Mean expression level")


def test_label_that_is_only_the_local_name_counts_as_curated_only():
    r = vs.compare_with_curated(NEW, CURATED)
    labels = {t["uri"]: t["label_status"] for t in r["text"]}
    assert labels[OBI] == "match"  # "assay" vs "Assay" — case-insensitive
    assert labels[DE] == "match"


async def test_build_kg_schema_driver_end_to_end(monkeypatch):
    """The driver stitches VoID + live edge counts + text lookups into one row set."""

    async def fake(q, client=None, **kw):
        if "void:entities" in q:
            return {"rows": CLASSES}
        if 'BIND("total" AS ?kind)' in q:
            return {"rows": PARTITIONS}
        if "<https://purl.org/okn/frink/kg/spoke-genelab> void:propertyPartition" in q:
            return {"rows": [{"prop": vs.RDF_PREDICATE, "n": 50208066}]}
        if "GROUP BY ?pred ?prop" in q:
            return {"rows": [{"pred": DE, "prop": SG + "log2fc", "n": 50208066}]}
        if "GROUP BY ?pred" in q:
            return {"rows": [{"pred": DE, "n": 50208066}, {"pred": SG + "R", "n": 9}]}
        if "GROUP BY ?sc ?oc" in q:
            return {"rows": [{"sc": BL + "Gene", "oc": BL + "Gene", "n": 9}]}
        if "VALUES ?u" in q:
            return {"rows": []}
        raise AssertionError(q)

    monkeypatch.setattr(vs, "run_sparql", fake)
    rows, notes = await vs.build_kg_schema("spoke-genelab", log=lambda _m: None)
    (edge,) = [r for r in rows if r.edge_property_of]
    assert (edge.uri, edge.triples) == (SG + "log2fc", 50208066)
    (reified_only,) = _by(rows, SG + "R")
    assert (reified_only.source_class, reified_only.triples) == (BL + "Gene", 9)
    assert reified_only.pattern == "reified"
    assert {r.pattern for r in _by(rows, SG + "PERFORMED_SpAS")} == {"direct"}
    assert edge.pattern == "" and all(not r.pattern for r in rows if r.type == "Class")
    assert all(r.label for r in rows)
    assert notes == []


async def test_check_freshness_flags_void_that_describes_another_release(monkeypatch):
    async def fake(q, client=None, **kw):
        if "void:triples ?triples" in q:
            return {"rows": [{"triples": 1820793, "version": "v0.0.4"}]}
        return {"rows": [{"n": 1215057}]}

    monkeypatch.setattr(vs, "run_sparql", fake)
    got = await vs.check_freshness("biomarkerkg")
    assert (got["void_triples"], got["served_triples"], got["matches"]) == (
        1820793,
        1215057,
        False,
    )


async def test_check_freshness_unknown_when_count_times_out(monkeypatch):
    async def fake(q, client=None, **kw):
        if "void:triples ?triples" in q:
            return {"rows": [{"triples": 10}]}
        raise vs.SparqlError("timed out")

    monkeypatch.setattr(vs, "run_sparql", fake)
    got = await vs.check_freshness("ubergraph")
    assert got["matches"] is None and "timed out" in got["error"]


def test_add_patterns_marks_direct_predicates_also_reified_or_in_axioms():
    """spoke-genelab's expression edge: 50,208,066 asserted triples AND statements."""
    rows = [
        vs.SchemaRow(DE, "Predicate", pattern="direct"),
        vs.SchemaRow(AURA + "in-concept", "Predicate", pattern="direct"),
        vs.SchemaRow(SG + "log2fc", "Predicate", edge_property_of=DE),
        vs.SchemaRow(BL + "Gene", "Class"),
    ]
    vs.add_patterns(rows, {DE: 50208066}, {AURA + "in-concept": 3})
    assert [r.pattern for r in rows] == ["direct;reified", "direct;axiom", "", ""]
    assert (
        rows[1].note
        == "Also used inside class axioms, as owl:onProperty of 3 owl:Restrictions."
    )


def test_validate_rows_flags_unknown_pattern():
    rec = dict.fromkeys(vs.COLUMNS, "")
    ok = {**rec, "URI": "u", "Type": "Predicate", "Pattern": "direct;reified"}
    bad = {**rec, "URI": "u", "Type": "Predicate", "Pattern": "direct;edge"}
    assert vs.validate_rows([ok], vs.COLUMNS) == []
    assert any("Pattern" in p for p in vs.validate_rows([bad], vs.COLUMNS))


def test_drop_excluded_removes_spoke_genelab_meta_layer():
    """Shapes from spoke-genelab (2026-10-15): 9 MetaNodes, 9 MetaRelationship statements."""
    meta_node, meta_rel = SG + "MetaNode", SG + "MetaRelationship"
    rows = [
        vs.SchemaRow(meta_node, "Class", triples=9),
        vs.SchemaRow(STMT, "Class", triples=50235722),
        vs.SchemaRow(BL + "Gene", "Class", triples=139719),
        vs.SchemaRow(
            meta_rel,
            "Predicate",
            source_class=meta_node,
            target_class=meta_node,
            triples=9,
        ),
        vs.SchemaRow(SG + "chromosome", "Predicate", source_class=meta_node, triples=1),
        vs.SchemaRow(
            SG + "chromosome", "Predicate", source_class=BL + "Gene", triples=5
        ),
        vs.SchemaRow(
            vs.RDF + "subject",
            "Predicate",
            source_class=STMT,
            target_class=meta_node,
            triples=9,
        ),
        vs.SchemaRow(
            vs.RDF + "subject",
            "Predicate",
            source_class=STMT,
            target_class=OBI,
            triples=50235713,
        ),
        vs.SchemaRow(
            vs.RDF_PREDICATE, "Predicate", source_class=STMT, triples=50235722
        ),
        vs.SchemaRow(SG + "from", "Predicate", edge_property_of=meta_rel, triples=9),
        vs.SchemaRow(SG + "log2fc", "Predicate", edge_property_of=DE, triples=50208066),
    ]
    kept = vs.drop_excluded(
        rows,
        vs.EXCLUDED_SCHEMA_CLASSES["spoke-genelab"],
        vs.EXCLUDED_SCHEMA_PREDICATES["spoke-genelab"],
        {DE: 50208066, meta_rel: 9},
    )
    assert [(r.uri.rsplit("/", 1)[-1], r.triples) for r in kept] == [
        ("22-rdf-syntax-ns#Statement", 50235713),
        ("Gene", 139719),
        ("chromosome", 5),
        ("22-rdf-syntax-ns#subject", 50235713),
        ("22-rdf-syntax-ns#predicate", 50235713),
        ("log2fc", 50208066),
    ]
