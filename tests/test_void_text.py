"""Tests for the Label/Description fill (mcp_okn.void_text).

Shapes come from the 2026-10-16 VoID files and their curated proto-okn
counterparts (bio101, spoke-genelab, securechainkg/sudokn, ubergraph).
"""

from mcp_okn import void_text as vt

AURA = "http://www.projecthalo.com/aura#"
SG = "https://purl.org/okn/frink/kg/spoke-genelab/schema/"
SUD = "http://asu.edu/semantics/SUDOKN/"
OWL = "http://www.w3.org/2002/07/owl#"
KG = "https://purl.org/okn/frink/kg/"

NOTE = (
    "Used only inside class axioms, as owl:onProperty of 14 owl:Restrictions; "
    "never asserted as a direct triple."
)


def _row(uri, type_="Predicate", label="", desc="", parent=""):
    return {
        "URI": uri,
        "Label": label or uri.rsplit("#", 1)[-1].rsplit("/", 1)[-1],
        "Description": desc,
        "Type": type_,
        "EdgePropertyOf": parent,
    }


def _curated(*rows):
    cols = ["URI", "Label", "Description", "Type", "EdgePropertyOf"]
    return [dict(zip(cols, r, strict=True)) for r in rows]


def test_split_note_and_rejoin():
    text, note = vt.split_note(f"Relates a chemical to its oxidized state. {NOTE}")
    assert (text, note) == ("Relates a chemical to its oxidized state.", NOTE)
    assert vt.split_note(NOTE) == ("", NOTE)
    assert vt.split_note("Plain text.") == ("Plain text.", "")
    assert vt.join_text("A relation.", NOTE) == f"A relation. {NOTE}"
    # Curated text that already states the usage is not repeated.
    curated = "A relation. Used only inside class axioms, as owl:onProperty of 14."
    assert vt.join_text(curated, NOTE) == curated


def test_curated_wins_and_keeps_the_usage_note():
    index = vt.curated_index(
        _curated(
            (
                AURA + "has-oxidized-form",
                "has oxidized form",
                "Curated text.",
                "Predicate",
                "",
            )
        )
    )
    row = _row(AURA + "has-oxidized-form", desc=f"KG text. {NOTE}")
    rep = vt.fill_records([row], index, {})
    assert row["Label"] == "has oxidized form"
    assert row["Description"] == f"Curated text. {NOTE}"
    assert rep.sources["curated"] == 1 and rep.labels["curated"] == 1


def test_edge_property_description_matches_its_parent_relationship():
    de, ab = SG + "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG", SG + "MEASURED_ABUNDANCE"
    index = vt.curated_index(
        _curated(
            (de, "DE", "Expression edge.", "Predicate", ""),
            (ab, "AB", "Abundance edge.", "Predicate", ""),
            (
                SG + "adj_p_value",
                "adj_p_value",
                "FDR of the gene.",
                "EdgeProperty",
                "MEASURED_DIFFERENTIAL_EXPRESSION_ASmMG",
            ),
            (
                SG + "adj_p_value",
                "adj_p_value",
                "FDR of the organism.",
                "EdgeProperty",
                "MEASURED_ABUNDANCE",
            ),
        )
    )
    rows = [_row(SG + "adj_p_value", parent=de), _row(SG + "adj_p_value", parent=ab)]
    vt.fill_records(rows, index, {})
    assert [r["Description"] for r in rows] == [
        "FDR of the gene.",
        "FDR of the organism.",
    ]


def test_existing_text_is_preserved_and_ontology_text_is_tagged():
    rows = [
        _row(SUD + "Org", desc="The KG's own definition."),
        _row(OWL + "onProperty"),
        _row(SUD + "WireDrawingCapability"),
        _row(AURA + "Day-Constant", type_="Class"),
    ]
    hits = {
        SUD + "Org": vt.TextHit(description="Should not be used.", source="sudokn KG"),
        OWL + "onProperty": vt.TextHit(
            "onProperty", "The property that determines the class.", "OWL"
        ),
        SUD + "WireDrawingCapability": vt.TextHit(
            "Wire Drawing Capability", "Drawing wire.", "sudokn KG"
        ),
    }
    rep = vt.fill_records(rows, {}, hits)
    assert rows[0]["Description"] == "The KG's own definition."
    assert rows[1]["Description"] == (
        "The property that determines the class. (source: OWL)"
    )
    assert rows[2]["Label"] == "Wire Drawing Capability"
    assert rows[2]["Description"] == "Drawing wire. (source: sudokn KG)"
    # Nothing reliable: left empty, label stays the local name, and it is reported.
    assert (rows[3]["Label"], rows[3]["Description"]) == ("Day-Constant", "")
    assert rep.unfilled == [
        {
            "URI": AURA + "Day-Constant",
            "Type": "Class",
            "EdgePropertyOf": "",
            "Label": "Day-Constant",
        }
    ]
    assert dict(rep.sources) == {"existing": 1, "ontology": 2, "unfilled": 1}


def test_axiom_note_survives_an_ontology_fill_and_unfilled_keeps_it():
    rows = [_row(AURA + "x", desc=NOTE), _row(AURA + "y", desc=NOTE)]
    hits = {AURA + "x": vt.TextHit(description="Meaning.", source="RO via OLS")}
    rep = vt.fill_records(rows, {}, hits)
    assert rows[0]["Description"] == f"Meaning. (source: RO via OLS) {NOTE}"
    assert rows[1]["Description"] == NOTE  # untouched, but reported
    assert rep.sources["unfilled"] == 1


def test_restriction_count_mismatch_is_reported():
    index = vt.curated_index(
        _curated(
            (
                AURA + "p",
                "p",
                "X. Used inside axioms, as owl:onProperty of 12 owl:Restrictions.",
                "Predicate",
                "",
            )
        )
    )
    rep = vt.fill_records([_row(AURA + "p", desc=f"KG. {NOTE}")], index, {})
    assert rep.count_mismatches == [
        f"{AURA}p: curated says 12 restrictions, the served graph has 14"
    ]


def test_needs_lookup_skips_curated_and_described_rows():
    index = vt.curated_index(_curated((SUD + "A", "A label", "A desc.", "Class", "")))
    rows = [
        _row(SUD + "A", type_="Class"),
        _row(SUD + "B", type_="Class", label="Real label", desc="Has text."),
        _row(SUD + "C", type_="Class"),
        _row(SUD + "D", type_="Class", desc="Text but a local-name label."),
    ]
    assert vt.needs_lookup(rows, index) == {SUD + "C", SUD + "D"}


def test_pick_federation_hits_prefers_own_graph_then_ubergraph():
    obo = "http://purl.obolibrary.org/obo/RO_0002211"
    rows = [
        {
            "u": obo,
            "g": KG + "sawgraph",
            "p": "http://www.w3.org/2000/01/rdf-schema#comment",
            "o": "Saw copy.",
        },
        {
            "u": obo,
            "g": KG + "ubergraph",
            "p": "http://purl.obolibrary.org/obo/IAO_0000115",
            "o": "Regulates.",
        },
        {
            "u": SUD + "X",
            "g": KG + "sudokn",
            "p": "http://www.w3.org/2000/01/rdf-schema#comment",
            "o": "  Own   text. ",
        },
        {
            "u": SUD + "X",
            "g": KG + "sudokn",
            "p": "http://www.w3.org/2000/01/rdf-schema#label",
            "o": "X label",
        },
    ]
    hits = vt.pick_federation_hits(rows, {obo: KG + "prokn", SUD + "X": KG + "sudokn"})
    assert (hits[obo].description, hits[obo].source) == (
        "Regulates.",
        "RO via ubergraph",
    )
    assert (
        hits[SUD + "X"].label,
        hits[SUD + "X"].description,
        hits[SUD + "X"].source,
    ) == (
        "X label",
        "Own text.",
        "",
    )


def test_pick_ols_hit_uses_defining_ontology_and_tags_only_descriptions():
    hit = vt.pick_ols_hit(
        {
            "terms": [],
            "properties": [
                {
                    "label": "start, dpf",
                    "ontology_prefix": "zfs",
                    "is_defining_ontology": False,
                    "description": ["Wrong one."],
                },
                {
                    "label": "start, days post fertilization",
                    "ontology_prefix": "MmusDv",
                    "is_defining_ontology": True,
                    "description": ["Count of days."],
                },
            ],
        }
    )
    assert hit == vt.TextHit(
        "start, days post fertilization", "Count of days.", "MMUSDV via OLS"
    )
    bare = vt.pick_ols_hit(
        {
            "terms": [
                {
                    "label": "perch family",
                    "ontology_prefix": "FOODON",
                    "description": [],
                }
            ]
        }
    )
    assert bare == vt.TextHit("perch family", "", "")
    assert vt.pick_ols_hit({}) is None


def test_curated_id_only_label_does_not_replace_a_real_label():
    ncit = "http://purl.obolibrary.org/obo/NCIT_C48192"
    ro = "http://purl.obolibrary.org/obo/RO_0000056"
    index = vt.curated_index(
        _curated(
            (ncit, "NCIT C48192", "", "Class", ""),
            (ro, "Participates In", "", "Predicate", ""),
            (SUD + "AutomotiveIndustry", "Automotive Industry", "", "Class", ""),
        )
    )
    rows = [
        _row(ncit, type_="Class", label="Importance Weight"),
        _row(ro, label="participates in"),
        _row(SUD + "AutomotiveIndustry", type_="Class", label="Automotive"),
        _row("http://purl.obolibrary.org/obo/NCIT_C1", type_="Class"),
    ]
    vt.fill_records(rows, index, {})
    assert [r["Label"] for r in rows] == [
        "Importance Weight",  # real name kept over the id spelling
        "Participates In",  # curated wins otherwise
        "Automotive Industry",
        "NCIT_C1",
    ]
    assert vt.id_only_label("MMO 0000000", "http://purl.obolibrary.org/obo/MMO_0000000")
    assert not vt.id_only_label("Automotive Industry", SUD + "AutomotiveIndustry")
