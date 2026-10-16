# VoID-derived schemas vs curated proto-okn schemas

Generated 2026-10-15 by `scripts/build_void_schema.py`. 44 VoID-derived file(s) in this directory; 40 have a curated counterpart in `sbl-sdsc/mcp-proto-okn/metadata/entities/`.

How to read this:

- Curated files are normalized before comparing: Source/TargetClass labels → class URIs (via the file's own Class rows), EdgePropertyOf short names → predicate URIs, `EdgeProperty`/`NodeProperty` → `Predicate`.
- **only VoID**: in the served graph but missing from the curated file. **only curated**: in the curated file but not in the served graph (phantom, renamed, or not yet deployed).
- **Edges only curated** over-reports: a curated predicate row holds `|`-joined source and target lists with no pairing, so it is expanded as every source × target combination, some of which the curators never meant (e.g. oard-kg `subject`). Use it to find candidates, not as a list of errors; VoID's per-edge rows give the real pairings with counts.
- Description status per curated row: `match` (same text as the KG/ubergraph), `differs`, `curated-only` (entity is served but no machine source describes it — hand-written), `machine-only`, `not-in-void` (entity not served).
- `manual_definitions.csv` holds the 3901 `curated-only` / `not-in-void` descriptions — the knowledge VoID cannot reproduce.
- Class counts in the VoID files are instance counts (`void:entities`); predicate counts are triples per (source class, predicate, target) edge.
- URIs below are shortened: `kg:` = the KG's own `https://purl.org/okn/frink/kg/{kg}/` namespace; `rdf:` = `http://www.w3.org/1999/02/22-rdf-syntax-ns#`, `rdfs:` = `http://www.w3.org/2000/01/rdf-schema#`, `xsd:` = `http://www.w3.org/2001/XMLSchema#`, `owl:` = `http://www.w3.org/2002/07/owl#`, `skos:` = `http://www.w3.org/2004/02/skos/core#`, `obo:` = `http://purl.obolibrary.org/obo/`, `biolink:` = `https://w3id.org/biolink/vocab/`, `schema:` = `http://schema.org/`, `dct:` = `http://purl.org/dc/terms/`. `comparison.json` has full URIs and uncapped lists.

## Coverage

- Skipped as too large: `wikidata` (683,972 edges)
- VoID file but no curated file: `babel`, `identifier-mappings`, `maudekg`, `ubergraph`

## VoID freshness

VoID is only trustworthy for a KG when it describes the graph actually served. Each KG's `void:triples` is compared with a live `COUNT(*)` of its named graph.

- Checked: 44; match: 37; **stale: 7**; unknown (count timed out): 0

| KG | VoID version | VoID updated | void:triples | served triples |
|---|---|---|---|---|
| biomarkerkg | v0.0.4 | 2026-10-09T14:03:28.536+00:00 | 1,820,793 | 1,215,057 |
| dreamkg | v0.0.5 | 2026-05-13T17:06:32.947+00:00 | 94,780 | 94,778 |
| maudekg | v0.0.2 | 2026-06-29T17:55:24.277+00:00 | 95,913 | 0 |
| nikg | v0.0.6 | 2026-03-16T00:38:01.139+00:00 | 174,613 | 1,338,339 |
| sawgraph | v0.0.16 | 2026-08-28T20:27:40.089+00:00 | 161,265,076 | 161,264,797 |
| securechainkg | v0.0.11 | 2026-03-23T20:04:56.930+00:00 | 75,238,886 | 75,238,585 |
| spatialkg | v0.0.6 | 2026-08-10T18:04:25.686+00:00 | 437,177,601 | 429,771,869 |

Treat the structural diff for a stale KG with suspicion: VoID may describe a different release than the curated file and the served graph.

## Summary

| KG | classes VoID / cur | only VoID | only cur | predicates VoID / cur | only VoID | only cur | edge props VoID / cur | desc match | desc differs | desc curated-only | desc machine-only | desc not-in-void |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bio101 | 127 / 105 | 118 | 96 | 381 / 382 | 0 | 1 | 0 / 0 | 52 | 307 | 31 | 0 | 97 |
| biobricks-aopwiki | 24 / 24 | 0 | 0 | 59 / 62 | 0 | 3 | 0 / 0 | 32 | 4 | 31 | 8 | 3 |
| biobricks-ice | 10 / 10 | 0 | 0 | 20 / 21 | 0 | 1 | 0 / 0 | 0 | 4 | 26 | 0 | 1 |
| biobricks-mesh | 22 / 21 | 4 | 3 | 63 / 68 | 5 | 10 | 0 / 0 | 58 | 4 | 14 | 0 | 13 |
| biobricks-pubchem-annotations | 1 / 1 | 0 | 0 | 5 / 6 | 0 | 1 | 0 / 0 | 0 | 0 | 6 | 0 | 1 |
| biobricks-tox21 | 1 / 1 | 0 | 0 | 2 / 3 | 0 | 1 | 0 / 0 | 0 | 0 | 3 | 0 | 1 |
| biobricks-toxcast | 7 / 7 | 0 | 0 | 10 / 11 | 0 | 1 | 0 / 0 | 0 | 4 | 13 | 0 | 1 |
| biohealth | 2 / 2 | 0 | 0 | 70 / 70 | 0 | 0 | 64 / 0 | 0 | 0 | 72 | 0 | 0 |
| biomarkerkg ⚠ stale | 7 / 7 | 0 | 0 | 12 / 12 | 10 | 10 | 0 / 0 | 0 | 0 | 9 | 0 | 10 |
| climatemodelskg | 52 / 51 | 4 | 3 | 144 / 137 | 7 | 0 | 0 / 0 | 381 | 0 | 20 | 0 | 3 |
| digcfdekg | 16 / 13 | 3 | 0 | 16 / 16 | 0 | 0 | 30 / 0 | 0 | 0 | 29 | 0 | 0 |
| dreamkg ⚠ stale | 14 / 13 | 5 | 4 | 53 / 40 | 14 | 1 | 0 / 0 | 0 | 6 | 42 | 0 | 5 |
| evoweb | 1 / 1 | 0 | 0 | 4 / 4 | 0 | 0 | 0 / 0 | 0 | 0 | 5 | 0 | 0 |
| fiokg | 109 / 89 | 23 | 3 | 109 / 44 | 65 | 0 | 0 / 0 | 41 | 5 | 88 | 0 | 3 |
| gene-expression-atlas-okn | 16 / 16 | 0 | 0 | 27 / 27 | 0 | 0 | 0 / 0 | 0 | 0 | 41 | 0 | 0 |
| geoconnex | 79 / 79 | 0 | 0 | 88 / 88 | 0 | 0 | 0 / 0 | 0 | 0 | 336 | 0 | 0 |
| glygenkg | 15 / 15 | 0 | 0 | 45 / 45 | 0 | 0 | 0 / 0 | 0 | 0 | 67 | 0 | 0 |
| hydrologykg | 127 / 127 | 28 | 28 | 180 / 106 | 74 | 0 | 0 / 0 | 11 | 79 | 200 | 0 | 28 |
| medical-device-kg | 36 / 66 | 1 | 31 | 163 / 315 | 0 | 152 | 0 / 0 | 0 | 0 | 388 | 0 | 183 |
| nasa-gesdisc-kg | 10 / 10 | 0 | 0 | 41 / 41 | 0 | 0 | 5 / 3 | 0 | 0 | 51 | 0 | 0 |
| ncipidkg | 7 / 6 | 1 | 0 | 20 / 20 | 0 | 0 | 16 / 16 | 0 | 45 | 39 | 0 | 0 |
| nde | 7 / 10 | 0 | 3 | 29 / 29 | 0 | 0 | 0 / 0 | 0 | 0 | 36 | 0 | 3 |
| nestkg | 11 / 9 | 2 | 0 | 34 / 34 | 0 | 0 | 2 / 2 | 7 | 0 | 36 | 0 | 0 |
| nikg ⚠ stale | 5 / 7 | 1 | 3 | 10 / 18 | 2 | 10 | 0 / 0 | 0 | 0 | 12 | 0 | 13 |
| oard-kg | 9 / 9 | 0 | 0 | 16 / 16 | 0 | 0 | 0 / 9 | 0 | 0 | 25 | 0 | 0 |
| pankgraph | 13 / 13 | 0 | 0 | 102 / 102 | 0 | 0 | 85 / 82 | 0 | 3 | 112 | 0 | 0 |
| phaseskg | 14 / 92 | 2 | 80 | 145 / 90 | 55 | 0 | 0 / 0 | 4 | 42 | 56 | 0 | 80 |
| prokn | 41 / 41 | 0 | 0 | 217 / 218 | 0 | 1 | 208 / 13 | 71 | 9 | 208 | 0 | 1 |
| rdkg | 13 / 11 | 2 | 0 | 21 / 21 | 0 | 0 | 0 / 0 | 0 | 7 | 25 | 0 | 0 |
| ruralkg | 20 / 244 | 3 | 227 | 84 / 86 | 2 | 4 | 0 / 0 | 1 | 16 | 145 | 0 | 231 |
| sawgraph ⚠ stale | 416 / 194 | 239 | 17 | 266 / 146 | 121 | 1 | 0 / 0 | 63 | 42 | 236 | 0 | 17 |
| scales | 31 / 34 | 2 | 5 | 288 / 293 | 4 | 9 | 0 / 0 | 572 | 29 | 16 | 0 | 8 |
| securechainkg ⚠ stale | 898 / 22 | 876 | 0 | 49 / 42 | 7 | 0 | 0 / 0 | 0 | 0 | 109 | 0 | 0 |
| sockg | 90 / 105 | 0 | 15 | 109 / 106 | 3 | 0 | 0 / 0 | 3 | 0 | 193 | 0 | 15 |
| spatialkg ⚠ stale | 25 / 15 | 16 | 6 | 53 / 23 | 30 | 0 | 0 / 0 | 0 | 9 | 55 | 0 | 6 |
| spoke-genelab | 9 / 8 | 1 | 0 | 55 / 50 | 5 | 0 | 20 / 20 | 0 | 1 | 70 | 0 | 0 |
| spoke-okn | 8 / 8 | 0 | 0 | 127 / 127 | 1 | 1 | 74 / 41 | 0 | 0 | 134 | 0 | 1 |
| sudokn | 822 / 56 | 782 | 16 | 73 / 37 | 36 | 0 | 0 / 0 | 0 | 15 | 72 | 0 | 16 |
| ufokn | 6 / 6 | 0 | 0 | 17 / 17 | 0 | 0 | 0 / 0 | 0 | 0 | 23 | 0 | 0 |
| wildlifekn | 15 / 15 | 0 | 0 | 48 / 48 | 0 | 0 | 12 / 12 | 0 | 0 | 89 | 0 | 0 |

## bio101

Curated row types: {'Class': 105, 'Predicate': 382}

**Classes only in VoID** (118)

- `http://www.projecthalo.com/aura#Absorbance-Scalar-Constant`
- `http://www.projecthalo.com/aura#Acceptance-Constant`
- `http://www.projecthalo.com/aura#Activation-Constant`
- `http://www.projecthalo.com/aura#Age-Constant`
- `http://www.projecthalo.com/aura#Angle-Constant`
- `http://www.projecthalo.com/aura#Animacy-Constant`
- `http://www.projecthalo.com/aura#Area-Constant`
- `http://www.projecthalo.com/aura#Breakability-Constant`
- `http://www.projecthalo.com/aura#Brightness-Constant`
- `http://www.projecthalo.com/aura#Capacity-Constant`
- `http://www.projecthalo.com/aura#Charge-Categorical-Constant`
- `http://www.projecthalo.com/aura#Chemical-Polarity-Constant`
- `http://www.projecthalo.com/aura#Chemical-Stability-Constant`
- `http://www.projecthalo.com/aura#Color-Constant`
- `http://www.projecthalo.com/aura#Concentration-Constant`
- `http://www.projecthalo.com/aura#Conductivity-Constant`
- `http://www.projecthalo.com/aura#Consistency-Constant`
- `http://www.projecthalo.com/aura#Day-Constant`
- `http://www.projecthalo.com/aura#Density-Constant`
- `http://www.projecthalo.com/aura#Depth-Constant`
- `http://www.projecthalo.com/aura#Dimension-Constant`
- `http://www.projecthalo.com/aura#Direction-Constant`
- `http://www.projecthalo.com/aura#Distance-Constant`
- `http://www.projecthalo.com/aura#Duration-Constant`
- `http://www.projecthalo.com/aura#Electrolyte-Status-Constant`
- … 93 more (see comparison.json)

**Classes only curated** (96)

- `http://www.projecthalo.com/aura#Action`
- `http://www.projecthalo.com/aura#Activity`
- `http://www.projecthalo.com/aura#Aggregate`
- `http://www.projecthalo.com/aura#Anatomical-Structure`
- `http://www.projecthalo.com/aura#Angiosperm`
- `http://www.projecthalo.com/aura#Animal-Cell`
- `http://www.projecthalo.com/aura#Animal-Organ`
- `http://www.projecthalo.com/aura#Animal-Process`
- `http://www.projecthalo.com/aura#Animal-Space`
- `http://www.projecthalo.com/aura#Animal-Structure`
- `http://www.projecthalo.com/aura#Anion`
- `http://www.projecthalo.com/aura#Architectural-Structure`
- `http://www.projecthalo.com/aura#Bacterium`
- `http://www.projecthalo.com/aura#Biological-Process`
- `http://www.projecthalo.com/aura#Biological-Region`
- `http://www.projecthalo.com/aura#Cation`
- `http://www.projecthalo.com/aura#Cell-Division`
- `http://www.projecthalo.com/aura#Cell-State`
- `http://www.projecthalo.com/aura#Cellular-Process`
- `http://www.projecthalo.com/aura#Cellular-Structure`
- `http://www.projecthalo.com/aura#Chemical`
- `http://www.projecthalo.com/aura#Chemical-Entity`
- `http://www.projecthalo.com/aura#Chemical-Reaction`
- `http://www.projecthalo.com/aura#Chemical-Signaling`
- `http://www.projecthalo.com/aura#Condition`
- … 71 more (see comparison.json)

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (6)

- `owl:DatatypeProperty` → `rdfs:domain`
- `owl:DatatypeProperty` → `rdfs:range`
- `owl:FunctionalProperty` → `http://www.projecthalo.com/aura#user-description`
- `owl:FunctionalProperty` → `rdfs:domain`
- `owl:FunctionalProperty` → `rdfs:range`
- `owl:ObjectProperty` → `http://www.projecthalo.com/aura#user-description`

**Edges only in VoID** (68)

- `owl:DatatypeProperty` → `rdfs:domain` → `owl:Class`
- `owl:FunctionalProperty` → `rdfs:domain` → `owl:Class`
- `owl:FunctionalProperty` → `rdfs:range` → `owl:Class`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Absorbance-Scalar-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Age-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Area-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Concentration-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Conductivity-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Density-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Depth-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Direction-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Distance-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Duration-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Electrolyte-Status-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Electronegativity-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Energy-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Fertility-Scalar-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Fluidity-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Frequency-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Heat-of-Vaporization-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Height-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Humidity-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Importance-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Intensity-Constant`
- `owl:Restriction` → `owl:hasValue` → `http://www.projecthalo.com/aura#Length-Constant`
- … 43 more (see comparison.json)

**Descriptions that differ** (307)

- `http://www.projecthalo.com/aura#concept2words`<br>curated: Lexicon annotation linking a concept to the words that name it. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `http://www.projecthalo.com/aura#absorbance`<br>curated: The property absorbance of a solution refers to the measure of the fraction of light absorbed through it. Functional. Declared in the schema but not populated in the current release.<br>KG: The property absorbance of a solution refers to the measure of the fraction of light absorbed through it. Declared in the schema but used in no triple or class axiom.
- `http://www.projecthalo.com/aura#abuts`<br>curated: A thing or place is adjacent to another. Used only inside class axioms, as owl:onProperty of 312 owl:Restrictions; never asserted as a direct triple.<br>KG: Used only inside class axioms, as owl:onProperty of 312 owl:Restrictions; never asserted as a direct triple.
- `http://www.projecthalo.com/aura#acceleration`<br>curated: The rate of change of velocity with respect to time. Functional. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `http://www.projecthalo.com/aura#acceleration-magnitude`<br>curated: The magnitude of acceleration for a vector. It can take both negative and positive values. Functional. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `http://www.projecthalo.com/aura#acceptance`<br>curated: Acceptance refers to an attribute of knowledge for its acceptance or rejection by people. Functional. Used only inside class axioms, as owl:onProperty of 2 owl:Restrictions; never asserted as a direct<br>KG: Acceptance refers to an attribute of knowledge for its acceptance or rejection by people. Used only inside class axioms, as owl:onProperty of 2 owl:Restrictions; never asserted as a direct triple.
- `http://www.projecthalo.com/aura#activation`<br>curated: Activation refers to the status of an entity for its ability to perform its primary function. Functional. Used only inside class axioms, as owl:onProperty of 82 owl:Restrictions; never asserted as a d<br>KG: Activation refers to the status of an entity for its ability to perform its primary function. Used only inside class axioms, as owl:onProperty of 82 owl:Restrictions; never asserted as a direct triple
- `http://www.projecthalo.com/aura#activation-of`<br>curated: Inverse of activation: Activation refers to the status of an entity for its ability to perform its primary function. Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never assert<br>KG: Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asserted as a direct triple.
- `http://www.projecthalo.com/aura#age`<br>curated: Age is a property for describing how long an Entity has existed. Functional. Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asserted as a direct triple.<br>KG: Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asserted as a direct triple.
- `http://www.projecthalo.com/aura#agent`<br>curated: The entity that initiates, performs or causes an event. The 'doer'. Used only inside class axioms, as owl:onProperty of 1,381 owl:Restrictions; never asserted as a direct triple.<br>KG: Used only inside class axioms, as owl:onProperty of 1,381 owl:Restrictions; never asserted as a direct triple.
- … 297 more (see comparison.json)

## biobricks-aopwiki

Curated row types: {'Class': 24, 'Predicate': 62}

**Predicates only curated** (3)

- `dct:accuralPeriodicity`
- `http://www.w3.org/ns/dcat#downloadURL`
- `http://xmlns.com/foaf/0.1/homepage`

**(source class, predicate) only in VoID** (147)

- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#AopContext`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#LifeStageContext`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_adverse_outcome`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_evidence`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_key_event`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_key_event_relationship`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_molecular_initiating_event`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://edamontology.org/operation_3799`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:NCIT_C25217`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:NCIT_C25688`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:NCIT_C25725`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:NCIT_C48192`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:NCIT_C54571`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:PATO_0000047`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://purl.org/dc/elements/1.1/creator`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://purl.org/dc/elements/1.1/description`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://purl.org/dc/elements/1.1/identifier`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://purl.org/dc/elements/1.1/source`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://purl.org/dc/elements/1.1/title`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `dct:abstract`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `dct:alternative`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `dct:created`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `rdfs:label`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `rdfs:seeAlso`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://xmlns.com/foaf/0.1/page`
- … 122 more (see comparison.json)

**Edges only in VoID** (70)

- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_adverse_outcome` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_key_event` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_key_event_relationship` → `http://aopkb.org/aop_ontology#KeyEventRelationship`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://aopkb.org/aop_ontology#has_molecular_initiating_event` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `obo:NCIT_C54571` → `obo:NCIT_C54571`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://purl.org/dc/elements/1.1/identifier` → `http://aopkb.org/aop_ontology#AdverseOutcomePathway`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `rdfs:seeAlso` → `http://aopkb.org/aop_ontology#AdverseOutcomePathway`
- `http://aopkb.org/aop_ontology#AdverseOutcomePathway` → `http://xmlns.com/foaf/0.1/page` → `http://aopkb.org/aop_ontology#AdverseOutcomePathway`
- `http://aopkb.org/aop_ontology#CellTypeContext` → `http://purl.org/dc/elements/1.1/identifier` → `http://aopkb.org/aop_ontology#CellTypeContext`
- `http://aopkb.org/aop_ontology#KeyEvent` → `http://aopkb.org/aop_ontology#CellTypeContext` → `http://aopkb.org/aop_ontology#CellTypeContext`
- `http://aopkb.org/aop_ontology#KeyEvent` → `http://aopkb.org/aop_ontology#OrganContext` → `http://aopkb.org/aop_ontology#OrganContext`
- `http://aopkb.org/aop_ontology#KeyEvent` → `http://edamontology.org/data_1025` → `http://edamontology.org/data_1025`
- `http://aopkb.org/aop_ontology#KeyEvent` → `http://edamontology.org/data_1025` → `http://edamontology.org/data_2298`
- `http://aopkb.org/aop_ontology#KeyEvent` → `obo:GO_0008150` → `obo:GO_0008150`
- `http://aopkb.org/aop_ontology#KeyEvent` → `obo:NCBITaxon_131567` → `obo:NCBITaxon_131567`
- `http://aopkb.org/aop_ontology#KeyEvent` → `obo:PATO_0001241` → `http://aopkb.org/aop_ontology#CellTypeContext`
- `http://aopkb.org/aop_ontology#KeyEvent` → `obo:PATO_0001241` → `http://aopkb.org/aop_ontology#OrganContext`
- `http://aopkb.org/aop_ontology#KeyEvent` → `obo:PATO_0001241` → `obo:GO_0008150`
- `http://aopkb.org/aop_ontology#KeyEvent` → `http://purl.org/dc/elements/1.1/identifier` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#KeyEvent` → `dct:isPartOf` → `http://aopkb.org/aop_ontology#AdverseOutcomePathway`
- `http://aopkb.org/aop_ontology#KeyEvent` → `rdfs:seeAlso` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#KeyEvent` → `http://xmlns.com/foaf/0.1/page` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#KeyEventRelationship` → `http://aopkb.org/aop_ontology#has_downstream_key_event` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#KeyEventRelationship` → `http://aopkb.org/aop_ontology#has_upstream_key_event` → `http://aopkb.org/aop_ontology#KeyEvent`
- `http://aopkb.org/aop_ontology#KeyEventRelationship` → `http://edamontology.org/data_1025` → `http://edamontology.org/data_1025`
- … 45 more (see comparison.json)

**Descriptions that differ** (4)

- `obo:GO_0008150`<br>curated: A biological process represents a series of molecular events with a defined beginning and end, carried out by one or more organized assemblies of molecular functions.<br>KG: Note that, in addition to forming the root of the biological process ontology, this term is recommended for the annotation of gene products whose biological process is unknown. When this term is used 
- `obo:GO_0008150`<br>curated: A biological process represents a series of molecular events with a defined beginning and end, carried out by one or more organized assemblies of molecular functions.<br>KG: Note that, in addition to forming the root of the biological process ontology, this term is recommended for the annotation of gene products whose biological process is unknown. When this term is used 
- `obo:PATO_0000001`<br>curated: A dependent entity that inheres in a bearer by virtue of how the bearer is related to other entities.<br>KG: A dependent entity that inheres in a bearer by virtue of how the bearer is related to other entities
- `obo:PATO_0000047`<br>curated: An organismal quality inhering in a bearer by virtue of the bearer's ability to produce gametes.<br>KG: An organismal quality inhering in a bearer by virtue of the bearer's ability to undergo sexual reproduction in order to differentiate the individuals or types involved.

## biobricks-ice

Curated row types: {'Class': 10, 'Predicate': 21}

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (29)

- `obo:CHEMINF_000000` → `http://edamontology.org/has_identifier`
- `obo:CHEMINF_000000` → `obo:RO_0000056`
- `obo:CHEMINF_000000` → `rdfs:label`
- `obo:CHEMINF_000446` → `http://purl.org/dc/elements/1.1/source`
- `obo:CHEMINF_000446` → `rdfs:label`
- `obo:CHEMINF_000568` → `http://purl.org/dc/elements/1.1/source`
- `obo:CHEMINF_000568` → `rdfs:label`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `http://purl.org/dc/elements/1.1/source`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `http://www.bioassayontology.org/bao#BAO_0000209`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `rdfs:label`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/assay_entrez_gene_id`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/assay_invitro_assay_format`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/assay_source`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/assay_species`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/assay_tissue`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/mayInformOn`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/throughMechanisticTarget`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/throughMechanisticTarget_NCIm`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://identifiers.org/umls:C1708327`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:OBI_0000299`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:RO_0000057`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:ExO_0000055`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:IAO_0000136`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `http://semanticscience.org/resource/SIO_000221`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `http://semanticscience.org/resource/SIO_000300`
- … 4 more (see comparison.json)

**Edges only in VoID** (17)

- `obo:CHEMINF_000000` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000446`
- `obo:CHEMINF_000000` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000568`
- `obo:CHEMINF_000000` → `obo:RO_0000056` → `http://www.bioassayontology.org/bao#BAO_0000040`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `http://www.bioassayontology.org/bao#BAO_0000209` → `http://www.bioassayontology.org/bao#BAO_0000040`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/assay_entrez_gene_id` → `http://edamontology.org/data_1027`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/throughMechanisticTarget_NCIm` → `http://edamontology.org/data_1181`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://ice.ntp.niehs.nih.gov/property/throughMechanisticTarget_NCIm` → `http://www.bioassayontology.org/bao#BAO_0003064`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://identifiers.org/umls:C1708327` → `http://edamontology.org/data_1181`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://identifiers.org/umls:C1708327` → `http://www.bioassayontology.org/bao#BAO_0003064`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:OBI_0000299` → `http://www.bioassayontology.org/bao#BAO_0000179`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:RO_0000057` → `obo:CHEMINF_000000`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:RO_0000057` → `biolink:ChemicalEntity`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:IAO_0000136` → `obo:CHEMINF_000000`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:IAO_0000136` → `biolink:ChemicalEntity`
- `biolink:ChemicalEntity` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000446`
- `biolink:ChemicalEntity` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000568`
- `biolink:ChemicalEntity` → `obo:RO_0000056` → `http://www.bioassayontology.org/bao#BAO_0000040`

**Descriptions that differ** (4)

- `obo:IAO_0000136`<br>curated: Indicates that information or data pertains to a particular subject<br>KG: A (currently) primitive relation that relates an information artifact to an entity.
- `obo:OBI_0000299`<br>curated: The result or product produced by a process or assay<br>KG: The inverse property of is specified output of
- `obo:RO_0000056`<br>curated: An entity takes part in or is involved in a biological process<br>KG: a relation between a continuant and a process, in which the continuant is somehow involved in the process
- `obo:RO_0000057`<br>curated: A process involves or includes a particular entity<br>KG: a relation between a process and a continuant, in which the continuant is somehow involved in the process

## biobricks-mesh

Curated row types: {'Class': 21, 'Predicate': 68}

**Classes only in VoID** (4)

- `owl:AnnotationProperty`
- `owl:DatatypeProperty`
- `owl:ObjectProperty`
- `http://www.w3.org/ns/sparql-service-description#Service`

**Classes only curated** (3)

- `http://id.nlm.nih.gov/mesh/vocab#Descriptor`
- `http://id.nlm.nih.gov/mesh/vocab#DescriptorQualifierPair`
- `http://id.nlm.nih.gov/mesh/vocab#SupplementaryConceptRecord`

**Predicates only in VoID** (5)

- `http://www.w3.org/ns/sparql-service-description#endpoint`
- `http://www.w3.org/ns/sparql-service-description#feature`
- `http://www.w3.org/ns/sparql-service-description#resultFormat`
- `http://www.w3.org/ns/sparql-service-description#supportedLanguage`
- `http://www.w3.org/ns/sparql-service-description#url`

**Predicates only curated** (10)

- `dct:created`
- `dct:creator`
- `dct:date`
- `dct:license`
- `dct:publisher`
- `dct:subject`
- `dct:title`
- `http://xmlns.com/foaf/0.1/homepage`
- `http://xmlns.com/foaf/0.1/page`
- `http://xmlns.com/foaf/0.1/primaryTopic`

**(source class, predicate) only in VoID** (218)

- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#active`
- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasQualifier`
- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#lastActiveYear`
- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `rdfs:label`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#active`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#annotation`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#dateCreated`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#dateEstablished`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#dateRevised`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#historyNote`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#identifier`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#preferredConcept`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#preferredTerm`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `rdfs:label`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#active`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#casn1_label`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#identifier`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#lastActiveYear`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#preferredTerm`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#registryNumber`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#relatedRegistryNumber`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#scopeNote`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#term`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `rdfs:label`
- … 193 more (see comparison.json)

**(source class, predicate) only curated** (1)

- `http://id.nlm.nih.gov/mesh/vocab#Descriptor` → `http://id.nlm.nih.gov/mesh/vocab#broaderDescriptor`

**Edges only in VoID** (92)

- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#TopicalDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasQualifier` → `http://id.nlm.nih.gov/mesh/vocab#Qualifier`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#preferredConcept` → `http://id.nlm.nih.gov/mesh/vocab#Concept`
- `http://id.nlm.nih.gov/mesh/vocab#CheckTag` → `http://id.nlm.nih.gov/mesh/vocab#preferredTerm` → `http://id.nlm.nih.gov/mesh/vocab#Term`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#preferredTerm` → `http://id.nlm.nih.gov/mesh/vocab#Term`
- `http://id.nlm.nih.gov/mesh/vocab#Concept` → `http://id.nlm.nih.gov/mesh/vocab#term` → `http://id.nlm.nih.gov/mesh/vocab#Term`
- `http://id.nlm.nih.gov/mesh/vocab#DisallowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#TopicalDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#DisallowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#hasQualifier` → `http://id.nlm.nih.gov/mesh/vocab#Qualifier`
- `http://id.nlm.nih.gov/mesh/vocab#DisallowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#useInstead` → `http://id.nlm.nih.gov/mesh/vocab#AllowedDescriptorQualifierPair`
- `http://id.nlm.nih.gov/mesh/vocab#DisallowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#useInstead` → `http://id.nlm.nih.gov/mesh/vocab#DisallowedDescriptorQualifierPair`
- `http://id.nlm.nih.gov/mesh/vocab#DisallowedDescriptorQualifierPair` → `http://id.nlm.nih.gov/mesh/vocab#useInstead` → `http://id.nlm.nih.gov/mesh/vocab#TopicalDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#allowableQualifier` → `http://id.nlm.nih.gov/mesh/vocab#Qualifier`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#broaderDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#broaderDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#TopicalDescriptor`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#concept` → `http://id.nlm.nih.gov/mesh/vocab#Concept`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#preferredConcept` → `http://id.nlm.nih.gov/mesh/vocab#Concept`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#preferredTerm` → `http://id.nlm.nih.gov/mesh/vocab#Term`
- `http://id.nlm.nih.gov/mesh/vocab#GeographicalDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#treeNumber` → `http://id.nlm.nih.gov/mesh/vocab#TreeNumber`
- `http://id.nlm.nih.gov/mesh/vocab#PublicationType` → `http://id.nlm.nih.gov/mesh/vocab#broaderDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#PublicationType`
- `http://id.nlm.nih.gov/mesh/vocab#PublicationType` → `http://id.nlm.nih.gov/mesh/vocab#concept` → `http://id.nlm.nih.gov/mesh/vocab#Concept`
- `http://id.nlm.nih.gov/mesh/vocab#PublicationType` → `http://id.nlm.nih.gov/mesh/vocab#preferredConcept` → `http://id.nlm.nih.gov/mesh/vocab#Concept`
- `http://id.nlm.nih.gov/mesh/vocab#PublicationType` → `http://id.nlm.nih.gov/mesh/vocab#preferredTerm` → `http://id.nlm.nih.gov/mesh/vocab#Term`
- `http://id.nlm.nih.gov/mesh/vocab#PublicationType` → `http://id.nlm.nih.gov/mesh/vocab#seeAlso` → `http://id.nlm.nih.gov/mesh/vocab#PublicationType`
- `http://id.nlm.nih.gov/mesh/vocab#PublicationType` → `http://id.nlm.nih.gov/mesh/vocab#treeNumber` → `http://id.nlm.nih.gov/mesh/vocab#TreeNumber`
- … 67 more (see comparison.json)

**Edges only curated** (1)

- `http://id.nlm.nih.gov/mesh/vocab#Descriptor` → `http://id.nlm.nih.gov/mesh/vocab#broaderDescriptor` → `http://id.nlm.nih.gov/mesh/vocab#Descriptor`

**Descriptions that differ** (4)

- `http://id.nlm.nih.gov/mesh/vocab#altLabel`<br>curated: A property of Terms. A lexical variant for a Termâs prefLabel. meshv:altLabel is a subproperty of rdfs:label<br>KG: A property of Terms. A lexical variant for a Term’s prefLabel. meshv:altLabel is a subproperty of rdfs:label
- `http://id.nlm.nih.gov/mesh/vocab#broader`<br>curated: A broader MeSH concept related to the subject.<br>KG: Declared in the schema but used in no triple or class axiom.
- `http://id.nlm.nih.gov/mesh/vocab#parentTreeNumber`<br>curated: Relates one TreeNumber to another. Immediate âparentâ TreeNumber, meaning one level higher in the TreeNumber hierarchy. Example: D03.438.221 is a parent of D03.438.221.173.<br>KG: Relates one TreeNumber to another. Immediate “parent” TreeNumber, meaning one level higher in the TreeNumber hierarchy. Example: D03.438.221 is a parent of D03.438.221.173.
- `http://id.nlm.nih.gov/mesh/vocab#previousIndexing`<br>curated: A property of Descriptors and Supplementary Concept Records. Free-text information referring to Descriptors or DescriptorQualifierPairs that were used to index the concept in MEDLINE before the Descri<br>KG: A property of Descriptors and Supplementary Concept Records. Free-text information referring to Descriptors or DescriptorQualifierPairs that were used to index the concept in MEDLINE before the Descri

## biobricks-pubchem-annotations

Curated row types: {'Class': 1, 'Predicate': 6}

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (3)

- `http://www.w3.org/ns/oa#Annotation` → `http://purl.org/dc/elements/1.1/subject`
- `http://www.w3.org/ns/oa#Annotation` → `http://www.w3.org/ns/oa#hasBody`
- `http://www.w3.org/ns/oa#Annotation` → `http://www.w3.org/ns/oa#hasTarget`

## biobricks-tox21

Curated row types: {'Class': 1, 'Predicate': 3}

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (2)

- `obo:CHEMINF_000446` → `http://purl.org/dc/elements/1.1/source`
- `obo:CHEMINF_000446` → `rdfs:label`

## biobricks-toxcast

Curated row types: {'Class': 7, 'Predicate': 11}

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (19)

- `obo:CHEMINF_000000` → `http://edamontology.org/has_identifier`
- `obo:CHEMINF_000000` → `obo:RO_0000056`
- `obo:CHEMINF_000000` → `rdfs:label`
- `obo:CHEMINF_000446` → `http://purl.org/dc/elements/1.1/source`
- `obo:CHEMINF_000446` → `rdfs:label`
- `obo:CHEMINF_000568` → `http://purl.org/dc/elements/1.1/source`
- `obo:CHEMINF_000568` → `rdfs:label`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `http://purl.org/dc/elements/1.1/source`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `http://www.bioassayontology.org/bao#BAO_0000209`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `rdfs:label`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `https://comptox.epa.gov/property/assayID`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:OBI_0000299`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:RO_0000057`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:IAO_0000136`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `http://semanticscience.org/resource/SIO_000300`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `rdfs:label`
- `biolink:ChemicalEntity` → `http://edamontology.org/has_identifier`
- `biolink:ChemicalEntity` → `obo:RO_0000056`
- `biolink:ChemicalEntity` → `rdfs:label`

**Edges only in VoID** (12)

- `obo:CHEMINF_000000` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000446`
- `obo:CHEMINF_000000` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000568`
- `obo:CHEMINF_000000` → `obo:RO_0000056` → `http://www.bioassayontology.org/bao#BAO_0000040`
- `http://www.bioassayontology.org/bao#BAO_0000015` → `http://www.bioassayontology.org/bao#BAO_0000209` → `http://www.bioassayontology.org/bao#BAO_0000040`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:OBI_0000299` → `http://www.bioassayontology.org/bao#BAO_0000179`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:RO_0000057` → `obo:CHEMINF_000000`
- `http://www.bioassayontology.org/bao#BAO_0000040` → `obo:RO_0000057` → `biolink:ChemicalEntity`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:IAO_0000136` → `obo:CHEMINF_000000`
- `http://www.bioassayontology.org/bao#BAO_0000179` → `obo:IAO_0000136` → `biolink:ChemicalEntity`
- `biolink:ChemicalEntity` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000446`
- `biolink:ChemicalEntity` → `http://edamontology.org/has_identifier` → `obo:CHEMINF_000568`
- `biolink:ChemicalEntity` → `obo:RO_0000056` → `http://www.bioassayontology.org/bao#BAO_0000040`

**Descriptions that differ** (4)

- `obo:IAO_0000136`<br>curated: Indicates that information or data pertains to a particular subject<br>KG: A (currently) primitive relation that relates an information artifact to an entity.
- `obo:OBI_0000299`<br>curated: The result or product produced by a process or assay<br>KG: The inverse property of is specified output of
- `obo:RO_0000056`<br>curated: An entity takes part in or is involved in a biological process<br>KG: a relation between a continuant and a process, in which the continuant is somehow involved in the process
- `obo:RO_0000057`<br>curated: A process involves or includes a particular entity<br>KG: a relation between a process and a continuant, in which the continuant is somehow involved in the process

## biohealth

Curated row types: {'Class': 2, 'Predicate': 70}

**(source class, predicate) only curated** (1)

- `rdf:Statement` → `dct:source`

**Edge properties (predicate, property) only in VoID** (64)

- `https://biohealthkg.proto-okn.net/kg/schema/ADMINISTERED_TO` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/COMPLICATES` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/CONVERTS_TO` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/LOCATION_OF(SPEC)` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/MEASUREMENT_OF` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/MEASURES` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/METHOD_OF` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_ADMINISTERED_TO` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_AFFECTS` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_ASSOCIATED_WITH` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_AUGMENTS` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_CAUSES` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_COEXISTS_WITH` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_COMPLICATES` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_CONVERTS_TO` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_DIAGNOSES` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_DISRUPTS` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_INHIBITS` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_INTERACTS_WITH` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_ISA` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_LOCATION_OF` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_MANIFESTATION_OF` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_MEASUREMENT_OF` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_MEASURES` → `dct:source`
- `https://biohealthkg.proto-okn.net/kg/schema/NEG_METHOD_OF` → `dct:source`
- … 39 more (see comparison.json)

## biomarkerkg

Curated row types: {'Class': 7, 'Predicate': 12}

**Predicates only in VoID** (10)

- `obo:OBCI_100000009`
- `obo:OBCI_100000011`
- `obo:OBCI_100000015`
- `obo:OBCI_100000016`
- `obo:OBCI_100000018`
- `obo:RO_0002558`
- `obo:RO_0020327`
- `obo:RO_0020328`
- `obo:RO_0020331`
- `obo:RO_0020333`

**Predicates only curated** (10)

- `obo:OBCI_1000002`
- `obo:OBCI_1000003`
- `obo:OBCI_1000006`
- `obo:OBCI_1000008`
- `obo:OBCI_1000009`
- `obo:OBCI_1000011`
- `obo:OBCI_1000015`
- `obo:OBCI_1000016`
- `obo:OBCI_1000017`
- `obo:OBCI_1000018`

**(source class, predicate) only in VoID** (46)

- `obo:OBCI_0000002` → `obo:OBCI_100000009`
- `obo:OBCI_0000002` → `obo:OBCI_100000011`
- `obo:OBCI_0000002` → `obo:OBCI_100000015`
- `obo:OBCI_0000002` → `obo:OBCI_100000016`
- `obo:OBCI_0000002` → `obo:OBCI_100000018`
- `obo:OBCI_0000002` → `obo:RO_0002558`
- `obo:OBCI_0000002` → `obo:RO_0020327`
- `obo:OBCI_0000002` → `obo:RO_0020328`
- `obo:OBCI_0000002` → `obo:RO_0020331`
- `obo:OBCI_0000002` → `obo:RO_0020333`
- `obo:OBCI_0000003` → `obo:OBCI_100000009`
- `obo:OBCI_0000003` → `obo:OBCI_100000011`
- `obo:OBCI_0000003` → `obo:OBCI_100000015`
- `obo:OBCI_0000003` → `obo:OBCI_100000016`
- `obo:OBCI_0000003` → `obo:OBCI_100000018`
- `obo:OBCI_0000003` → `obo:RO_0002558`
- `obo:OBCI_0000003` → `obo:RO_0020328`
- `obo:OBCI_0000003` → `obo:RO_0020331`
- `obo:OBCI_0000004` → `obo:OBCI_100000009`
- `obo:OBCI_0000004` → `obo:OBCI_100000011`
- `obo:OBCI_0000004` → `obo:OBCI_100000015`
- `obo:OBCI_0000004` → `obo:OBCI_100000018`
- `obo:OBCI_0000004` → `obo:RO_0002558`
- `obo:OBCI_0000005` → `obo:OBCI_100000009`
- `obo:OBCI_0000005` → `obo:OBCI_100000011`
- … 21 more (see comparison.json)

**(source class, predicate) only curated** (60)

- `obo:OBCI_0000002` → `obo:OBCI_1000002`
- `obo:OBCI_0000002` → `obo:OBCI_1000003`
- `obo:OBCI_0000002` → `obo:OBCI_1000006`
- `obo:OBCI_0000002` → `obo:OBCI_1000008`
- `obo:OBCI_0000002` → `obo:OBCI_1000009`
- `obo:OBCI_0000002` → `obo:OBCI_1000011`
- `obo:OBCI_0000002` → `obo:OBCI_1000015`
- `obo:OBCI_0000002` → `obo:OBCI_1000016`
- `obo:OBCI_0000002` → `obo:OBCI_1000017`
- `obo:OBCI_0000002` → `obo:OBCI_1000018`
- `obo:OBCI_0000003` → `obo:OBCI_1000002`
- `obo:OBCI_0000003` → `obo:OBCI_1000003`
- `obo:OBCI_0000003` → `obo:OBCI_1000006`
- `obo:OBCI_0000003` → `obo:OBCI_1000008`
- `obo:OBCI_0000003` → `obo:OBCI_1000009`
- `obo:OBCI_0000003` → `obo:OBCI_1000011`
- `obo:OBCI_0000003` → `obo:OBCI_1000015`
- `obo:OBCI_0000003` → `obo:OBCI_1000016`
- `obo:OBCI_0000003` → `obo:OBCI_1000017`
- `obo:OBCI_0000003` → `obo:OBCI_1000018`
- `obo:OBCI_0000004` → `obo:OBCI_1000002`
- `obo:OBCI_0000004` → `obo:OBCI_1000003`
- `obo:OBCI_0000004` → `obo:OBCI_1000006`
- `obo:OBCI_0000004` → `obo:OBCI_1000008`
- `obo:OBCI_0000004` → `obo:OBCI_1000009`
- … 35 more (see comparison.json)

**Edges only in VoID** (13)

- `obo:OBCI_0000002` → `obo:OBCI_100000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000002` → `obo:OBCI_100000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000002` → `obo:OBCI_100000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000003` → `obo:OBCI_100000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000004` → `obo:OBCI_100000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000004` → `obo:OBCI_100000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000005` → `obo:OBCI_100000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000005` → `obo:OBCI_100000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000006` → `obo:OBCI_100000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000006` → `obo:OBCI_100000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_100000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_100000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_100000016` → `http://purl.uniprot.org/core/Protein`

**Edges only curated** (24)

- `obo:OBCI_0000002` → `obo:OBCI_1000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000002` → `obo:OBCI_1000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000002` → `obo:OBCI_1000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000002` → `obo:OBCI_1000017` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000003` → `obo:OBCI_1000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000003` → `obo:OBCI_1000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000003` → `obo:OBCI_1000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000003` → `obo:OBCI_1000017` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000004` → `obo:OBCI_1000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000004` → `obo:OBCI_1000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000004` → `obo:OBCI_1000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000004` → `obo:OBCI_1000017` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000005` → `obo:OBCI_1000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000005` → `obo:OBCI_1000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000005` → `obo:OBCI_1000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000005` → `obo:OBCI_1000017` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000006` → `obo:OBCI_1000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000006` → `obo:OBCI_1000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000006` → `obo:OBCI_1000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000006` → `obo:OBCI_1000017` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_1000009` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_1000015` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_1000016` → `http://purl.uniprot.org/core/Protein`
- `obo:OBCI_0000008` → `obo:OBCI_1000017` → `http://purl.uniprot.org/core/Protein`

## climatemodelskg

Curated row types: {'Class': 51, 'NodeProperty': 217, 'Predicate': 136}

**Classes only in VoID** (4)

- `owl:Class`
- `owl:DatatypeProperty`
- `owl:ObjectProperty`
- `owl:Ontology`

**Classes only curated** (3)

- `https://climatepub4kg.github.io/ontology#GridLabel`
- `https://climatepub4kg.github.io/ontology#Model`
- `https://climatepub4kg.github.io/ontology#Water_Bodies`

**Predicates only in VoID** (7)

- `rdfs:comment`
- `rdfs:domain`
- `rdfs:isDefinedBy`
- `rdfs:label`
- `rdfs:range`
- `owl:versionIRI`
- `owl:versionInfo`

**(source class, predicate) only in VoID** (33)

- `owl:Class` → `rdfs:comment`
- `owl:Class` → `rdfs:isDefinedBy`
- `owl:Class` → `rdfs:label`
- `owl:Class` → `skos:definition`
- `owl:DatatypeProperty` → `rdfs:comment`
- `owl:DatatypeProperty` → `rdfs:domain`
- `owl:DatatypeProperty` → `rdfs:isDefinedBy`
- `owl:DatatypeProperty` → `rdfs:label`
- `owl:DatatypeProperty` → `rdfs:range`
- `owl:DatatypeProperty` → `skos:definition`
- `owl:ObjectProperty` → `rdfs:comment`
- `owl:ObjectProperty` → `rdfs:domain`
- `owl:ObjectProperty` → `rdfs:isDefinedBy`
- `owl:ObjectProperty` → `rdfs:label`
- `owl:ObjectProperty` → `rdfs:range`
- `owl:ObjectProperty` → `skos:definition`
- `owl:Ontology` → `dct:abstract`
- `owl:Ontology` → `dct:contributor`
- `owl:Ontology` → `dct:creator`
- `owl:Ontology` → `dct:description`
- `owl:Ontology` → `dct:issued`
- `owl:Ontology` → `dct:license`
- `owl:Ontology` → `dct:publisher`
- `owl:Ontology` → `dct:source`
- `owl:Ontology` → `dct:title`
- … 8 more (see comparison.json)

**(source class, predicate) only curated** (16)

- `owl:Class` → `skos:definition`
- `owl:DatatypeProperty` → `skos:definition`
- `owl:ObjectProperty` → `skos:definition`
- `owl:Ontology` → `dct:abstract`
- `owl:Ontology` → `dct:contributor`
- `owl:Ontology` → `dct:creator`
- `owl:Ontology` → `dct:description`
- `owl:Ontology` → `dct:issued`
- `owl:Ontology` → `dct:license`
- `owl:Ontology` → `dct:publisher`
- `owl:Ontology` → `dct:source`
- `owl:Ontology` → `dct:title`
- `owl:Ontology` → `http://purl.org/ontology/bibo/status`
- `owl:Ontology` → `http://purl.org/vocab/vann/preferredNamespacePrefix`
- `owl:Ontology` → `http://purl.org/vocab/vann/preferredNamespaceUri`
- `owl:Ontology` → `http://xmlns.com/foaf/0.1/homepage`

**Edges only in VoID** (6)

- `owl:Class` → `rdfs:isDefinedBy` → `owl:Ontology`
- `owl:DatatypeProperty` → `rdfs:domain` → `owl:Class`
- `owl:DatatypeProperty` → `rdfs:isDefinedBy` → `owl:Ontology`
- `owl:ObjectProperty` → `rdfs:domain` → `owl:Class`
- `owl:ObjectProperty` → `rdfs:isDefinedBy` → `owl:Ontology`
- `owl:ObjectProperty` → `rdfs:range` → `owl:Class`

**Curated class labels that resolve to no URI** (4)

- `owl:Class`
- `owl:DatatypeProperty`
- `owl:ObjectProperty`
- `owl:Ontology`

## digcfdekg

Curated row types: {'Class': 13, 'Predicate': 16}

**Classes only in VoID** (3)

- `owl:Class`
- `owl:DatatypeProperty`
- `owl:ObjectProperty`

**(source class, predicate) only in VoID** (20)

- `owl:Class` → `rdfs:label`
- `owl:ObjectProperty` → `rdfs:label`
- `kg:schema/GeneFactorAssociation` → `rdf:object`
- `kg:schema/GeneFactorAssociation` → `rdf:predicate`
- `kg:schema/GeneFactorAssociation` → `rdf:subject`
- `kg:schema/GeneInGeneSetAssociation` → `rdf:object`
- `kg:schema/GeneInGeneSetAssociation` → `rdf:predicate`
- `kg:schema/GeneInGeneSetAssociation` → `rdf:subject`
- `kg:schema/GeneSetFactorAssociation` → `rdf:object`
- `kg:schema/GeneSetFactorAssociation` → `rdf:predicate`
- `kg:schema/GeneSetFactorAssociation` → `rdf:subject`
- `kg:schema/GeneSetTraitAssociation` → `rdf:object`
- `kg:schema/GeneSetTraitAssociation` → `rdf:predicate`
- `kg:schema/GeneSetTraitAssociation` → `rdf:subject`
- `kg:schema/GeneTraitAssociation` → `rdf:object`
- `kg:schema/GeneTraitAssociation` → `rdf:predicate`
- `kg:schema/GeneTraitAssociation` → `rdf:subject`
- `kg:schema/TraitFactorAssociation` → `rdf:object`
- `kg:schema/TraitFactorAssociation` → `rdf:predicate`
- `kg:schema/TraitFactorAssociation` → `rdf:subject`

**(source class, predicate) only curated** (5)

- `rdf:Statement` → `dct:source`
- `rdf:Statement` → `http://www.w3.org/ns/prov#wasGeneratedBy`
- `rdf:Statement` → `kg:schema/edgeType`
- `rdf:Statement` → `kg:schema/scoreType`
- `rdf:Statement` → `kg:schema/weight`

**Edges only in VoID** (19)

- `rdf:Statement` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/GeneFactorAssociation` → `rdf:object` → `kg:schema/Factor`
- `kg:schema/GeneFactorAssociation` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/GeneFactorAssociation` → `rdf:subject` → `kg:schema/Gene`
- `kg:schema/GeneInGeneSetAssociation` → `rdf:object` → `kg:schema/GeneSet`
- `kg:schema/GeneInGeneSetAssociation` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/GeneInGeneSetAssociation` → `rdf:subject` → `kg:schema/Gene`
- `kg:schema/GeneSetFactorAssociation` → `rdf:object` → `kg:schema/Factor`
- `kg:schema/GeneSetFactorAssociation` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/GeneSetFactorAssociation` → `rdf:subject` → `kg:schema/GeneSet`
- `kg:schema/GeneSetTraitAssociation` → `rdf:object` → `kg:schema/Trait`
- `kg:schema/GeneSetTraitAssociation` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/GeneSetTraitAssociation` → `rdf:subject` → `kg:schema/GeneSet`
- `kg:schema/GeneTraitAssociation` → `rdf:object` → `kg:schema/Trait`
- `kg:schema/GeneTraitAssociation` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/GeneTraitAssociation` → `rdf:subject` → `kg:schema/Gene`
- `kg:schema/TraitFactorAssociation` → `rdf:object` → `kg:schema/Factor`
- `kg:schema/TraitFactorAssociation` → `rdf:predicate` → `owl:ObjectProperty`
- `kg:schema/TraitFactorAssociation` → `rdf:subject` → `kg:schema/Trait`

**Edges only curated** (2)

- `rdf:Statement` → `http://www.w3.org/ns/prov#wasGeneratedBy` → `kg:schema/GenerationMethod`
- `rdf:Statement` → `kg:schema/scoreType` → `kg:schema/ScoreType`

**Edge properties (predicate, property) only in VoID** (30)

- `kg:schema/geneInGeneSet` → `dct:source`
- `kg:schema/geneInGeneSet` → `http://www.w3.org/ns/prov#wasGeneratedBy`
- `kg:schema/geneInGeneSet` → `kg:schema/edgeType`
- `kg:schema/geneInGeneSet` → `kg:schema/scoreType`
- `kg:schema/geneInGeneSet` → `kg:schema/weight`
- `kg:schema/geneSetToFactor` → `dct:source`
- `kg:schema/geneSetToFactor` → `http://www.w3.org/ns/prov#wasGeneratedBy`
- `kg:schema/geneSetToFactor` → `kg:schema/edgeType`
- `kg:schema/geneSetToFactor` → `kg:schema/scoreType`
- `kg:schema/geneSetToFactor` → `kg:schema/weight`
- `kg:schema/geneSetToTrait` → `dct:source`
- `kg:schema/geneSetToTrait` → `http://www.w3.org/ns/prov#wasGeneratedBy`
- `kg:schema/geneSetToTrait` → `kg:schema/edgeType`
- `kg:schema/geneSetToTrait` → `kg:schema/scoreType`
- `kg:schema/geneSetToTrait` → `kg:schema/weight`
- `kg:schema/geneToFactor` → `dct:source`
- `kg:schema/geneToFactor` → `http://www.w3.org/ns/prov#wasGeneratedBy`
- `kg:schema/geneToFactor` → `kg:schema/edgeType`
- `kg:schema/geneToFactor` → `kg:schema/scoreType`
- `kg:schema/geneToFactor` → `kg:schema/weight`
- `kg:schema/geneToTrait` → `dct:source`
- `kg:schema/geneToTrait` → `http://www.w3.org/ns/prov#wasGeneratedBy`
- `kg:schema/geneToTrait` → `kg:schema/edgeType`
- `kg:schema/geneToTrait` → `kg:schema/scoreType`
- `kg:schema/geneToTrait` → `kg:schema/weight`
- … 5 more (see comparison.json)

## dreamkg

Curated row types: {'Class': 13, 'Predicate': 40}

**Classes only in VoID** (5)

- `owl:Class`
- `owl:DatatypeProperty`
- `owl:NamedIndividual`
- `owl:ObjectProperty`
- `owl:Ontology`

**Classes only curated** (4)

- `schema:AdministrativeArea`
- `schema:Audience`
- `schema:OpeningHoursSpecification`
- `schema:Organization`

**Predicates only in VoID** (14)

- `schema:about`
- `schema:abstract`
- `schema:audience`
- `schema:isAccessibleForFree`
- `schema:itemReviewed`
- `schema:review`
- `schema:serviceChannel`
- `schema:subjectOf`
- `schema:suggestedAnswer`
- `http://www.opengis.net/ont/geosparql#lat`
- `http://www.opengis.net/ont/geosparql#long`
- `rdfs:comment`
- `rdfs:subClassOf`
- `rdfs:subPropertyOf`

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (4)

- `owl:Class` → `rdfs:subClassOf`
- `owl:DatatypeProperty` → `rdfs:subPropertyOf`
- `owl:ObjectProperty` → `rdfs:subPropertyOf`
- `owl:Ontology` → `rdfs:comment`

**Edges only in VoID** (2)

- `schema:CategoryCode` → `schema:inCodeSet` → `owl:NamedIndividual`
- `http://www.opengis.net/ont/geosparql#Geometry` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`

**Descriptions that differ** (6)

- `schema:audienceType`<br>curated: The target group associated with a given audience (e.g., veterans, car owners, musicians). Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `schema:closes`<br>curated: The closing hour of the place or service on the given day(s) of the week. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `schema:dayOfWeek`<br>curated: The day of the week for which these opening hours are valid. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `schema:hoursAvailable`<br>curated: The hours during which this service or contact is available. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `schema:opens`<br>curated: The opening hour of the place or service on the given day(s) of the week. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `schema:url`<br>curated: The URL of the item. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.

## evoweb

Curated row types: {'Class': 1, 'Predicate': 4}

## fiokg

Curated row types: {'Class': 89, 'Predicate': 48}

**Classes only in VoID** (23)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3`
- `rdf:List`
- `rdf:ObjectProperty`
- `rdf:Property`
- `rdfs:Class`
- `rdfs:ContainerMembershipProperty`
- `rdfs:Datatype`
- `rdfs:Resource`
- `owl:AnnotationProperty`
- `owl:Class`
- `owl:DatatypeProperty`
- `owl:NamedIndividual`
- `owl:ObjectProperty`
- `owl:Ontology`
- `owl:OntologyProperty`
- `owl:ReflexiveProperty`
- `owl:Restriction`
- `owl:SymmetricProperty`
- `owl:Thing`
- `owl:TransitiveProperty`
- `http://www.w3.org/ns/prov#Agent`

**Classes only curated** (3)

- `http://w3id.org/fio/v1/epa-frs#Chemicalstorageprograms`
- `http://w3id.org/fio/v1/epa-frs#StationSystem`
- `http://w3id.org/fio/v1/fio#IndustryCollection`

**Predicates only in VoID** (65)

- `http://proton.semanticweb.org/protonsys#transitiveOver`
- `dct:decscription`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfCrosses`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfEquals`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfOverlaps`
- `http://w3id.org/fio/v1/epa-frs#hasMonitoringRecord`
- `http://w3id.org/fio/v1/fio#sameCode`
- `http://w3id.org/sawgraph/v1/us-wqp#groupName`
- `http://w3id.org/sawgraph/v1/us-wqp#hasProjectId`
- `http://w3id.org/sawgraph/v1/us-wqp#locationType`
- `http://w3id.org/sawgraph/v1/us-wqp#rank`
- `http://w3id.org/sawgraph/v1/us-wqp#sampleCollectionMethod`
- `http://w3id.org/sawgraph/v1/us-wqp#sampleID`
- `http://w3id.org/sawgraph/v1/us-wqp#siteId`
- `http://w3id.org/sawgraph/v1/us-wqp#siteName`
- `http://w3id.org/sawgraph/v1/us-wqp#srsID`
- `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `rdf:first`
- `rdf:langRange`
- `rdf:rest`
- `rdfs:comment`
- `rdfs:domain`
- `rdfs:isDefinedBy`
- `rdfs:range`
- … 40 more (see comparison.json)

**(source class, predicate) only in VoID** (763)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `owl:sameAs`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfTouches`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `owl:sameAs`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/Region` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf`
- `http://w3id.org/fio/v1/epa-frs#Agency` → `http://w3id.org/fio/v1/fio#hasFacility`
- `http://w3id.org/fio/v1/epa-frs#Agency` → `rdfs:label`
- `http://w3id.org/fio/v1/epa-frs#Agency` → `owl:sameAs`
- `http://w3id.org/fio/v1/epa-frs#Agency.Agriculture` → `http://w3id.org/fio/v1/fio#hasFacility`
- `http://w3id.org/fio/v1/epa-frs#Agency.Agriculture` → `rdfs:label`
- `http://w3id.org/fio/v1/epa-frs#Agency.Agriculture` → `owl:sameAs`
- `http://w3id.org/fio/v1/epa-frs#Agency.Commerce` → `http://w3id.org/fio/v1/fio#hasFacility`
- `http://w3id.org/fio/v1/epa-frs#Agency.Commerce` → `rdfs:label`
- `http://w3id.org/fio/v1/epa-frs#Agency.Commerce` → `owl:sameAs`
- `http://w3id.org/fio/v1/epa-frs#Agency.Congress` → `http://w3id.org/fio/v1/fio#hasFacility`
- `http://w3id.org/fio/v1/epa-frs#Agency.Congress` → `rdfs:label`
- `http://w3id.org/fio/v1/epa-frs#Agency.Congress` → `owl:sameAs`
- … 738 more (see comparison.json)

**(source class, predicate) only curated** (1)

- `http://w3id.org/fio/v1/fio#Industry` → `http://w3id.org/fio/v1/fio#yearDeprecated`

**Edges only in VoID** (3753)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Region`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://w3id.org/fio/v1/epa-frs#FRS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://w3id.org/fio/v1/fio#Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `rdfs:Resource`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://w3id.org/fio/v1/epa-frs#FRS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://w3id.org/fio/v1/fio#Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `rdfs:Resource`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://w3id.org/fio/v1/epa-frs#FRS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://w3id.org/fio/v1/fio#Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `rdfs:Resource`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation` → `http://w3id.org/fio/v1/epa-frs#EPA-PFAS-Facility`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation` → `http://w3id.org/fio/v1/epa-frs#FRS-Facility`
- … 3728 more (see comparison.json)

**Descriptions that differ** (5)

- `http://w3id.org/fio/v1/epa-frs#MonitoringRecord`<br>curated: Monitoring Record for a facility<br>KG: A record that monitors a facility on an ongoing basis
- `http://www.opengis.net/ont/geosparql#SpatialObject`<br>curated: Anything spatial (being or having a shape, position or an extent). Here the only specific type of the regions facilities are located in: counties, county subdivisions and Level 13 S2 cells; facilities<br>KG: Source: GeoSPARQL
- `http://w3id.org/fio/v1/epa-frs#fromSystem`<br>curated: Links a record to the information system it originated from<br>KG: Also used inside class axioms, as owl:onProperty of 12 owl:Restrictions.
- `http://w3id.org/fio/v1/epa-frs#ofInterestType`<br>curated: Links an environmental interest to its classification category<br>KG: Also used inside class axioms, as owl:onProperty of 18 owl:Restrictions.
- `http://w3id.org/fio/v1/fio#ofIndustry`<br>curated: A relation between an entity and the industry it is classified under<br>KG: A relation between an entity and the industry it is classified under Also used inside class axioms, as owl:onProperty of 2 owl:Restrictions.

## gene-expression-atlas-okn

Curated row types: {'Class': 16, 'EdgeProperty': 2, 'NodeProperty': 18, 'Predicate': 7}

**(source class, predicate) only in VoID** (36)

- `biolink:AnatomicalEntity` → `biolink:name`
- `biolink:Assay` → `http://purl.org/okn/wobd/array_design`
- `biolink:Assay` → `http://purl.org/okn/wobd/contrast_id`
- `biolink:Assay` → `http://purl.org/okn/wobd/technology`
- `biolink:Assay` → `biolink:has_attribute`
- `biolink:Assay` → `biolink:name`
- `biolink:Association` → `http://purl.org/okn/wobd/adj_p_value`
- `biolink:Association` → `http://purl.org/okn/wobd/direction`
- `biolink:Association` → `http://purl.org/okn/wobd/effect_size`
- `biolink:Association` → `http://purl.org/okn/wobd/enrichment_source`
- `biolink:Association` → `http://purl.org/okn/wobd/p_value`
- `biolink:Association` → `biolink:object`
- `biolink:Association` → `biolink:predicate`
- `biolink:Association` → `biolink:subject`
- `biolink:Attribute` → `biolink:name`
- `biolink:BiologicalSex` → `biolink:name`
- `biolink:Cell` → `biolink:name`
- `biolink:Disease` → `biolink:name`
- `biolink:Gene` → `biolink:id`
- `biolink:GeneExpressionMixin` → `http://purl.org/okn/wobd/adj_p_value`
- `biolink:GeneExpressionMixin` → `http://purl.org/okn/wobd/direction`
- `biolink:GeneExpressionMixin` → `http://purl.org/okn/wobd/log2fc`
- `biolink:LifeStage` → `biolink:name`
- `biolink:OntologyClass` → `biolink:name`
- `biolink:OrganismTaxon` → `biolink:name`
- … 11 more (see comparison.json)

**(source class, predicate) only curated** (2)

- `biolink:Assay` → `biolink:description`
- `biolink:ProteinDomain` → `biolink:id`

**Edges only in VoID** (22)

- `biolink:Assay` → `biolink:has_attribute` → `biolink:AnatomicalEntity`
- `biolink:Assay` → `biolink:has_attribute` → `biolink:BiologicalSex`
- `biolink:Assay` → `biolink:has_attribute` → `biolink:Cell`
- `biolink:Assay` → `biolink:has_attribute` → `biolink:Disease`
- `biolink:Assay` → `biolink:has_attribute` → `biolink:LifeStage`
- `biolink:Association` → `biolink:object` → `biolink:LifeStage`
- `biolink:Association` → `biolink:object` → `biolink:OntologyClass`
- `biolink:Association` → `biolink:object` → `biolink:Pathway`
- `biolink:Association` → `biolink:object` → `biolink:ProteinDomain`
- `biolink:Association` → `biolink:subject` → `biolink:Assay`
- `biolink:Study` → `biolink:has_attribute` → `biolink:AnatomicalEntity`
- `biolink:Study` → `biolink:has_attribute` → `biolink:Attribute`
- `biolink:Study` → `biolink:has_attribute` → `biolink:BiologicalSex`
- `biolink:Study` → `biolink:has_attribute` → `biolink:Cell`
- `biolink:Study` → `biolink:has_attribute` → `biolink:Disease`
- `biolink:Study` → `biolink:has_attribute` → `biolink:LifeStage`
- `biolink:Study` → `biolink:has_attribute` → `biolink:OntologyClass`
- `biolink:Study` → `biolink:in_taxon` → `biolink:OrganismTaxon`
- `biolink:Study` → `biolink:studies` → `biolink:AnatomicalEntity`
- `biolink:Study` → `biolink:studies` → `biolink:BiologicalSex`
- `biolink:Study` → `biolink:studies` → `biolink:Cell`
- `biolink:Study` → `biolink:studies` → `biolink:LifeStage`

## geoconnex

Curated row types: {'Class': 79, 'Predicate': 257}

**(source class, predicate) only in VoID** (430)

- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/geo`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/identifier`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/name`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/provider`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/url`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://www.opengis.net/def/schema/hy_features/hyf/referencedPosition`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `https://schema.org/geo`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `https://schema.org/identifier`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `https://schema.org/name`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `https://schema.org/provider`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `https://schema.org/url`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `https://www.opengis.net/def/schema/hy_features/hyf/referencedPosition`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://schema.org/geo`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://schema.org/identifier`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://schema.org/name`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://schema.org/provider`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://schema.org/subjectOf`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://schema.org/url`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AT` → `https://www.opengis.net/def/schema/hy_features/hyf/referencedPosition`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/ES` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/ES` → `https://schema.org/geo`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/ES` → `https://schema.org/identifier`
- … 405 more (see comparison.json)

**Edges only in VoID** (298)

- `http://gnis-ld.org/lod/gnis/ontology/County` → `https://schema.org/containedInPlace` → `https://schema.org/AdministrativeArea`
- `http://gnis-ld.org/lod/gnis/ontology/County` → `https://schema.org/containedInPlace` → `https://schema.org/Place`
- `http://gnis-ld.org/lod/gnis/ontology/County` → `https://schema.org/containedInPlace` → `https://schema.org/State`
- `http://gnis-ld.org/lod/gnis/ontology/County` → `https://schema.org/geoWithin` → `https://schema.org/AdministrativeArea`
- `http://gnis-ld.org/lod/gnis/ontology/County` → `https://schema.org/geoWithin` → `https://schema.org/Place`
- `http://gnis-ld.org/lod/gnis/ontology/County` → `https://schema.org/geoWithin` → `https://schema.org/State`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `http://gnis-ld.org/lod/gnis/ontology/county` → `https://schema.org/AdministrativeArea`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `http://gnis-ld.org/lod/gnis/ontology/county` → `https://schema.org/Place`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `http://gnis-ld.org/lod/gnis/ontology/state` → `https://schema.org/AdministrativeArea`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `http://gnis-ld.org/lod/gnis/ontology/state` → `https://schema.org/Place`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `http://gnis-ld.org/lod/gnis/ontology/state` → `https://schema.org/State`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `https://schema.org/containedInPlace` → `https://schema.org/AdministrativeArea`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `https://schema.org/containedInPlace` → `https://schema.org/Place`
- `http://gnis-ld.org/lod/gnis/ontology/Feature` → `https://schema.org/containedInPlace` → `https://schema.org/State`
- `http://www.opengis.net/ont/geosparql#Geometry` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `http://www.opengis.net/ont/sf#GeometryCollection` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `http://www.opengis.net/ont/sf#LineString` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `http://www.opengis.net/ont/sf#MultiPolygon` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `http://www.opengis.net/ont/sf#Point` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `http://www.opengis.net/ont/sf#Polygon` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/sf#Point`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/geo` → `https://schema.org/GeoCoordinates`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/identifier` → `https://schema.org/PropertyValue`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AG` → `https://schema.org/provider` → `https://schema.org/GovernmentOrganization`
- `https://api.waterdata.usgs.gov/ogcapi/v0/collections/site-types/items/AS` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/sf#Point`
- … 273 more (see comparison.json)

## glygenkg

Curated row types: {'Class': 15, 'Predicate': 52}

## hydrologykg

Curated row types: {'Class': 127, 'Predicate': 191}

**Classes only in VoID** (28)

- `rdf:List`
- `rdf:ObjectProperty`
- `rdf:Property`
- `rdfs:Class`
- `rdfs:ContainerMembershipProperty`
- `rdfs:Datatype`
- `rdfs:Resource`
- `owl:AllDisjointClasses`
- `owl:AnnotationProperty`
- `owl:AsymmetricProperty`
- `owl:Class`
- `owl:DataProperty`
- `owl:DatatypeProperty`
- `owl:NamedIndividual`
- `owl:ObjectProperty`
- `owl:Ontology`
- `owl:OntologyProperty`
- `owl:ReflexiveProperty`
- `owl:Restriction`
- `owl:SymmetricProperty`
- `owl:Thing`
- `owl:TransitiveProperty`
- `owl:objectProperty`
- `http://www.w3.org/2003/11/swrl#AtomList`
- `http://www.w3.org/2003/11/swrl#DatavaluedPropertyAtom`
- … 3 more (see comparison.json)

**Classes only curated** (28)

- `http://hyfo.spatialai.org/v1/hyfo#AquiferWaterFeature`
- `http://hyfo.spatialai.org/v1/hyfo#SubsurfaceWaterFeature`
- `http://hyfo.spatialai.org/v1/hyfo#SurfaceWaterFeature`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeature`
- `http://qudt.org/schema/qudt/IntervalScale`
- `http://qudt.org/schema/qudt/NominalScale`
- `http://qudt.org/schema/qudt/NumericUnion`
- `http://qudt.org/schema/qudt/OrdinalScale`
- `http://qudt.org/schema/qudt/RatioScale`
- `http://qudt.org/schema/qudt/Scale`
- `http://qudt.org/schema/qudt/Unit`
- `http://sawgraph.spatialai.org/v1/us-sdwis#CombinedDistributionSystem`
- `http://sawgraph.spatialai.org/v1/us-sdwis#PWS-SubFeature`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_4`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_5`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_6`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/RoadSegment`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/StatisticalArea`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/ZipCodeArea`
- `http://www.opengis.net/ont/geosparql#FeatureCollection`
- `https://www.opengis.net/def/schema/hy_features/hyf/HY_Canal`
- `https://www.opengis.net/def/schema/hy_features/hyf/HY_Catchment`
- `https://www.opengis.net/def/schema/hy_features/hyf/HY_Estuary`
- `https://www.opengis.net/def/schema/hy_features/hyf/HY_Impoundment`
- … 3 more (see comparison.json)

**Predicates only in VoID** (74)

- `http://sawgraph.spatialai.org/v1/us-sdwis#buysFrom`
- `http://sawgraph.spatialai.org/v1/us-sdwis#hasPart`
- `http://sawgraph.spatialai.org/v1/us-sdwis#hasPermanentSource`
- `http://sawgraph.spatialai.org/v1/us-sdwis#hasSource`
- `http://sawgraph.spatialai.org/v1/us-sdwis#inCombinedSystem`
- `http://sawgraph.spatialai.org/v1/us-sdwis#partOf`
- `http://sawgraph.spatialai.org/v1/us-sdwis#sellsTo`
- `http://sawgraph.spatialai.org/v1/us-sdwis#sourceFor`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfEquals`
- `http://swrl.stanford.edu/ontologies/3.3/swrla.owl#isRuleEnabled`
- `http://www.semanticweb.org/efive/aggFilterOnDataProp`
- `http://www.semanticweb.org/efive/hasAggVar`
- `http://www.semanticweb.org/efive/hasIQR`
- `http://www.semanticweb.org/efive/hasMode`
- `rdf:first`
- `rdf:langRange`
- `rdf:rest`
- `rdfs:comment`
- `rdfs:domain`
- `rdfs:isDefinedBy`
- `rdfs:range`
- `rdfs:seeAlso`
- `rdfs:subClassOf`
- `rdfs:subPropertyOf`
- … 49 more (see comparison.json)

**(source class, predicate) only in VoID** (1052)

- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `rdfs:label`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `owl:sameAs`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `rdfs:comment`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `rdfs:label`
- `http://gwml2.org/def/gwml2#GW_AquiferSystem` → `owl:sameAs`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://nhdplusv2.spatialai.org/v1/nhdplusv2#hasCOMID`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://nhdplusv2.spatialai.org/v1/nhdplusv2#hasFCODE`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://nhdplusv2.spatialai.org/v1/nhdplusv2#hasFTYPE`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://nhdplusv2.spatialai.org/v1/nhdplusv2#hasFlowPathLength`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://nhdplusv2.spatialai.org/v1/nhdplusv2#hasReachCode`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `dct:title`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfCrosses`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfTouches`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://hyfo.spatialai.org/v1/hyfo#WaterFeatureRepresentation` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation`
- … 1027 more (see comparison.json)

**Edges only in VoID** (4391)

- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://gwml2.org/def/gwml2#gwAquiferSystem` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://gwml2.org/def/gwml2#gwAquiferSystem` → `owl:Thing`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Cell`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Region`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `owl:Thing`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Cell`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Region`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `owl:Thing`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Cell`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/Region`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://gwml2.org/def/gwml2#GW_Aquifer` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `owl:Thing`
- … 4366 more (see comparison.json)

**Descriptions that differ** (79)

- `obo:OBI_0200000`<br>curated: A planned process that produces output data from input data (OBI). Here the type of the six algorithms used to compute the dataset summaries.<br>KG: A planned process that produces output data from input data.
- `http://purl.org/spatialai/stad/v2/core/DatasetDescription`<br>curated: The extended stad:DatasetDescription class for describing datasets.<br>KG: The extended stad:DatasetDescription class for describing datasets
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`<br>curated: Administrative regions as defined by GADM.<br>KG: Administrative regoins as defined by the Global Administrative Area Database (GADM); see https://gadm.org/metadata.html
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`<br>curated: GADM level 1 administrative regions (states, provinces).<br>KG: GADM level 1 administrative regions which are the highest level of division of a country, such as US states, Canadian provinces, or French departments.
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`<br>curated: GADM level 2 administrative regions (counties).<br>KG: GADM level 2 administrative regions which further subdivide states, provinces, or departments. Examples include counties in the US
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3`<br>curated: GADM level 3 administrative regions (county subdivisions).<br>KG: GADM level 3 administrative regions. In the US, these are subdivisions of counties, formally known as county subdivisions, such as minor civil divisions (e.g. towns ot townships) or census county divi
- `http://www.opengis.net/ont/geosparql#Feature`<br>curated: A discrete spatial phenomenon in a universe of discourse.<br>KG: Source: GeoSPARQL
- `http://www.opengis.net/ont/geosparql#Geometry`<br>curated: A coherent set of direct positions in space. The positions are held within a Spatial Reference System (SRS).<br>KG: Source: GeoSPARQL
- `http://www.opengis.net/ont/geosparql#SpatialObject`<br>curated: Anything spatial (being or having a shape, position or an extent).<br>KG: Source: GeoSPARQL
- `http://www.semanticweb.org/efive/AggregateIntervalVariable`<br>curated: The interval variable of interest for a :StatisticalSummary.<br>KG: The interval variable of interest for a :StatisticalSummary
- … 69 more (see comparison.json)

## medical-device-kg

Curated row types: {'Class': 66, 'Predicate': 505}

**Classes only in VoID** (1)

- `rdf:Property`

**Classes only curated** (31)

- `http://medicaldevice.com/ontology/AccessGUDIDRecord`
- `http://medicaldevice.com/ontology/AdverseEventReport`
- `http://medicaldevice.com/ontology/Analyte`
- `http://medicaldevice.com/ontology/ApprovalPathway`
- `http://medicaldevice.com/ontology/CLIARecord`
- `http://medicaldevice.com/ontology/CLIAWaivedRecord`
- `http://medicaldevice.com/ontology/Component`
- `http://medicaldevice.com/ontology/Dataset`
- `http://medicaldevice.com/ontology/DesignChange`
- `http://medicaldevice.com/ontology/DeviceComponent`
- `http://medicaldevice.com/ontology/DeviceIdentifier`
- `http://medicaldevice.com/ontology/DeviceListing`
- `http://medicaldevice.com/ontology/DeviceMaterial`
- `http://medicaldevice.com/ontology/DevicesFDARecord`
- `http://medicaldevice.com/ontology/FDADataRecord`
- `http://medicaldevice.com/ontology/GMDNTerm`
- `http://medicaldevice.com/ontology/HDERecord`
- `http://medicaldevice.com/ontology/IVDRecord`
- `http://medicaldevice.com/ontology/Material`
- `http://medicaldevice.com/ontology/MedSunReport`
- `http://medicaldevice.com/ontology/ProvenanceRecord`
- `http://medicaldevice.com/ontology/RecognizedStandard`
- `http://medicaldevice.com/ontology/RegulatorySubmission`
- `http://medicaldevice.com/ontology/SafetyReport`
- `http://medicaldevice.com/ontology/SafetySignal`
- … 6 more (see comparison.json)

**Predicates only curated** (152)

- `http://medicaldevice.com/ontology/accreditationBody`
- `http://medicaldevice.com/ontology/adverseEventFlag`
- `http://medicaldevice.com/ontology/affectsComponent`
- `http://medicaldevice.com/ontology/affectsLabeling`
- `http://medicaldevice.com/ontology/affectsMaterial`
- `http://medicaldevice.com/ontology/affectsPackaging`
- `http://medicaldevice.com/ontology/affectsSoftware`
- `http://medicaldevice.com/ontology/affectsSterility`
- `http://medicaldevice.com/ontology/analyteId`
- `http://medicaldevice.com/ontology/approvalDate`
- `http://medicaldevice.com/ontology/ascaPilot`
- `http://medicaldevice.com/ontology/assemblerAddress`
- `http://medicaldevice.com/ontology/assemblerName`
- `http://medicaldevice.com/ontology/belongsToDevice`
- `http://medicaldevice.com/ontology/brandName`
- `http://medicaldevice.com/ontology/catalogNumber`
- `http://medicaldevice.com/ontology/certificateNumber`
- `http://medicaldevice.com/ontology/changeDescription`
- `http://medicaldevice.com/ontology/changeReason`
- `http://medicaldevice.com/ontology/commercialDistributionStatus`
- `http://medicaldevice.com/ontology/companyName`
- `http://medicaldevice.com/ontology/complexity`
- `http://medicaldevice.com/ontology/componentDescription`
- `http://medicaldevice.com/ontology/dateEffective`
- `http://medicaldevice.com/ontology/dateOrder`
- … 127 more (see comparison.json)

**(source class, predicate) only in VoID** (45)

- `http://asu.edu/semantics/SUDOKN/NAICSClassifier` → `http://medicaldevice.com/ontology/naicsCode`
- `http://asu.edu/semantics/SUDOKN/NAICSClassifier` → `http://medicaldevice.com/ontology/naicsVersion`
- `http://asu.edu/semantics/SUDOKN/NAICSClassifier` → `rdfs:label`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/establishmentName`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/feiNumber`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/hasManufacturer`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/initialImporterFlag`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/regExpiryDateYear`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/registrationAddress`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/registrationNumber`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/registrationStatus`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/retrievedAt`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/sourceDataset`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/sourceRecordId`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/sourceUrl`
- `http://medicaldevice.com/ontology/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasNAICSClassifier`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://medicaldevice.com/ontology/geocodingConfidence`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://medicaldevice.com/ontology/geocodingSource`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://medicaldevice.com/ontology/normalizedAddress`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://www.w3.org/2003/01/geo/wgs84_pos#lat`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://www.w3.org/2003/01/geo/wgs84_pos#long`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://medicaldevice.com/ontology/establishmentName`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://medicaldevice.com/ontology/feiNumber`
- … 20 more (see comparison.json)

**(source class, predicate) only curated** (20)

- `http://medicaldevice.com/ontology/AccessGUDIDRecord` → `http://medicaldevice.com/ontology/hasIdentifier`
- `http://medicaldevice.com/ontology/CLIARecord` → `http://medicaldevice.com/ontology/hasSpecialty`
- `http://medicaldevice.com/ontology/CLIARecord` → `http://medicaldevice.com/ontology/hasTestSystem`
- `http://medicaldevice.com/ontology/DeviceListing` → `http://medicaldevice.com/ontology/registeredAt`
- `http://medicaldevice.com/ontology/Manufacturer` → `http://medicaldevice.com/ontology/hasRegistrationRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/has510kRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasAccessGUDIDRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasDeNovoRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasDesignChange`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasHDERecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasMAUDEReport`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasMedSunReport`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasPMADesignChange`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasPMARecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasRecallRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasTPLCRecord`
- `http://medicaldevice.com/ontology/ProductCode` → `http://medicaldevice.com/ontology/hasClassificationRecord`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://medicaldevice.com/ontology/hasDeviceListing`
- `http://medicaldevice.com/ontology/TPLCRecord` → `http://medicaldevice.com/ontology/hasMDRStatistic`
- `http://medicaldevice.com/ontology/UDIIdentifier` → `http://medicaldevice.com/ontology/belongsToDevice`

**Edges only in VoID** (27)

- `http://medicaldevice.com/ontology/DeNovoRecord` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/DeviceFDARecord` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/hasManufacturer` → `http://medicaldevice.com/ontology/Manufacturer`
- `http://medicaldevice.com/ontology/Facility` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/HumanitarianDeviceExemption` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/K510Record` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasNAICSClassifier` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `http://medicaldevice.com/ontology/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasNAICSClassifier` → `http://medicaldevice.com/ontology/NAICSClassification`
- `http://medicaldevice.com/ontology/Manufacturer` → `http://medicaldevice.com/ontology/hasNAICSClassification` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `http://medicaldevice.com/ontology/PMAChangeMemo` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/PMARecord` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/ProductClassificationRecord` → `http://medicaldevice.com/ontology/hasNAICSClassification` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `http://medicaldevice.com/ontology/ProductCode` → `http://medicaldevice.com/ontology/hasNAICSClassification` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `http://medicaldevice.com/ontology/ProductCodeNAICSMapping` → `http://medicaldevice.com/ontology/assignedNAICS` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `http://medicaldevice.com/ontology/Recall` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/RecallRecord` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://www.opengis.net/ont/geosparql#defaultGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://medicaldevice.com/ontology/hasManufacturer` → `http://medicaldevice.com/ontology/Manufacturer`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://medicaldevice.com/ontology/hasManufacturer` → `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://www.opengis.net/ont/geosparql#defaultGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`
- `http://www.opengis.net/ont/geosparql#Geometry` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasNAICSClassifier` → `http://medicaldevice.com/ontology/NAICSClassification`
- … 2 more (see comparison.json)

**Edges only curated** (20)

- `http://medicaldevice.com/ontology/AccessGUDIDRecord` → `http://medicaldevice.com/ontology/hasIdentifier` → `http://medicaldevice.com/ontology/UDIIdentifier`
- `http://medicaldevice.com/ontology/CLIARecord` → `http://medicaldevice.com/ontology/hasSpecialty` → `http://medicaldevice.com/ontology/Specialty`
- `http://medicaldevice.com/ontology/CLIARecord` → `http://medicaldevice.com/ontology/hasTestSystem` → `http://medicaldevice.com/ontology/TestSystem`
- `http://medicaldevice.com/ontology/DeviceListing` → `http://medicaldevice.com/ontology/registeredAt` → `http://medicaldevice.com/ontology/RegistrationListingRecord`
- `http://medicaldevice.com/ontology/Manufacturer` → `http://medicaldevice.com/ontology/hasRegistrationRecord` → `http://medicaldevice.com/ontology/RegistrationListingRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/has510kRecord` → `http://medicaldevice.com/ontology/K510Record`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasAccessGUDIDRecord` → `http://medicaldevice.com/ontology/AccessGUDIDRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasDeNovoRecord` → `http://medicaldevice.com/ontology/DeNovoRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasDesignChange` → `http://medicaldevice.com/ontology/PMAChangeMemo`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasHDERecord` → `http://medicaldevice.com/ontology/HDERecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasMAUDEReport` → `http://medicaldevice.com/ontology/MAUDEReport`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasMedSunReport` → `http://medicaldevice.com/ontology/MedSunReport`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasPMADesignChange` → `http://medicaldevice.com/ontology/PMAChangeMemo`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasPMARecord` → `http://medicaldevice.com/ontology/PMARecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasRecallRecord` → `http://medicaldevice.com/ontology/RecallRecord`
- `http://medicaldevice.com/ontology/MedicalDevice` → `http://medicaldevice.com/ontology/hasTPLCRecord` → `http://medicaldevice.com/ontology/TPLCRecord`
- `http://medicaldevice.com/ontology/ProductCode` → `http://medicaldevice.com/ontology/hasClassificationRecord` → `http://medicaldevice.com/ontology/ProductClassificationRecord`
- `http://medicaldevice.com/ontology/RegistrationListingRecord` → `http://medicaldevice.com/ontology/hasDeviceListing` → `http://medicaldevice.com/ontology/DeviceListing`
- `http://medicaldevice.com/ontology/TPLCRecord` → `http://medicaldevice.com/ontology/hasMDRStatistic` → `http://medicaldevice.com/ontology/MDRStatistic`
- `http://medicaldevice.com/ontology/UDIIdentifier` → `http://medicaldevice.com/ontology/belongsToDevice` → `http://medicaldevice.com/ontology/AccessGUDIDRecord`

## nasa-gesdisc-kg

Curated row types: {'Class': 10, 'Predicate': 41}

**(source class, predicate) only in VoID** (17)

- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Author` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/DataCenter` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/DataCenter` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Dataset` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Dataset` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Institution` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Institution` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Instrument` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Instrument` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Platform` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Platform` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Project` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Project` → `rdfs:label`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/Publication` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/ScienceKeyword` → `dct:identifier`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/ScienceKeyword` → `rdfs:label`

**Edge properties (predicate, property) only in VoID** (4)

- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/CO_USED_WITH` → `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/derived`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/CO_USED_WITH` → `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/weight`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/WORKS_WITH_DATASET` → `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/derived`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/WORKS_WITH_DATASET` → `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/weight`

**Edge properties (predicate, property) only curated** (2)

- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/CO_USED_WITH|https://purl.org/okn/frink/kg/nasa-gesdisc/schema/WORKS_WITH_DATASET` → `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/derived`
- `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/CO_USED_WITH|https://purl.org/okn/frink/kg/nasa-gesdisc/schema/WORKS_WITH_DATASET` → `https://purl.org/okn/frink/kg/nasa-gesdisc/schema/weight`

## ncipidkg

Curated row types: {'Class': 6, 'Predicate': 78}

**Classes only in VoID** (1)

- `owl:ObjectProperty`

**(source class, predicate) only in VoID** (2)

- `owl:ObjectProperty` → `rdfs:domain`
- `owl:ObjectProperty` → `rdfs:range`

**Descriptions that differ** (45)

- `obo:CHEBI_23367`<br>curated: Any constitutionally or isotopically distinct atom, molecule, ion, ion pair, radical, radical ion, complex, conformer etc., identifiable as a separately distinguishable entity. Chemicals appear here a<br>KG: Any constitutionally or isotopically distinct atom, molecule, ion, ion pair, radical, radical ion, complex, conformer etc., identifiable as a separately distinguishable entity.
- `obo:SO_0000655`<br>curated: An RNA transcript that does not encode for a protein rather the RNA molecule is the gene product.<br>KG: A ncRNA is a processed_transcript, so it may not contain parts such as transcribed_spacer_regions that are removed in the act of processing. For the corresponding primary_transcripts, please see term 
- `obo:RO_0000056`<br>curated: A relation between a continuant and a process, in which the continuant is somehow involved in the process.<br>KG: a relation between a continuant and a process, in which the continuant is somehow involved in the process
- `obo:RO_0000056`<br>curated: A relation between a continuant and a process, in which the continuant is somehow involved in the process.<br>KG: a relation between a continuant and a process, in which the continuant is somehow involved in the process
- `obo:RO_0000056`<br>curated: A relation between a continuant and a process, in which the continuant is somehow involved in the process.<br>KG: a relation between a continuant and a process, in which the continuant is somehow involved in the process
- `obo:RO_0000056`<br>curated: A relation between a continuant and a process, in which the continuant is somehow involved in the process.<br>KG: a relation between a continuant and a process, in which the continuant is somehow involved in the process
- `obo:RO_0002211`<br>curated: x regulates y if x has an effect on the frequency, rate, or extent of y.<br>KG: p regulates q iff p is causally upstream of q, the execution of p is not constant and varies according to specific conditions, and p influences the rate or magnitude of execution of q due to an effect
- `obo:RO_0002211`<br>curated: x regulates y if x has an effect on the frequency, rate, or extent of y.<br>KG: p regulates q iff p is causally upstream of q, the execution of p is not constant and varies according to specific conditions, and p influences the rate or magnitude of execution of q due to an effect
- `obo:RO_0002211`<br>curated: x regulates y if x has an effect on the frequency, rate, or extent of y.<br>KG: p regulates q iff p is causally upstream of q, the execution of p is not constant and varies according to specific conditions, and p influences the rate or magnitude of execution of q due to an effect
- `obo:RO_0002211`<br>curated: x regulates y if x has an effect on the frequency, rate, or extent of y.<br>KG: p regulates q iff p is causally upstream of q, the execution of p is not constant and varies according to specific conditions, and p influences the rate or magnitude of execution of q due to an effect
- … 35 more (see comparison.json)

## nde

Curated row types: {'Class': 10, 'Predicate': 29}

**Classes only curated** (3)

- `schema:DataDownload`
- `schema:ResearchProject`
- `schema:ScholarlyArticle`

**(source class, predicate) only in VoID** (1)

- `schema:Dataset` → `owl:sameAs`

**(source class, predicate) only curated** (3)

- `Property` → `rdfs:domain`
- `Property` → `rdfs:range`
- `Thing` → `owl:sameAs`

**Edges only curated** (35)

- `Property` → `rdfs:domain` → `rdfs:Class`
- `Property` → `rdfs:range` → `rdfs:Class`
- `Thing` → `owl:sameAs` → `Thing`
- `schema:DataCatalog` → `schema:archivedAt` → `Literal (string)`
- `schema:DataCatalog` → `schema:name` → `Literal (string)`
- `schema:DataCatalog` → `schema:url` → `Literal (string)`
- `schema:DataCatalog` → `schema:versionDate` → `Literal (date`
- `schema:DataCatalog` → `schema:versionDate` → `dateTime)`
- `schema:Dataset` → `schema:abstract` → `Literal (string)`
- `schema:Dataset` → `schema:author` → `Literal (string)`
- `schema:Dataset` → `schema:date` → `Literal (date)`
- `schema:Dataset` → `schema:dateCreated` → `Literal (date)`
- `schema:Dataset` → `schema:dateModified` → `Literal (date`
- `schema:Dataset` → `schema:dateModified` → `dateTime)`
- `schema:Dataset` → `schema:datePublished` → `Literal (date)`
- `schema:Dataset` → `schema:description` → `Literal (string)`
- `schema:Dataset` → `schema:identifier` → `Literal (string)`
- `schema:Dataset` → `schema:name` → `Literal (string)`
- `schema:Dataset` → `schema:sameAs` → `Literal (string)`
- `schema:Dataset` → `schema:url` → `Literal (string)`
- `schema:DefinedTerm` → `schema:name` → `Literal (string)`
- `schema:MonetaryGrant` → `schema:endDate` → `Literal (date)`
- `schema:MonetaryGrant` → `schema:identifier` → `Literal (string)`
- `schema:MonetaryGrant` → `schema:name` → `Literal (string)`
- `schema:MonetaryGrant` → `schema:startDate` → `Literal (date)`
- … 10 more (see comparison.json)

**Curated class labels that resolve to no URI** (6)

- `Literal (date`
- `Literal (date)`
- `Literal (string)`
- `Property`
- `Thing`
- `dateTime)`

## nestkg

Curated row types: {'Class': 9, 'Predicate': 34}

**Classes only in VoID** (2)

- `rdf:Property`
- `owl:DatatypeProperty`

**(source class, predicate) only in VoID** (18)

- `rdf:Property` → `rdfs:comment`
- `rdf:Property` → `rdfs:domain`
- `rdf:Property` → `rdfs:label`
- `rdf:Property` → `rdfs:range`
- `rdf:Property` → `rdfs:seeAlso`
- `rdf:Property` → `rdfs:subPropertyOf`
- `rdfs:Class` → `rdfs:comment`
- `rdfs:Class` → `rdfs:label`
- `rdfs:Class` → `rdfs:subClassOf`
- `owl:Class` → `rdfs:comment`
- `owl:Class` → `rdfs:label`
- `owl:Class` → `rdfs:subClassOf`
- `owl:DatatypeProperty` → `rdfs:comment`
- `owl:DatatypeProperty` → `rdfs:domain`
- `owl:DatatypeProperty` → `rdfs:label`
- `owl:DatatypeProperty` → `rdfs:range`
- `owl:DatatypeProperty` → `rdfs:seeAlso`
- `owl:DatatypeProperty` → `rdfs:subPropertyOf`

**Edges only in VoID** (4)

- `rdf:Property` → `rdfs:domain` → `rdfs:Class`
- `rdf:Property` → `rdfs:domain` → `owl:Class`
- `owl:DatatypeProperty` → `rdfs:domain` → `rdfs:Class`
- `owl:DatatypeProperty` → `rdfs:domain` → `owl:Class`

**Edges only curated** (5)

- `http://semanticscience.org/resource/SIO_010035` → `biolink:interacts_with` → `http://semanticscience.org/resource/SIO_010035`
- `biolink:Association` → `https://www.ndexbio.org/vocab/nest/tumorsMutatedFraction` → `xsd:double`
- `https://www.ndexbio.org/vocab/ProteinSystem` → `https://www.ndexbio.org/vocab/memberCount` → `xsd:nonNegativeInteger`
- `https://www.ndexbio.org/vocab/ProteinSystem` → `https://www.ndexbio.org/vocab/nest/hisigAdjustedPValue` → `xsd:double`
- `https://www.ndexbio.org/vocab/ProteinSystem` → `https://www.ndexbio.org/vocab/nest/hisigWeight` → `xsd:double`

## nikg

Curated row types: {'Class': 7, 'Predicate': 18}

**Classes only in VoID** (1)

- `http://www.opengis.net/ont/sf#Point`

**Classes only curated** (3)

- `https://metadata.phila.gov/BlockGroup`
- `https://metadata.phila.gov/mesh_D000091368`
- `https://metadata.phila.gov/mesh_D005842`

**Predicates only in VoID** (2)

- `http://www.opengis.net/ont/geosparql#asWKT`
- `https://metadata.phila.gov/happened_at`

**Predicates only curated** (10)

- `dct:date`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://www.opengis.net/ont/sf#sfWithin`
- `https://metadata.phila.gov/IsArrest`
- `https://metadata.phila.gov/IsDomestic`
- `https://metadata.phila.gov/OffenderWound`
- `https://metadata.phila.gov/date_of`
- `https://metadata.phila.gov/time_of`
- `https://metadata.phila.gov/type_of`
- `https://schema.org/location`

**(source class, predicate) only in VoID** (10)

- `http://www.opengis.net/ont/sf#Point` → `http://www.opengis.net/ont/geosparql#asWKT`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/OffenderDeceased`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/OffenderInjured`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/OffenderRace`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/OffenderSex`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/OfficerInvolved`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/age_of`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/happened_at`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/is_fatal`
- `https://metadata.phila.gov/Location` → `http://www.opengis.net/ont/geosparql#hasGeometry`

**(source class, predicate) only curated** (1)

- `geo:Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry`

**Edges only in VoID** (4)

- `http://www.opengis.net/ont/sf#Point` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/age_of` → `http://qudt.org/vocab/unit/YR`
- `https://metadata.phila.gov/Incident` → `https://metadata.phila.gov/happened_at` → `https://metadata.phila.gov/CensusTract`
- `https://metadata.phila.gov/Location` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/sf#Point`

**Edges only curated** (1)

- `geo:Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `geo:Geometry`

**Curated class labels that resolve to no URI** (2)

- `geo:Feature`
- `geo:Geometry`

## oard-kg

Curated row types: {'Class': 9, 'Predicate': 16}

**(source class, predicate) only in VoID** (17)

- `biolink:ConceptCountAnalysisResult` → `biolink:category`
- `biolink:ConceptCountAnalysisResult` → `biolink:concept_count_object`
- `biolink:ConceptCountAnalysisResult` → `biolink:concept_count_subject`
- `biolink:ConceptCountAnalysisResult` → `biolink:concept_pair_count`
- `biolink:ConceptCountAnalysisResult` → `biolink:dataset_count`
- `biolink:ConceptCountAnalysisResult` → `biolink:supporting_data_set`
- `biolink:Dataset` → `biolink:category`
- `biolink:Disease` → `biolink:category`
- `biolink:DiseaseToPhenotypicFeatureAssociation` → `biolink:category`
- `biolink:EntityToDiseaseAssociation` → `biolink:category`
- `biolink:LogOddsAnalysisResult` → `biolink:category`
- `biolink:LogOddsAnalysisResult` → `biolink:log_odds_ratio`
- `biolink:LogOddsAnalysisResult` → `biolink:log_odds_ratio_95_ci`
- `biolink:LogOddsAnalysisResult` → `biolink:total_sample_size`
- `biolink:PhenotypicFeature` → `biolink:category`
- `biolink:PhenotypicFeatureToPhenotypicFeatureAssociation` → `biolink:category`
- `biolink:Study` → `biolink:category`

**Edges only in VoID** (1)

- `biolink:ConceptCountAnalysisResult` → `biolink:supporting_data_set` → `biolink:Dataset`

**Edges only curated** (6)

- `biolink:DiseaseToPhenotypicFeatureAssociation` → `biolink:object` → `biolink:Disease`
- `biolink:DiseaseToPhenotypicFeatureAssociation` → `biolink:subject` → `biolink:PhenotypicFeature`
- `biolink:EntityToDiseaseAssociation` → `biolink:object` → `biolink:PhenotypicFeature`
- `biolink:EntityToDiseaseAssociation` → `biolink:subject` → `biolink:PhenotypicFeature`
- `biolink:PhenotypicFeatureToPhenotypicFeatureAssociation` → `biolink:object` → `biolink:Disease`
- `biolink:PhenotypicFeatureToPhenotypicFeatureAssociation` → `biolink:subject` → `biolink:Disease`

**Edge properties (predicate, property) only curated** (9)

- `biolink:has_study_results` → `biolink:category`
- `biolink:has_study_results` → `biolink:concept_count_object`
- `biolink:has_study_results` → `biolink:concept_count_subject`
- `biolink:has_study_results` → `biolink:concept_pair_count`
- `biolink:has_study_results` → `biolink:dataset_count`
- `biolink:has_study_results` → `biolink:log_odds_ratio`
- `biolink:has_study_results` → `biolink:log_odds_ratio_95_ci`
- `biolink:has_study_results` → `biolink:supporting_data_set`
- `biolink:has_study_results` → `biolink:total_sample_size`

## pankgraph

Curated row types: {'Class': 13, 'Predicate': 102}

**(source class, predicate) only in VoID** (62)

- `obo:SO_0000694` → `dct:source`
- `obo:SO_0000694` → `rdfs:seeAlso`
- `obo:SO_0000694` → `kg:schema/data_version`
- `obo:SO_0000694` → `biolink:affects_expression_of`
- `obo:SO_0001483` → `dct:source`
- `obo:SO_0001483` → `rdfs:seeAlso`
- `obo:SO_0001483` → `kg:schema/data_version`
- `obo:SO_0001747` → `dct:source`
- `obo:SO_0001747` → `kg:schema/data_version`
- `obo:SO_0001747` → `biolink:associated_with`
- `kg:schema/T1D` → `dct:source`
- `kg:schema/T1D` → `rdfs:comment`
- `kg:schema/T1D` → `rdfs:label`
- `kg:schema/T1D` → `rdfs:seeAlso`
- `kg:schema/T1D` → `kg:schema/data_version`
- `kg:schema/T1D` → `biolink:synonym`
- `kg:schema/gene_ontology` → `rdfs:seeAlso`
- `kg:schema/gene_ontology` → `kg:schema/data_version`
- `kg:schema/go` → `rdfs:seeAlso`
- `kg:schema/go` → `kg:schema/data_version`
- `biolink:Article` → `dct:title`
- `biolink:Article` → `kg:schema/consortium`
- `biolink:Article` → `kg:schema/pmcid`
- `biolink:Article` → `kg:schema/pubdate`
- `biolink:Article` → `kg:schema/pubmedid`
- … 37 more (see comparison.json)

**(source class, predicate) only curated** (2)

- `obo:SO_0000694` → `biolink:associated_with`
- `biolink:OntologyClass` → `biolink:related_to`

**Edges only in VoID** (27)

- `obo:SO_0000694` → `biolink:affects_expression_of` → `biolink:Gene`
- `obo:SO_0001747` → `biolink:associated_with` → `biolink:Cell`
- `obo:SO_0001747` → `biolink:associated_with` → `biolink:CellLine`
- `obo:SO_0001747` → `biolink:associated_with` → `biolink:OntologyClass`
- `obo:SO_0001747` → `biolink:located_in` → `biolink:Gene`
- `rdf:Statement` → `rdf:object` → `kg:schema/T1D`
- `rdf:Statement` → `rdf:object` → `kg:schema/gene_ontology`
- `rdf:Statement` → `rdf:object` → `kg:schema/go`
- `rdf:Statement` → `rdf:object` → `biolink:Cell`
- `rdf:Statement` → `rdf:object` → `biolink:CellLine`
- `rdf:Statement` → `rdf:object` → `biolink:Disease`
- `rdf:Statement` → `rdf:object` → `biolink:Gene`
- `rdf:Statement` → `rdf:object` → `biolink:OntologyClass`
- `rdf:Statement` → `rdf:subject` → `obo:SO_0000694`
- `rdf:Statement` → `rdf:subject` → `obo:SO_0001483`
- `rdf:Statement` → `rdf:subject` → `obo:SO_0001747`
- `rdf:Statement` → `rdf:subject` → `biolink:Article`
- `rdf:Statement` → `rdf:subject` → `biolink:Gene`
- `biolink:Article` → `biolink:related_to` → `kg:schema/gene_ontology`
- `biolink:Article` → `biolink:related_to` → `kg:schema/go`
- `biolink:Article` → `biolink:related_to` → `biolink:OntologyClass`
- `biolink:Gene` → `biolink:expressed_in` → `biolink:CellLine`
- `biolink:Gene` → `biolink:expressed_in` → `biolink:OntologyClass`
- `biolink:Gene` → `biolink:functional_association` → `kg:schema/gene_ontology`
- `biolink:Gene` → `biolink:functional_association` → `kg:schema/go`
- … 2 more (see comparison.json)

**Edges only curated** (3)

- `obo:SO_0000694` → `biolink:associated_with` → `kg:schema/T1D`
- `obo:SO_0001747` → `biolink:located_in` → `biolink:Cell`
- `biolink:OntologyClass` → `biolink:related_to` → `biolink:OntologyClass`

**Edge properties (predicate, property) only in VoID** (34)

- `biolink:affects_expression_of` → `dct:source`
- `biolink:affects_expression_of` → `kg:schema/data_version`
- `biolink:affects_expression_of` → `kg:schema/purity`
- `biolink:affects_expression_of` → `kg:schema/tissue_id`
- `biolink:affects_expression_of` → `kg:schema/tissue_name`
- `biolink:associated_with` → `dct:source`
- `biolink:associated_with` → `kg:schema/AAB_pos__OCR_GeneActivityScore_mean`
- `biolink:associated_with` → `kg:schema/AAB_pos__OCR_GeneActivityScore_median`
- `biolink:associated_with` → `kg:schema/OCR_GeneActivityScore_mean`
- `biolink:associated_with` → `kg:schema/OCR_GeneActivityScore_median`
- `biolink:associated_with` → `kg:schema/data_version`
- `biolink:associated_with` → `kg:schema/non_diabetic__OCR_GeneActivityScore_mean`
- `biolink:associated_with` → `kg:schema/non_diabetic__OCR_GeneActivityScore_median`
- `biolink:associated_with` → `kg:schema/type_1_diabetes__OCR_GeneActivityScore_mean`
- `biolink:associated_with` → `kg:schema/type_1_diabetes__OCR_GeneActivityScore_median`
- `biolink:associated_with` → `kg:schema/type_2_diabetes__OCR_GeneActivityScore_mean`
- `biolink:associated_with` → `kg:schema/type_2_diabetes__OCR_GeneActivityScore_median`
- `biolink:expressed_in` → `dct:source`
- `biolink:expressed_in` → `kg:schema/Adjusted_P_value`
- `biolink:expressed_in` → `kg:schema/Log2FoldChange`
- `biolink:expressed_in` → `kg:schema/P_value`
- `biolink:expressed_in` → `kg:schema/SE_of_Log2FoldChange`
- `biolink:expressed_in` → `kg:schema/UpOrDownRegulation`
- `biolink:expressed_in` → `kg:schema/data_version`
- `biolink:functional_association` → `dct:source`
- … 9 more (see comparison.json)

**Edge properties (predicate, property) only curated** (31)

- `biolink:affects_expression_of` → `kg:schema/AAB_pos__OCR_GeneActivityScore_mean`
- `biolink:affects_expression_of` → `kg:schema/AAB_pos__OCR_GeneActivityScore_median`
- `biolink:affects_expression_of` → `kg:schema/Adjusted_P_value`
- `biolink:affects_expression_of` → `kg:schema/Log2FoldChange`
- `biolink:affects_expression_of` → `kg:schema/OCR_GeneActivityScore_mean`
- `biolink:affects_expression_of` → `kg:schema/OCR_GeneActivityScore_median`
- `biolink:affects_expression_of` → `kg:schema/P_value`
- `biolink:affects_expression_of` → `kg:schema/SE_of_Log2FoldChange`
- `biolink:affects_expression_of` → `kg:schema/chr`
- `biolink:affects_expression_of` → `kg:schema/end_loc`
- `biolink:affects_expression_of` → `kg:schema/gencode_annotation`
- `biolink:affects_expression_of` → `kg:schema/id_version`
- `biolink:affects_expression_of` → `kg:schema/non_diabetic__OCR_GeneActivityScore_mean`
- `biolink:affects_expression_of` → `kg:schema/non_diabetic__OCR_GeneActivityScore_median`
- `biolink:affects_expression_of` → `kg:schema/start_loc`
- `biolink:affects_expression_of` → `kg:schema/strand`
- `biolink:affects_expression_of` → `kg:schema/type_1_diabetes__OCR_GeneActivityScore_mean`
- `biolink:affects_expression_of` → `kg:schema/type_1_diabetes__OCR_GeneActivityScore_median`
- `biolink:affects_expression_of` → `kg:schema/type_2_diabetes__OCR_GeneActivityScore_mean`
- `biolink:affects_expression_of` → `kg:schema/type_2_diabetes__OCR_GeneActivityScore_median`
- `biolink:expressed_in` → `kg:schema/purity`
- `biolink:expressed_in` → `kg:schema/tissue_id`
- `biolink:expressed_in` → `kg:schema/tissue_name`
- `biolink:gene_associated_with_condition` → `kg:schema/UpOrDownRegulation`
- `biolink:gene_associated_with_condition` → `kg:schema/author`
- … 6 more (see comparison.json)

**Descriptions that differ** (3)

- `obo:SO_0000694`<br>curated: A single nucleotide polymorphism; a single-base sequence variant that is polymorphic in a population.<br>KG: SNPs are single base pair positions in genomic DNA at which different sequence alternatives exist in normal individuals in some population(s), wherein the least frequent variant has an abundance of 1%
- `obo:SO_0001483`<br>curated: A single nucleotide variant; a genomic position at which different single-nucleotide alternatives exist.<br>KG: SNVs are single nucleotide positions in genomic DNA at which different sequence alternatives exist.
- `obo:SO_0001747`<br>curated: A DNA region corresponding to an unfolded, accessible stretch of chromatin.<br>KG: Requested by John Calley 3125900.

## phaseskg

Curated row types: {'Class': 92, 'Predicate': 90}

**Classes only in VoID** (2)

- `owl:AnnotationProperty`
- `owl:ObjectProperty`

**Classes only curated** (80)

- `http://humanbehaviourchange.org/ontology/BCIO_003000`
- `http://humanbehaviourchange.org/ontology/BCIO_006014`
- `http://humanbehaviourchange.org/ontology/BCIO_006064`
- `http://humanbehaviourchange.org/ontology/BCIO_006085`
- `http://humanbehaviourchange.org/ontology/BCIO_028000`
- `http://humanbehaviourchange.org/ontology/BCIO_034000`
- `http://humanbehaviourchange.org/ontology/BCIO_036000`
- `http://humanbehaviourchange.org/ontology/BCIO_036001`
- `http://humanbehaviourchange.org/ontology/BCIO_036107`
- `http://humanbehaviourchange.org/ontology/BCIO_037000`
- `http://humanbehaviourchange.org/ontology/BCIO_042000`
- `http://humanbehaviourchange.org/ontology/BCIO_043000`
- `http://humanbehaviourchange.org/ontology/BCIO_050435`
- `obo:BFO_0000001`
- `obo:BFO_0000002`
- `obo:BFO_0000003`
- `obo:BFO_0000004`
- `obo:BFO_0000015`
- `obo:BFO_0000016`
- `obo:BFO_0000017`
- `obo:BFO_0000019`
- `obo:BFO_0000020`
- `obo:BFO_0000031`
- `obo:BFO_0000034`
- `obo:BFO_0000040`
- … 55 more (see comparison.json)

**Predicates only in VoID** (55)

- `http://protege.stanford.edu/plugins/owl/protege#defaultLanguage`
- `obo:IAO_0000113`
- `obo:IAO_0000411`
- `obo:IAO_0000424`
- `obo:IAO_0000426`
- `obo:IAO_0000427`
- `obo:IAO_0000596`
- `obo:IAO_0000597`
- `obo:IAO_0000598`
- `obo:IAO_0000599`
- `obo:IAO_0000603`
- `obo:IAO_0000700`
- `obo:IAO_0006011`
- `obo:IAO_0006012`
- `obo:IAO_0100001`
- `obo:OMO_0001001`
- `obo:OMO_0002001`
- `obo:OMO_0003000`
- `obo:OMO_0003001`
- `obo:OMO_0003002`
- `obo:OMO_0003003`
- `obo:OMO_0003004`
- `obo:OMO_0003005`
- `obo:OMO_0003006`
- `obo:OMO_0003007`
- … 30 more (see comparison.json)

**(source class, predicate) only in VoID** (163)

- `obo:IAO_0000078` → `obo:IAO_0000111`
- `obo:IAO_0000078` → `obo:IAO_0000115`
- `obo:IAO_0000078` → `obo:IAO_0000117`
- `obo:IAO_0000078` → `obo:IAO_0000119`
- `obo:IAO_0000078` → `rdfs:isDefinedBy`
- `obo:IAO_0000078` → `rdfs:label`
- `obo:IAO_0000225` → `obo:IAO_0000111`
- `obo:IAO_0000225` → `obo:IAO_0000115`
- `obo:IAO_0000225` → `obo:IAO_0000116`
- `obo:IAO_0000225` → `obo:IAO_0000117`
- `obo:IAO_0000225` → `obo:IAO_0000233`
- `obo:IAO_0000225` → `obo:IAO_0000234`
- `obo:IAO_0000225` → `http://purl.org/dc/elements/1.1/contributor`
- `obo:IAO_0000225` → `rdfs:isDefinedBy`
- `obo:IAO_0000225` → `rdfs:label`
- `obo:IAO_0000409` → `obo:IAO_0000111`
- `obo:IAO_0000409` → `obo:IAO_0000115`
- `obo:IAO_0000409` → `obo:IAO_0000116`
- `obo:IAO_0000409` → `obo:IAO_0000117`
- `obo:IAO_0000409` → `obo:IAO_0000119`
- `obo:IAO_0000409` → `rdfs:isDefinedBy`
- `obo:IAO_0000409` → `rdfs:label`
- `obo:PHASES_0002005` → `obo:IAO_0000115`
- `obo:PHASES_0002005` → `dct:contributor`
- `obo:PHASES_0002005` → `dct:created`
- … 138 more (see comparison.json)

**Edges only in VoID** (35)

- `obo:PHASES_0002005` → `dct:contributor` → `owl:NamedIndividual`
- `obo:PHASES_0002005` → `http://www.geneontology.org/formats/oboInOwl#inSubset` → `owl:AnnotationProperty`
- `obo:PHASES_0002005` → `rdfs:subClassOf` → `owl:Class`
- `http://www.geneontology.org/formats/oboInOwl#Subset` → `obo:IAO_0000231` → `obo:IAO_0000225`
- `http://www.geneontology.org/formats/oboInOwl#Subset` → `obo:IAO_0000231` → `owl:NamedIndividual`
- `owl:AnnotationProperty` → `obo:IAO_0000114` → `obo:IAO_0000078`
- `owl:AnnotationProperty` → `obo:IAO_0000114` → `owl:NamedIndividual`
- `owl:AnnotationProperty` → `dct:contributor` → `owl:NamedIndividual`
- `owl:AnnotationProperty` → `rdfs:subPropertyOf` → `owl:AnnotationProperty`
- `owl:Axiom` → `owl:annotatedProperty` → `owl:AnnotationProperty`
- `owl:Axiom` → `owl:annotatedSource` → `obo:PHASES_0002005`
- `owl:Axiom` → `owl:annotatedSource` → `owl:Class`
- `owl:Axiom` → `owl:annotatedSource` → `owl:NamedIndividual`
- `owl:Axiom` → `owl:annotatedSource` → `owl:ObjectProperty`
- `owl:Class` → `obo:IAO_0000114` → `obo:IAO_0000078`
- `owl:Class` → `obo:IAO_0000114` → `owl:NamedIndividual`
- `owl:Class` → `dct:contributor` → `owl:NamedIndividual`
- `owl:Class` → `http://www.geneontology.org/formats/oboInOwl#inSubset` → `owl:AnnotationProperty`
- `owl:Class` → `rdfs:subClassOf` → `owl:Class`
- `owl:Class` → `rdfs:subClassOf` → `owl:Restriction`
- `owl:Class` → `owl:disjointWith` → `owl:Class`
- `owl:Class` → `owl:equivalentClass` → `owl:Class`
- `owl:NamedIndividual` → `obo:IAO_0000231` → `obo:IAO_0000225`
- `owl:NamedIndividual` → `obo:IAO_0000231` → `owl:NamedIndividual`
- `owl:NamedIndividual` → `dct:contributor` → `owl:NamedIndividual`
- … 10 more (see comparison.json)

**Descriptions that differ** (42)

- `obo:IAO_0000078`<br>curated: A data item that represents the curation status of an ontology term.<br>KG: The curation status of the term. The allowed values come from an enumerated list of predefined terms. See the specification of these instances for more detailed definitions of each enumerated value.
- `obo:IAO_0000225`<br>curated: A specification of the reason why an ontology term was made obsolete.<br>KG: The reason for which a term has been deprecated. The allowed values come from an enumerated list of predefined terms. See the specification of these instances for more detailed definitions of each enu
- `obo:IAO_0000409`<br>curated: A specification for a type of denotation used to reference an entity.<br>KG: A denotator type indicates how a term should be interpreted from an ontological perspective.
- `obo:PHASES_0002005`<br>curated: A theory information content entity that provides a systematic framework for explaining, predicting, or understanding psychological phenomena.<br>KG: A theory that summarizes and explains mental and behavioral patterns within the context of society and culture.
- `http://humanbehaviourchange.org/ontology/BCIOR_000010`<br>curated: A relation that links an individual human behaviour to a behavioural attribute.<br>KG: A relation that links an individual human behaviour to a behavioural attribute. Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asserted as a direct triple.
- `http://humanbehaviourchange.org/ontology/BCIOR_000011`<br>curated: Realises the human life function of an individual human behaviour.<br>KG: Realises the human life function of an individual human behaviour. Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asserted as a direct triple.
- `http://humanbehaviourchange.org/ontology/BCIOR_000013`<br>curated: Causal relation between two entities in which a behaviour brings into existence, causes to occur, destroys, prevents from occurring, or changes an entity.<br>KG: Causally relation between two entities in which a behaviour brings into existence, causes to occur, destroys, prevents from occurring, or changes an entity. Declared in the schema but used in no tripl
- `http://humanbehaviourchange.org/ontology/BCIOR_000014`<br>curated: Has participant that relates a behaviour to the person enacting the behaviour.<br>KG: Has participant that relates a behaviour to the person enacting the behaviour. Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asserted as a direct triple.
- `http://humanbehaviourchange.org/ontology/BCIOR_000015`<br>curated: Has participant that relates a behaviour to a material entity that the person enacting the behaviour intends to enable or facilitate the behaviour.<br>KG: Has participant that relates a behaviour to a material entity that the person enacting the behaviour intends to enable or facilitate the behaviour. Used only inside class axioms, as owl:onProperty of 
- `http://humanbehaviourchange.org/ontology/BCIOR_000016`<br>curated: Has participant that relates a behaviour to another sentient being that accompanies the person enacting the behaviour.<br>KG: Has participant that relates a behaviour to another sentient being that accompanies the person enacting the behaviour. Used only inside class axioms, as owl:onProperty of 1 owl:Restriction; never asse
- … 32 more (see comparison.json)

## prokn

Curated row types: {'Class': 41, 'Predicate': 248}

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (393)

- `obo:FBcv_0003016` → `dct:source`
- `obo:FBcv_0003016` → `dct:type`
- `obo:FBcv_0003016` → `http://purl.uniprot.org/core/organism`
- `obo:FBcv_0003016` → `http://purl.uniprot.org/core/taxon`
- `obo:FBcv_0003016` → `rdfs:label`
- `obo:FBcv_0003016` → `https://research.bioinformatics.udel.edu/ProKN/rdf/speciesGroupFlag`
- `obo:NCIT_C178092` → `http://ensembl.org/glossary/ENSGLOSSARY_00000950000095`
- `obo:NCIT_C178092` → `obo:NCIT_C157517`
- `obo:NCIT_C178092` → `obo:NCIT_C48662`
- `obo:NCIT_C178092` → `obo:NCIT_C82562`
- `obo:NCIT_C178092` → `obo:SO_0001762`
- `obo:NCIT_C178092` → `dct:date`
- `obo:NCIT_C178092` → `dct:identifier`
- `obo:NCIT_C178092` → `dct:source`
- `obo:NCIT_C178092` → `dct:type`
- `obo:NCIT_C178092` → `http://purl.org/ontology/bibo/pmid`
- `obo:NCIT_C178092` → `http://purl.uniprot.org/core/citation`
- `obo:NCIT_C178092` → `http://purl.uniprot.org/core/disease`
- `obo:NCIT_C178092` → `schema:MolecularEntity`
- `obo:NCIT_C178092` → `schema:identifier`
- `obo:NCIT_C178092` → `http://snomed.info/id/276239002`
- `obo:NCIT_C178092` → `http://www.ebi.ac.uk/efo/EFO_0000651`
- `obo:NCIT_C178092` → `rdfs:comment`
- `obo:NCIT_C178092` → `rdfs:label`
- `obo:NCIT_C178092` → `skos:exactMatch`
- … 368 more (see comparison.json)

**(source class, predicate) only curated** (6)

- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE`
- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_HEART`
- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_KIDNEY`
- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_LIVER`
- `rdf:Statement` → `biolink:has_evidence`
- `https://www.w3.org/2002/07/owl#NegativePropertyAssertion` → `biolink:has_evidence`

**Edges only in VoID** (177)

- `obo:NCIT_C178092` → `obo:bto#related_to` → `http://www.ebi.ac.uk/efo/EFO_0000651`
- `obo:NCIT_C178092` → `http://purl.org/ontology/bibo/pmid` → `http://purl.uniprot.org/core/citation`
- `obo:NCIT_C178092` → `skos:exactMatch` → `http://purl.uniprot.org/core/Disease`
- `obo:NCIT_C178092` → `skos:exactMatch` → `http://www.ebi.ac.uk/efo/EFO_0000651`
- `obo:NCIT_C43366` → `obo:ECO_9000000` → `https://w3id.org/reproduceme#Experiment`
- `obo:NCIT_C43366` → `obo:NCIT_C41184` → `http://www.ebi.ac.uk/efo/EFO_0000651`
- `obo:NCIT_C43366` → `obo:RO_0003308` → `http://purl.uniprot.org/core/Disease`
- `obo:NCIT_C43366` → `obo:RO_0003308` → `http://www.ebi.ac.uk/efo/EFO_0000651`
- `obo:NCIT_C43366` → `obo:has_dbxref` → `obo:NCIT_C43366`
- `obo:NCIT_C43366` → `obo:has_dbxref` → `obo:NCIT_C61154`
- `obo:NCIT_C43366` → `obo:has_dbxref` → `http://www.bioassayontology.org/bao#BAO_0003059`
- `obo:NCIT_C43366` → `rdfs:subClassOf` → `obo:NCIT_C43366`
- `obo:NCIT_C43366` → `rdfs:subClassOf` → `schema:Drug`
- `obo:NCIT_C43366` → `skos:exactMatch` → `obo:NCIT_C61154`
- `obo:NCIT_C43366` → `skos:exactMatch` → `http://www.bioassayontology.org/bao#BAO_0003059`
- `obo:NCIT_C43366` → `https://biolink.github.io/biolink-model/similar_to` → `obo:NCIT_C61154`
- `obo:NCIT_C43366` → `https://biolink.github.io/biolink-model/similar_to` → `http://www.bioassayontology.org/bao#BAO_0003059`
- `obo:NCIT_C48182` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE` → `http://purl.uniprot.org/core/Gene`
- `obo:NCIT_C61154` → `obo:ECO_9000000` → `https://w3id.org/reproduceme#Experiment`
- `obo:NCIT_C61154` → `obo:NCIT_C41184` → `http://purl.uniprot.org/core/Disease`
- `obo:NCIT_C61154` → `obo:NCIT_C41184` → `http://www.ebi.ac.uk/efo/EFO_0000651`
- `obo:NCIT_C61154` → `obo:RO_0003308` → `http://purl.uniprot.org/core/Disease`
- `obo:NCIT_C61154` → `obo:has_dbxref` → `obo:NCIT_C43366`
- `obo:NCIT_C61154` → `obo:has_dbxref` → `obo:NCIT_C61154`
- `obo:NCIT_C61154` → `obo:has_dbxref` → `http://www.bioassayontology.org/bao#BAO_0003059`
- … 152 more (see comparison.json)

**Edges only curated** (4)

- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE` → `obo:NCIT_C48182`
- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_HEART` → `obo:UBERON_0000948`
- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_KIDNEY` → `obo:UBERON_0002113`
- `http://purl.uniprot.org/core/Gene` → `https://research.bioinformatics.udel.edu/ProKN/rdf/HAS_MARKER_GENE_IN_LIVER` → `obo:UBERON_0002107`

**Edge properties (predicate, property) only in VoID** (195)

- `http://purl.allotrope.org/ontologies/result#AFX_0000408` → `dct:source`
- `obo:BCGO_0000177` → `dct:source`
- `obo:CLO_0037210` → `dct:source`
- `obo:ECO_9000000` → `dct:source`
- `obo:GENO_0000382` → `dct:source`
- `obo:GENO_0000382` → `http://www.geneontology.org/formats/oboInOwl#evidence`
- `obo:MI_2236` → `dct:source`
- `obo:MI_2236` → `http://purl.org/ontology/bibo/pmid`
- `obo:MI_2236` → `schema:identifier`
- `obo:MI_2241` → `dct:source`
- `obo:MI_2241` → `http://purl.org/ontology/bibo/pmid`
- `obo:MI_2241` → `schema:identifier`
- `obo:NCIT_C41184` → `dct:source`
- `obo:NCIT_C41184` → `schema:provider`
- `obo:NCIT_C41184` → `rdfs:label`
- `obo:NCIT_C94578` → `dct:source`
- `obo:NCIT_C94578` → `schema:identifier`
- `obo:NCIT_C94578` → `https://w3id.org/reproduceme#Treatment`
- `obo:PATO_0000627` → `dct:source`
- `obo:PATO_0000627` → `skos:exactMatch`
- `obo:PATO_0000627` → `https://w3id.org/reproduceme#Treatment`
- `obo:PATO_0000642` → `dct:source`
- `obo:RO_0002180` → `dct:source`
- `obo:RO_0002180` → `https://biolink.github.io/biolink-model/homologous_to`
- `obo:RO_0002410` → `dct:source`
- … 170 more (see comparison.json)

**Descriptions that differ** (9)

- `obo:SO_0001147`<br>curated: Describes the natural sequence variants due to polymorphisms, disease-associated mutations, RNA editing and variations between strains, isolates or cultivars.<br>KG: Discrete.
- `obo:GO_0005694`<br>curated: A structure composed of a very long molecule of DNA and associated proteins (e.g. histones) that carries hereditary information.<br>KG: Chromosomes include parts that are not part of the chromatin. Examples include the kinetochore.
- `obo:ECO_9000000`<br>curated: A relation connecting an evidence type to an assertion method where the assertion method describes the type of process employed to evaluate the evidence.<br>KG: In the future we may use a more generic relation with weaker domain and range constraints taken from IAO, RO or OBI.
- `obo:GO_0000776`<br>curated: A multisubunit complex that is located at the centromeric region of DNA and provides an attachment point for the spindle microtubules.<br>KG: Note that the kinetochore overlaps the centromeric DNA, but centromeric DNA is not part of the kinetochore.
- `obo:NCIT_C13258`<br>curated: Semiautonomous, self-reproducing organelles that occur in the cytoplasm of all cells of most, but not all, eukaryotes. Mitochondria are the principal energy source of the cell and contain the cytochro<br>KG: Semiautonomous, self-reproducing organelles that occur in the cytoplasm of all cells of most, but not all, eukaryotes. Mitochondria contain distinctive ribosomes, transfer RNAs, amino acyl t-RNA synth
- `obo:GO_0005730`<br>curated: A small, dense body one or more of which are present in the nucleus of eukaryotic cells. It is rich in RNA and protein, is not bounded by a limiting membrane, and is not seen during mitosis.<br>KG: A small, dense body one or more of which are present in the nucleus of eukaryotic cells. It is rich in RNA and protein, is not bounded by a limiting membrane, and is not seen during mitosis. Its prime
- `obo:GO_0005813`<br>curated: A structure comprised of a core structure (in most organisms, a pair of centrioles) and peripheral material from which a microtubule-based structure, such as a spindle apparatus, is organized.<br>KG: A structure comprised of a core structure (in most organisms, a pair of centrioles) and peripheral material from which a microtubule-based structure, such as a spindle apparatus, is organized. Centros
- `obo:GO_0032154`<br>curated: The cleavage furrow is a plasma membrane invagination at the cell division site. The cleavage furrow begins as a shallow groove and eventually deepens to divide the cytoplasm.<br>KG: While the term 'cleavage furrow' was initially associated with animal cells, such a structure occurs in many other types of cells, including unicellular protists.
- `obo:RO_0002180`<br>curated: w 'has component' p if w 'has part' p and w is such that it can be directly disassembled into n parts p, p2, p3, ..., pn, where these parts are of similar type.<br>KG: w 'has component' p if w 'has part' p and w is such that it can be directly disassembled into into n parts p, p2, p3, ..., pn, where these parts are of similar type.

## rdkg

Curated row types: {'Class': 11, 'Predicate': 21}

**Classes only in VoID** (2)

- `owl:ObjectProperty`
- `owl:Ontology`

**(source class, predicate) only in VoID** (52)

- `owl:ObjectProperty` → `rdfs:comment`
- `owl:ObjectProperty` → `rdfs:label`
- `owl:Ontology` → `rdfs:comment`
- `owl:Ontology` → `rdfs:label`
- `owl:Ontology` → `owl:versionInfo`
- `biolink:AnatomicalEntity` → `rdfs:label`
- `biolink:AnatomicalEntity` → `skos:prefLabel`
- `biolink:AnatomicalEntity` → `biolink:category`
- `biolink:AnatomicalEntity` → `biolink:id`
- `biolink:BiologicalProcess` → `rdfs:label`
- `biolink:BiologicalProcess` → `skos:prefLabel`
- `biolink:BiologicalProcess` → `biolink:category`
- `biolink:BiologicalProcess` → `biolink:id`
- `biolink:ChemicalEntity` → `rdfs:label`
- `biolink:ChemicalEntity` → `skos:prefLabel`
- `biolink:ChemicalEntity` → `biolink:category`
- `biolink:ChemicalEntity` → `biolink:id`
- `biolink:ChemicalExposure` → `rdfs:label`
- `biolink:ChemicalExposure` → `skos:prefLabel`
- `biolink:ChemicalExposure` → `biolink:category`
- `biolink:ChemicalExposure` → `biolink:id`
- `biolink:Disease` → `rdfs:label`
- `biolink:Disease` → `skos:prefLabel`
- `biolink:Disease` → `biolink:category`
- `biolink:Disease` → `biolink:contraindicated_for`
- … 27 more (see comparison.json)

**(source class, predicate) only curated** (2)

- `biolink:Gene` → `biolink:contributes_to`
- `biolink:Gene` → `biolink:gene_associated_with_condition`

**Edges only in VoID** (16)

- `biolink:Disease` → `biolink:contraindicated_for` → `biolink:Drug`
- `biolink:Disease` → `biolink:contributes_to` → `biolink:ChemicalExposure`
- `biolink:Disease` → `biolink:contributes_to` → `biolink:Gene`
- `biolink:Disease` → `biolink:gene_associated_with_condition` → `biolink:AnatomicalEntity`
- `biolink:Disease` → `biolink:gene_associated_with_condition` → `biolink:BiologicalProcess`
- `biolink:Disease` → `biolink:gene_associated_with_condition` → `biolink:ChemicalEntity`
- `biolink:Disease` → `biolink:gene_associated_with_condition` → `biolink:Gene`
- `biolink:Disease` → `biolink:has_phenotype` → `biolink:Disease`
- `biolink:Disease` → `biolink:related_to` → `biolink:AnatomicalEntity`
- `biolink:Disease` → `biolink:related_to` → `biolink:BiologicalProcess`
- `biolink:Disease` → `biolink:related_to` → `biolink:ChemicalEntity`
- `biolink:Disease` → `biolink:related_to` → `biolink:Disease`
- `biolink:Disease` → `biolink:related_to` → `biolink:ExposureEvent`
- `biolink:Disease` → `biolink:related_to` → `biolink:Gene`
- `biolink:Gene` → `biolink:related_to` → `biolink:Disease`
- `biolink:PhenotypicFeature` → `biolink:has_phenotype` → `biolink:Disease`

**Edges only curated** (2)

- `biolink:Gene` → `biolink:contributes_to` → `biolink:Disease`
- `biolink:Gene` → `biolink:gene_associated_with_condition` → `biolink:Disease`

**Descriptions that differ** (7)

- `biolink:causes_condition`<br>curated: Relates a variant to the disease it causes.<br>KG: Relates a variant to the disease it causes
- `biolink:gene_associated_with_condition`<br>curated: Relates a gene to a disease condition.<br>KG: Relates a gene to a disease condition
- `biolink:has_gene`<br>curated: Relates a variant to its gene.<br>KG: Relates a variant to its gene
- `biolink:has_phenotype`<br>curated: Relates a disease to its associated phenotypes.<br>KG: Relates a disease to its associated phenotypes
- `biolink:related_to`<br>curated: A general association between entities.<br>KG: General association between entities
- `biolink:subclass_of`<br>curated: Indicates a hierarchical relationship between diseases.<br>KG: Indicates hierarchical relationship between diseases
- `biolink:treats`<br>curated: Relates a drug to the disease it treats.<br>KG: Relates a drug to the disease it treats

## ruralkg

Curated row types: {'Class': 244, 'Predicate': 149}

**Classes only in VoID** (3)

- `rdf:Property`
- `owl:AnnotationProperty`
- `owl:ObjectProperty`

**Classes only curated** (227)

- `http://sail.ua.edu/ruralkg/healthcare/AccessToCare`
- `http://sail.ua.edu/ruralkg/healthcare/ExpendituresAndPayments`
- `http://sail.ua.edu/ruralkg/healthcare/HealthInsurance`
- `http://sail.ua.edu/ruralkg/healthcare/Healthcare`
- `http://sail.ua.edu/ruralkg/healthcare/HealthcareUtilization`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_AccesstoCare_BarriersDelays`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_AccesstoCare_SatisfactionQuality`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_AccesstoCare_UnmetNeed`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_AccesstoCare_UsualSourceofCare`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_ExpendituresandPayments_ByPayer`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_ExpendituresandPayments_ByServiceType`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_ExpendituresandPayments_ChargesPayments`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_ExpendituresandPayments_OutofPocket`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_ExpendituresandPayments_TotalExpenditures`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_AmbulatoryOfficeVisits`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_Dental`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_EmergencyDepartment`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_HomeHealth`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_HospitalInpatient`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_MedicationInquiry`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_OtherServices`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_PrescriptionMedications`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_Therapies`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_UsualSourceofCare`
- `http://sail.ua.edu/ruralkg/healthcare/Section_MEPS_HealthcareUtilization_Vision`
- … 202 more (see comparison.json)

**Predicates only in VoID** (2)

- `rdfs:domain`
- `rdfs:range`

**Predicates only curated** (4)

- `http://release.niem.gov/niem/domains/jxdm/7.2/#ArrestCategoryCode`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#ArrestSubjectJuvenileDispositionCode`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#JudicialDistrictCode`
- `http://release.niem.gov/niem/niem-core/5.0/#MeasureValueText`

**(source class, predicate) only in VoID** (8)

- `owl:AnnotationProperty` → `rdfs:comment`
- `owl:AnnotationProperty` → `rdfs:isDefinedBy`
- `owl:AnnotationProperty` → `rdfs:label`
- `owl:ObjectProperty` → `rdfs:comment`
- `owl:ObjectProperty` → `rdfs:domain`
- `owl:ObjectProperty` → `rdfs:isDefinedBy`
- `owl:ObjectProperty` → `rdfs:label`
- `owl:ObjectProperty` → `rdfs:range`

**Edges only in VoID** (3)

- `owl:AnnotationProperty` → `rdfs:isDefinedBy` → `owl:Ontology`
- `owl:ObjectProperty` → `rdfs:domain` → `rdfs:Class`
- `owl:ObjectProperty` → `rdfs:isDefinedBy` → `owl:Ontology`

**Descriptions that differ** (16)

- `http://sail.ua.edu/ruralkg/settlementtype/CountyStatus`<br>curated: Represents the status classification of a county<br>KG: Status of a county in terms of rural or urban classification.
- `http://sail.ua.edu/ruralkg/settlementtype/RUCC`<br>curated: Rural-Urban Continuum Code classification<br>KG: Rural-Urban Continuum Code classification.
- `http://sail.ua.edu/ruralkg/substanceabuse/Substance`<br>curated: Represents a substance involved in substance abuse<br>KG: Types of substances that can be abused.
- `http://sail.ua.edu/ruralkg/substanceabuse/SubstanceRelatedIncident`<br>curated: Represents an incident related to substance abuse<br>KG: Types of incidents related to substance abuse.
- `http://sail.ua.edu/ruralkg/treatment/MentalHealthService`<br>curated: Represents a mental health service offering<br>KG: Specific mental health services offered.
- `http://sail.ua.edu/ruralkg/treatment/MentalHealthServiceCategory`<br>curated: Represents a category of mental health services<br>KG: Categories of mental health services.
- `http://sail.ua.edu/ruralkg/treatment/TreatmentProvider`<br>curated: Represents an organization or individual providing treatment services<br>KG: Entities that provide treatment services.
- `http://sail.ua.edu/ruralkg/variable/BRFSS`<br>curated: Behavioral Risk Factor Surveillance System variable<br>KG: Variables from the Behavioral Risk Factor Surveillance System dataset (year 2022). Topic placement lives on the section-class side under publichealth:/substanceabuse:/settlement:; this class is just t
- `http://sail.ua.edu/ruralkg/variable/BRFSSAnswer`<br>curated: Answer value for a BRFSS variable<br>KG: Answer options for BRFSS variables.
- `http://sail.ua.edu/ruralkg/variable/MEPS`<br>curated: Medical Expenditure Panel Survey variable<br>KG: Variables from the Medical Expenditure Panel Survey dataset.
- … 6 more (see comparison.json)

## sawgraph

Curated row types: {'Class': 194, 'Predicate': 164}

**Classes only in VoID** (239)

- `obo:BFO_0000040`
- `obo:COB_0000022`
- `obo:FOODON_00001002`
- `obo:FOODON_00001006`
- `obo:FOODON_00001015`
- `obo:FOODON_00001041`
- `obo:FOODON_00001092`
- `obo:FOODON_00001093`
- `obo:FOODON_00001134`
- `obo:FOODON_00001147`
- `obo:FOODON_00001173`
- `obo:FOODON_00001242`
- `obo:FOODON_00001248`
- `obo:FOODON_00001256`
- `obo:FOODON_00001257`
- `obo:FOODON_00001261`
- `obo:FOODON_00001623`
- `obo:FOODON_00001669`
- `obo:FOODON_00001678`
- `obo:FOODON_00002127`
- `obo:FOODON_00002147`
- `obo:FOODON_00002150`
- `obo:FOODON_00002220`
- `obo:FOODON_00002319`
- `obo:FOODON_00002403`
- … 214 more (see comparison.json)

**Classes only curated** (17)

- `http://w3id.org/coso/v1/contaminoso#ContaminantAbsoluteMeasurement`
- `http://w3id.org/coso/v1/contaminoso#ContaminantMassQuantityKind`
- `http://w3id.org/coso/v1/contaminoso#ContaminantReleaseObservation`
- `http://w3id.org/coso/v1/contaminoso#MonitoredFeature`
- `http://w3id.org/coso/v1/contaminoso#ReleaseFeature`
- `http://w3id.org/coso/v1/contaminoso#ReleasePoint`
- `http://w3id.org/sawgraph/v1/us-wqp#CensoringLevel`
- `http://w3id.org/sawgraph/v1/us-wqp#DefWQPBiologicalSample`
- `http://w3id.org/sawgraph/v1/us-wqp#DefWQPWasteWaterSample`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.AquaticVegetation`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.BacteriaVirus`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.BenthicMacroinvertebrates`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.Corals`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.Diatoms`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.Invertebrates`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.PhytoplanktonZooplankton`
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.TerrestrialVegetation`

**Predicates only in VoID** (121)

- `obo:BFO_0000050`
- `obo:BFO_0000051`
- `obo:IAO_0000111`
- `obo:IAO_0000112`
- `obo:IAO_0000115`
- `obo:IAO_0000116`
- `obo:IAO_0000118`
- `obo:IAO_0000119`
- `obo:IAO_0000412`
- `obo:IAO_0000600`
- `obo:RO_0000053`
- `obo:RO_0000086`
- `obo:RO_0001000`
- `obo:RO_0002160`
- `obo:RO_0002162`
- `obo:RO_0002202`
- `obo:RO_0002350`
- `obo:RO_0003001`
- `obo:RO_0009004`
- `http://purl.org/dc/elements/1.1/contributor`
- `dct:updated`
- `http://purl.org/spatialai/stad/v2/core/hasTransformationKind`
- `http://purl.org/vocab/vann/preferredNamespacePrefix`
- `http://purl.org/vocab/vann/preferredNamespaceUri`
- `http://qudt.org/schema/qudt/abbreviation`
- … 96 more (see comparison.json)

**Predicates only curated** (1)

- `http://w3id.org/sawgraph/v1/us-wqp#Sample`

**(source class, predicate) only in VoID** (3993)

- `obo:BFO_0000040` → `http://w3id.org/sawgraph/v1/us-wqp#rank`
- `obo:BFO_0000040` → `rdfs:comment`
- `obo:BFO_0000040` → `rdfs:isDefinedBy`
- `obo:BFO_0000040` → `rdfs:label`
- `obo:BFO_0000040` → `rdfs:seeAlso`
- `obo:BFO_0000040` → `owl:sameAs`
- `obo:COB_0000022` → `http://w3id.org/sawgraph/v1/us-wqp#rank`
- `obo:COB_0000022` → `rdfs:isDefinedBy`
- `obo:COB_0000022` → `rdfs:label`
- `obo:COB_0000022` → `rdfs:seeAlso`
- `obo:COB_0000022` → `owl:sameAs`
- `obo:FOODON_00001002` → `http://w3id.org/sawgraph/v1/us-wqp#rank`
- `obo:FOODON_00001002` → `rdfs:isDefinedBy`
- `obo:FOODON_00001002` → `rdfs:label`
- `obo:FOODON_00001002` → `rdfs:seeAlso`
- `obo:FOODON_00001002` → `owl:sameAs`
- `obo:FOODON_00001006` → `rdfs:isDefinedBy`
- `obo:FOODON_00001006` → `rdfs:label`
- `obo:FOODON_00001006` → `rdfs:seeAlso`
- `obo:FOODON_00001006` → `owl:sameAs`
- `obo:FOODON_00001015` → `rdfs:isDefinedBy`
- `obo:FOODON_00001015` → `rdfs:label`
- `obo:FOODON_00001015` → `rdfs:seeAlso`
- `obo:FOODON_00001015` → `owl:sameAs`
- `obo:FOODON_00001041` → `rdfs:isDefinedBy`
- … 3968 more (see comparison.json)

**Edges only in VoID** (21095)

- `obo:BFO_0000040` → `rdfs:isDefinedBy` → `rdfs:Resource`
- `obo:BFO_0000040` → `rdfs:isDefinedBy` → `owl:Ontology`
- `obo:BFO_0000040` → `rdfs:isDefinedBy` → `owl:Thing`
- `obo:BFO_0000040` → `rdfs:seeAlso` → `rdfs:Resource`
- `obo:BFO_0000040` → `rdfs:seeAlso` → `owl:Ontology`
- `obo:BFO_0000040` → `rdfs:seeAlso` → `owl:Thing`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:BFO_0000040`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:COB_0000022`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001002`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001006`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001015`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001041`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001092`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001093`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001134`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001147`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001173`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001242`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001248`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001256`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001257`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001261`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001623`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001669`
- `obo:BFO_0000040` → `owl:sameAs` → `obo:FOODON_00001678`
- … 21070 more (see comparison.json)

**Descriptions that differ** (42)

- `http://qudt.org/schema/qudt/QuantityKind`<br>curated: A Quantity Kind is any observable property that can be measured and quantified numerically.<br>KG: A <b>Quantity Kind</b> is any observable property that can be measured and quantified numerically. Familiar examples include physical properties such as length, mass, time, force, energy, power, elect
- `http://qudt.org/schema/qudt/QuantityValue`<br>curated: A Quantity Value expresses the magnitude and kind of a quantity and is given by the product of a numerical value and a unit of measure.<br>KG: A <i>Quantity Value</i> expresses the magnitude and kind of a quantity and is given by the product of a numerical value <code>n</code> and a unit of measure <code>U</code>. The number multiplying the 
- `http://qudt.org/schema/qudt/Unit`<br>curated: A unit of measure, or unit, is a particular quantity value that has been chosen as a scale for measuring other quantities of the same kind.<br>KG: A unit of measure, or unit, is a particular quantity value that has been chosen as a scale for measuring other quantities the same kind (more generally of equivalent dimension). For example, the meter
- `http://w3id.org/coso/v1/contaminoso#DetectQuantityValue`<br>curated: A Quantity Value that represents a detection of the contaminant.<br>KG: A Quantity Value that represents a quantified detection of the contaminant.
- `http://w3id.org/sawgraph/v1/us-wqp#ContractQuantitationLimit`<br>curated: Minimum level of reliable quantitation acceptable under the contract Statement of Work (SOW). A subclass of coso:QuantitationLimit.<br>KG: - Minimum level of reliable quantitation acceptable under the contract Statement of Work (SOW).
- `http://w3id.org/sawgraph/v1/us-wqp#EstimatedDetectionLevel`<br>curated: Estimated Detection Level -- Minimum concentration required to produce a specified signal-to-noise (S/N) ratio. A subclass of coso:DetectionLimit.<br>KG: Estimated Detection Level -- Minimum concentration required to produce a specified signal-to-noise (S/N) ratio.
- `http://w3id.org/sawgraph/v1/us-wqp#MinimumReportingLevel`<br>curated: Minimum Reporting Level is the smallest measured concentration of a constituent that can be reliably measured using a given analytical method. A subclass of coso:QuantitationLimit.<br>KG: Minimum Reporting Level is the smallest measured concentration of a constituent that can be reliably measured using a given analytical method
- `http://w3id.org/sawgraph/v1/us-wqp#PracticalQuantitationLimit`<br>curated: Practical Quantitation Limit (PQL). A subclass of coso:QuantitationLimit.<br>KG: Practical Quantitation Limit (PQL)
- `http://w3id.org/sawgraph/v1/us-wqp#SampleDetectionLimit`<br>curated: Sample Detection Limit (SDL) - The MDL adjusted to reflect sample-specific actions such as dilution or use of smaller aliquot sizes, or to report results on a dry-weight basis. A subclass of coso:Dete<br>KG: Sample Detection Limit (SDL) - The MDL adjusted to reflect sample-specific actions such as dilution or use of smaller aliquot sizes, or to report results on a dry-weight basis.
- `http://w3id.org/sawgraph/v1/us-wqp#TaxonGroup.FishNekton`<br>curated: Water Quality Portal taxon-group enumeration value for fish nekton; a subclass of wqp:Taxon used as the sample material type of a biological sample.<br>KG: North American Native Fishes Association Fish List - http://www.nanfa.org/checklist.shtml
- … 32 more (see comparison.json)

## scales

Curated row types: {'Class': 34, 'Predicate': 591}

**Classes only in VoID** (2)

- `rdf:Property`
- `rdfs:Class`

**Classes only curated** (5)

- `http://release.niem.gov/niem/auxiliary/statistics/5.0/#Population`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingFacility`
- `http://release.niem.gov/niem/niem-core/5.0/#Jurisdiction`
- `http://sail.ua.edu/ruralkg/treatmentprovider/TreatmentProvider`
- `http://schemas.scales-okn.org/rdf/scales#DisambiguatedEntity`

**Predicates only in VoID** (4)

- `rdfs:comment`
- `rdfs:domain`
- `rdfs:range`
- `rdfs:subClassOf`

**Predicates only curated** (9)

- `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingSubject`
- `http://schemas.scales-okn.org/rdf/scales#IdbFilejudg`
- `http://schemas.scales-okn.org/rdf/scales#IdbFilemag`
- `http://schemas.scales-okn.org/rdf/scales#IdbFjudge`
- `http://schemas.scales-okn.org/rdf/scales#IdbName`
- `http://schemas.scales-okn.org/rdf/scales#IdbSource`
- `http://schemas.scales-okn.org/rdf/scales#IdbTermjudg`
- `http://schemas.scales-okn.org/rdf/scales#IdbTermmag`
- `http://schemas.scales-okn.org/rdf/scales#IdbTjudge`

**(source class, predicate) only in VoID** (8)

- `rdf:Property` → `rdfs:comment`
- `rdf:Property` → `rdfs:domain`
- `rdf:Property` → `rdfs:range`
- `rdf:Property` → `rdfs:subClassOf`
- `rdfs:Class` → `rdfs:comment`
- `rdfs:Class` → `rdfs:domain`
- `rdfs:Class` → `rdfs:range`
- `rdfs:Class` → `rdfs:subClassOf`

**(source class, predicate) only curated** (9)

- `http://release.niem.gov/niem/domains/jxdm/7.2/#Booking` → `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingSubject`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbFilejudg`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbFilemag`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbFjudge`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbName`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbSource`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbTermjudg`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbTermmag`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#IdbTjudge`

**Edges only in VoID** (41)

- `http://release.niem.gov/niem/domains/jxdm/7.2/#Arrest` → `http://release.niem.gov/niem/niem-core/5.0/#Location` → `http://release.niem.gov/niem/niem-core/5.0/#RelativeLocationReferencePoint`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#Charge` → `http://release.niem.gov/niem/domains/jxdm/7.2/#ChargeSubject` → `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingSubject`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#Charge` → `http://release.niem.gov/niem/domains/jxdm/7.2/#ChargeSubject` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#Charge` → `http://release.niem.gov/niem/domains/jxdm/7.2/#ChargeSubject` → `http://release.niem.gov/niem/domains/jxdm/7.2/#ChargeSubject`
- `http://release.niem.gov/niem/domains/jxdm/7.2/#Charge` → `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#CriminalCase`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty` → `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingSubject`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty` → `http://release.niem.gov/niem/domains/jxdm/7.2/#ChargeSubject`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty` → `http://release.niem.gov/niem/niem-core/5.0/#Person`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseInitiatingParty` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseInitiatingParty`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#MemberCase` → `http://schemas.scales-okn.org/rdf/scales#CivilCase`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#Party` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#Party` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseInitiatingParty`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#Party` → `http://release.niem.gov/niem/niem-core/5.0/#Person`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#RelatedCase` → `http://schemas.scales-okn.org/rdf/scales#CivilCase`
- `http://release.niem.gov/niem/niem-core/5.0/#CourtCase` → `http://schemas.scales-okn.org/rdf/scales#RelatedCase` → `http://schemas.scales-okn.org/rdf/scales#CriminalCase`
- `http://release.niem.gov/niem/niem-core/5.0/#RelativeLocation` → `http://release.niem.gov/niem/niem-core/5.0/#Location` → `http://release.niem.gov/niem/niem-core/5.0/#RelativeLocationReferencePoint`
- `http://release.niem.gov/niem/niem-core/5.0/#RelativeLocation` → `http://release.niem.gov/niem/niem-core/5.0/#RelativeLocationReferencePoint` → `http://release.niem.gov/niem/niem-core/5.0/#RelativeLocationReferencePoint`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseInitiatingParty` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseInitiatingParty`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://schemas.scales-okn.org/rdf/scales#MemberCase` → `http://schemas.scales-okn.org/rdf/scales#CivilCase`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://schemas.scales-okn.org/rdf/scales#Party` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseDefendantParty`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://schemas.scales-okn.org/rdf/scales#Party` → `http://release.niem.gov/niem/domains/jxdm/7.2/#CaseInitiatingParty`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://schemas.scales-okn.org/rdf/scales#RelatedCase` → `http://schemas.scales-okn.org/rdf/scales#CivilCase`
- `http://schemas.scales-okn.org/rdf/scales#CivilCase` → `http://schemas.scales-okn.org/rdf/scales#RelatedCase` → `http://schemas.scales-okn.org/rdf/scales#CriminalCase`
- … 16 more (see comparison.json)

**Edges only curated** (1)

- `http://release.niem.gov/niem/domains/jxdm/7.2/#Booking` → `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingSubject` → `http://release.niem.gov/niem/niem-core/5.0/#Person`

**Descriptions that differ** (29)

- `http://release.niem.gov/niem/auxiliary/statistics/5.0/#Population`<br>curated: A total membership of a defined class of people, objects or events. Declared in the schema, but no node carries this rdf:type in the current release.<br>KG: A total membership of a defined class of people, objects or events.
- `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingFacility`<br>curated: A police station or a detention facility where a booking occurs. Declared in the schema, but no node carries this rdf:type in the current release.<br>KG: A police station or a detention facility where a booking occurs.
- `http://release.niem.gov/niem/niem-core/5.0/#Jurisdiction`<br>curated: A geopolitical area in which an organization, person, or object has a specific range of authority. Declared in the schema, but no node carries this rdf:type in the current release.<br>KG: A geopolitical area in which an organization, person, or object has a specific range of authority.
- `http://sail.ua.edu/ruralkg/treatmentprovider/TreatmentProvider`<br>curated: An entity, such as a clinic or hospital, that offers treatment. Declared in the schema, but no node carries this rdf:type in the current release.<br>KG: An entity, such as a clinic or hospital, that offers treatment.
- `http://schemas.scales-okn.org/rdf/scales#DisambiguatedEntity`<br>curated: A disambiguated entity that a given undisambiguated record represents. Declared in the schema, but no node carries this rdf:type in the current release.<br>KG: A disambiguated entity that a given undisambiguated record represents.
- `http://release.niem.gov/niem/auxiliary/statistics/5.0/#Population`<br>curated: A total membership of a defined class of people, objects or events. Subjects are Jurisdiction nodes, which carry no rdf:type in the current release.<br>KG: A total membership of a defined class of people, objects or events.
- `http://release.niem.gov/niem/codes/occs/5.0/#FacilityFunctionCode`<br>curated: A purpose or use of a facility. Subjects are BookingFacility nodes, which carry no rdf:type in the current release.<br>KG: A purpose or use of a facility.
- `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingFacility`<br>curated: A police station or a detention facility where a booking occurs. Objects are BookingFacility nodes, which carry no rdf:type in the current release.<br>KG: A police station or a detention facility where a booking occurs.
- `http://release.niem.gov/niem/domains/jxdm/7.2/#BookingSubject`<br>curated: A person who is booked. Declared in the schema but not populated in the current release.<br>KG: A person who is booked.
- `http://release.niem.gov/niem/niem-core/5.0/#FacilityName`<br>curated: A name of a facility. Subjects are BookingFacility nodes, which carry no rdf:type in the current release.<br>KG: A name of a facility.
- … 19 more (see comparison.json)

## securechainkg

Curated row types: {'Class': 22, 'NodeProperty': 39, 'Predicate': 48}

**Classes only in VoID** (876)

- `http://asu.edu/semantics/SUDOKN/ABSProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AS9000`
- `http://asu.edu/semantics/SUDOKN/AS9003`
- `http://asu.edu/semantics/SUDOKN/AS9100`
- `http://asu.edu/semantics/SUDOKN/AS9102`
- `http://asu.edu/semantics/SUDOKN/AS9120`
- `http://asu.edu/semantics/SUDOKN/ASME`
- `http://asu.edu/semantics/SUDOKN/AWSWelder`
- `http://asu.edu/semantics/SUDOKN/AbrasiveCleaningCapability`
- `http://asu.edu/semantics/SUDOKN/AbrasiveMachiningCapability`
- `http://asu.edu/semantics/SUDOKN/AcetalProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AcetronProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AcrylicProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AdditiveManufacturingCapability`
- `http://asu.edu/semantics/SUDOKN/AdhesiveBondingCapability`
- `http://asu.edu/semantics/SUDOKN/AerospaceIndustry`
- `http://asu.edu/semantics/SUDOKN/AerospaceQuality`
- `http://asu.edu/semantics/SUDOKN/AgeQuenchHardeningCapability`
- `http://asu.edu/semantics/SUDOKN/AgricultureIndustry`
- `http://asu.edu/semantics/SUDOKN/AlkalineOxideConversionCoatingCapability`
- `http://asu.edu/semantics/SUDOKN/AlloyProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AlloySteelProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AluminumProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AnnealingCapability`
- `http://asu.edu/semantics/SUDOKN/AnodizingCapability`
- … 851 more (see comparison.json)

**Predicates only in VoID** (7)

- `http://asu.edu/semantics/SUDOKN/hasNAICSCodeValue`
- `rdf:first`
- `rdf:rest`
- `rdfs:domain`
- `rdfs:range`
- `rdfs:subClassOf`
- `owl:unionOf`

**(source class, predicate) only in VoID** (1178)

- `http://asu.edu/semantics/SUDOKN/ABSProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AS9000` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AS9003` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AS9100` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AS9102` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AS9120` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/ASME` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AWSWelder` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AbrasiveCleaningCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AbrasiveMachiningCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AcetalProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AcetronProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AcrylicProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AdditiveManufacturingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AdhesiveBondingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AerospaceIndustry` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AerospaceQuality` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AgeQuenchHardeningCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AgricultureIndustry` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AlkalineOxideConversionCoatingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AlloyProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AlloySteelProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AluminumProcessingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AnnealingCapability` → `rdfs:label`
- `http://asu.edu/semantics/SUDOKN/AnodizingCapability` → `rdfs:label`
- … 1153 more (see comparison.json)

**Edges only in VoID** (877)

- `rdf:Property` → `rdfs:domain` → `rdfs:Class`
- `rdf:Property` → `rdfs:domain` → `owl:Class`
- `rdf:Property` → `rdfs:range` → `rdfs:Class`
- `rdfs:Class` → `rdfs:subClassOf` → `rdfs:Class`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9000`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9003`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9100`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9102`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9120`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/ASME`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AWSWelder`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AerospaceQuality`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/BABA`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/BritishRetailConsortium`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/FDA`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/FDA21CFRPart820`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/FDAGMP`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/FDAPMA`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/HACCP`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/IATF`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/IATF16949`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/ISO13485`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/ISO14000`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/ISO14001`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/ISO16949`
- … 852 more (see comparison.json)

## sockg

Curated row types: {'Class': 105, 'Predicate': 106}

**Classes only curated** (15)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/Region`
- `http://www.opengis.net/ont/geosparql#Feature`
- `http://www.opengis.net/ont/geosparql#SpatialObject`
- `rdfs:Class`
- `https://idir.uta.edu/sockg-ontology#BiomassAnalysis`
- `https://idir.uta.edu/sockg-ontology#CropRelatedMeasurement`
- `https://idir.uta.edu/sockg-ontology#ErosionMeasurement`
- `https://idir.uta.edu/sockg-ontology#GrowthStageRelatedMeasurement`
- `https://idir.uta.edu/sockg-ontology#MeasurableEntity`
- `https://idir.uta.edu/sockg-ontology#PlantFractionRelatedMeasurement`
- `https://idir.uta.edu/sockg-ontology#PossiblySimulatedMeasurement`
- `https://idir.uta.edu/sockg-ontology#QualityMeasurement`
- `https://idir.uta.edu/sockg-ontology#Sample`
- `https://idir.uta.edu/sockg-ontology#SoilSample`

**Predicates only in VoID** (3)

- `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/spatialRelation`
- `https://idir.uta.edu/sockg-ontology#hasStandardDeviation`

**(source class, predicate) only in VoID** (341)

- `dct:BibliographicResource` → `dct:bibliographicCitation`
- `dct:BibliographicResource` → `dct:creator`
- `dct:BibliographicResource` → `dct:identifier`
- `dct:BibliographicResource` → `dct:issued`
- `http://purl.org/ontology/bibo/Book` → `dct:title`
- `http://qudt.org/schema/qudt/QuantityValue` → `http://qudt.org/schema/qudt/hasUnit`
- `http://qudt.org/schema/qudt/QuantityValue` → `http://qudt.org/schema/qudt/numericValue`
- `http://qudt.org/schema/qudt/QuantityValue` → `http://qudt.org/schema/qudt/standardUncertainty`
- `http://qudt.org/schema/qudt/QuantityValue` → `https://idir.uta.edu/sockg-ontology#hasStandardDeviation`
- `http://qudt.org/schema/qudt/QuantityValue` → `https://idir.uta.edu/sockg-ontology#isInterpolated`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `rdfs:label`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `rdfs:label`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://www.opengis.net/ont/geosparql#Geometry` → `http://www.opengis.net/ont/geosparql#asWKT`
- `http://www.opengis.net/ont/geosparql#SpatialObject` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo`
- `owl:Class` → `rdfs:comment`
- `owl:Class` → `rdfs:subClassOf`
- `owl:Class` → `owl:disjointWith`
- `owl:DatatypeProperty` → `rdfs:domain`
- `owl:DatatypeProperty` → `rdfs:range`
- … 316 more (see comparison.json)

**(source class, predicate) only curated** (1)

- `http://www.opengis.net/ont/geosparql#Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry`

**Edges only in VoID** (214)

- `http://qudt.org/schema/qudt/QuantityValue` → `http://qudt.org/schema/qudt/hasUnit` → `http://qudt.org/schema/qudt/Unit`
- `http://qudt.org/schema/qudt/QuantityValue` → `https://idir.uta.edu/sockg-ontology#hasStandardDeviation` → `http://qudt.org/schema/qudt/QuantityValue`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `owl:Class`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `https://idir.uta.edu/sockg-ontology#Location`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `https://idir.uta.edu/sockg-ontology#Site`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `https://idir.uta.edu/sockg-ontology#Location`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `https://idir.uta.edu/sockg-ontology#Site`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `https://idir.uta.edu/sockg-ontology#Location`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0`
- `http://www.opengis.net/ont/geosparql#Geometry` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `http://www.opengis.net/ont/geosparql#SpatialObject` → `http://purl.org/spatialai/spatial/spatial-full#spatiallyRelatedTo` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `owl:Class` → `rdfs:subClassOf` → `owl:Class`
- `owl:Class` → `owl:disjointWith` → `owl:Class`
- `owl:DatatypeProperty` → `rdfs:domain` → `owl:Class`
- `owl:DatatypeProperty` → `rdfs:range` → `rdfs:Datatype`
- `owl:DatatypeProperty` → `rdfs:range` → `owl:Class`
- `owl:ObjectProperty` → `rdfs:domain` → `owl:Class`
- `owl:ObjectProperty` → `rdfs:range` → `owl:Class`
- `owl:ObjectProperty` → `rdfs:subPropertyOf` → `owl:ObjectProperty`
- `owl:ObjectProperty` → `owl:equivalentProperty` → `owl:ObjectProperty`
- … 189 more (see comparison.json)

**Edges only curated** (1)

- `http://www.opengis.net/ont/geosparql#Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`

**Curated class labels that resolve to no URI** (1)

- `Quantity Value`

## spatialkg

Curated row types: {'Class': 15, 'Predicate': 55}

**Classes only in VoID** (16)

- `rdf:List`
- `rdf:ObjectProperty`
- `rdf:Property`
- `rdfs:Class`
- `rdfs:ContainerMembershipProperty`
- `rdfs:Datatype`
- `rdfs:Resource`
- `owl:AnnotationProperty`
- `owl:Class`
- `owl:DatatypeProperty`
- `owl:ObjectProperty`
- `owl:Ontology`
- `owl:OntologyProperty`
- `owl:ReflexiveProperty`
- `owl:SymmetricProperty`
- `owl:Thing`

**Classes only curated** (6)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_0`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level10`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level11`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level12`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level8`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level9`

**Predicates only in VoID** (30)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/cellID`
- `rdf:langRange`
- `rdfs:comment`
- `rdfs:domain`
- `rdfs:isDefinedBy`
- `rdfs:range`
- `rdfs:seeAlso`
- `rdfs:subClassOf`
- `rdfs:subPropertyOf`
- `xsd:length`
- `xsd:maxExclusive`
- `xsd:maxInclusive`
- `xsd:maxLength`
- `xsd:minExclusive`
- `xsd:minInclusive`
- `xsd:minLength`
- `xsd:pattern`
- `owl:backwardCompatibleWith`
- `owl:bottomDataProperty`
- `owl:bottomObjectProperty`
- `owl:deprecated`
- `owl:disjointWith`
- `owl:equivalentClass`
- `owl:equivalentProperty`
- `owl:incompatibleWith`
- … 5 more (see comparison.json)

**(source class, predicate) only in VoID** (197)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/hasFIPS`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfOverlaps`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `rdfs:label`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `owl:sameAs`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3` → `owl:sameAs`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/cellID`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfOverlaps`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfTouches`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfWithin`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://www.opengis.net/ont/geosparql#defaultGeometry`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- … 172 more (see comparison.json)

**Edges only in VoID** (670)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://purl.org/spatialai/spatial/spatial-full#connectedTo` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/administrativePartOf` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell_Level13`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `http://www.opengis.net/ont/geosparql#SpatialObject`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfContains` → `owl:Thing`
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfOverlaps` → `http://stko-kwg.geog.ucsb.edu/lod/ontology/S2Cell`
- … 645 more (see comparison.json)

**Descriptions that differ** (9)

- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion`<br>curated: Administrative regions as defined by the Global Administrative Area Database (GADM). The country node (administrativeRegion.USA) has this type only, with no level class.<br>KG: Administrative regoins as defined by the Global Administrative Area Database (GADM); see https://gadm.org/metadata.html
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_1`<br>curated: GADM level 1 administrative regions which are the highest level of division of a country, such as US states, Canadian provinces, or French departments. Each of the 51 states appears twice, as a KnowWh<br>KG: GADM level 1 administrative regions which are the highest level of division of a country, such as US states, Canadian provinces, or French departments.
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_2`<br>curated: GADM level 2 administrative regions which further subdivide states, provinces, or departments. Examples include counties in the US. Each of the 3,114 counties appears twice, as a KnowWhereGraph IRI an<br>KG: GADM level 2 administrative regions which further subdivide states, provinces, or departments. Examples include counties in the US
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/AdministrativeRegion_3`<br>curated: GADM level 3 administrative regions. In the US, these are subdivisions of counties, formally known as county subdivisions, such as minor civil divisions (e.g. towns or townships) or census county divi<br>KG: GADM level 3 administrative regions. In the US, these are subdivisions of counties, formally known as county subdivisions, such as minor civil divisions (e.g. towns ot townships) or census county divi
- `http://www.opengis.net/ont/geosparql#Feature`<br>curated: A discrete spatial phenomenon in a universe of discourse.<br>KG: Source: GeoSPARQL
- `http://www.opengis.net/ont/geosparql#Geometry`<br>curated: A coherent set of direct positions in space. The positions are held within a Spatial Reference System (SRS).<br>KG: Source: GeoSPARQL
- `http://www.opengis.net/ont/geosparql#SpatialObject`<br>curated: Anything spatial (being or having a shape, position or an extent).<br>KG: Source: GeoSPARQL
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfCrosses`<br>curated: Indicates that two geographic features cross each other (DE-9IM pattern T*T****** for line/area). Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `http://stko-kwg.geog.ucsb.edu/lod/ontology/sfEquals`<br>curated: Indicates that two geographic features are spatially equal (DE-9IM pattern TFFFTFFFT). Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.

## spoke-genelab

Curated row types: {'Class': 8, 'EdgeProperty': 20, 'NodeProperty': 34, 'Predicate': 9}

**Classes only in VoID** (1)

- `rdf:Statement`

**Predicates only in VoID** (5)

- `rdf:object`
- `rdf:predicate`
- `rdf:subject`
- `rdfs:comment`
- `rdfs:label`

**(source class, predicate) only in VoID** (10)

- `obo:OBI_0000070` → `rdfs:label`
- `rdf:Statement` → `rdf:object`
- `rdf:Statement` → `rdf:predicate`
- `rdf:Statement` → `rdf:subject`
- `kg:schema/MethylationRegion` → `rdfs:label`
- `kg:schema/Mission` → `rdfs:label`
- `kg:schema/Organism` → `rdfs:label`
- `biolink:Gene` → `rdfs:label`
- `biolink:Study` → `rdfs:comment`
- `biolink:Study` → `rdfs:label`

**Edges only in VoID** (8)

- `obo:OBI_0000070` → `kg:schema/material_id_1` → `biolink:AnatomicalEntity`
- `obo:OBI_0000070` → `kg:schema/material_id_1` → `biolink:Cell`
- `obo:OBI_0000070` → `kg:schema/material_id_2` → `biolink:AnatomicalEntity`
- `obo:OBI_0000070` → `kg:schema/material_id_2` → `biolink:Cell`
- `rdf:Statement` → `rdf:object` → `kg:schema/MethylationRegion`
- `rdf:Statement` → `rdf:object` → `kg:schema/Organism`
- `rdf:Statement` → `rdf:object` → `biolink:Gene`
- `rdf:Statement` → `rdf:subject` → `obo:OBI_0000070`

**Descriptions that differ** (1)

- `obo:OBI_0000070`<br>curated: Unique identifier for an assay instance in the NASA Open Science Data Repository (OSDR)<br>KG: A planned process that has the objective to produce information about a material entity (the evaluant) by examining it.

## spoke-okn

Curated row types: {'Class': 8, 'EdgeProperty': 41, 'NodeProperty': 48, 'Predicate': 38}

**Predicates only in VoID** (1)

- `rdf:`

**Predicates only curated** (1)

- `rdf:type`

**(source class, predicate) only in VoID** (22)

- `rdf:Statement` → `rdf:object`
- `rdf:Statement` → `rdf:predicate`
- `rdf:Statement` → `rdf:subject`
- `kg:schema/SDoH` → `dct:source`
- `kg:schema/SDoH` → `rdfs:comment`
- `kg:schema/SDoH` → `rdfs:label`
- `https://schema.org/AdministrativeArea` → `dct:source`
- `https://schema.org/AdministrativeArea` → `rdf:`
- `https://schema.org/AdministrativeArea` → `rdfs:label`
- `https://schema.org/AdministrativeArea` → `rdfs:seeAlso`
- `biolink:ChemicalEntity` → `dct:source`
- `biolink:ChemicalEntity` → `http://www.geneontology.org/formats/oboInOwl#hasDbXref`
- `biolink:ChemicalEntity` → `rdfs:label`
- `biolink:Disease` → `dct:source`
- `biolink:Disease` → `rdfs:label`
- `biolink:Disease` → `rdfs:seeAlso`
- `biolink:EnvironmentalFeature` → `dct:source`
- `biolink:EnvironmentalFeature` → `rdfs:label`
- `biolink:Gene` → `rdfs:comment`
- `biolink:Gene` → `rdfs:label`
- `biolink:OrganismTaxon` → `dct:source`
- `biolink:OrganismTaxon` → `rdfs:label`

**Edges only in VoID** (9)

- `rdf:Statement` → `rdf:object` → `https://schema.org/AdministrativeArea`
- `rdf:Statement` → `rdf:object` → `biolink:ChemicalEntity`
- `rdf:Statement` → `rdf:object` → `biolink:Disease`
- `rdf:Statement` → `rdf:subject` → `kg:schema/SDoH`
- `rdf:Statement` → `rdf:subject` → `https://schema.org/AdministrativeArea`
- `rdf:Statement` → `rdf:subject` → `biolink:ChemicalEntity`
- `rdf:Statement` → `rdf:subject` → `biolink:Disease`
- `rdf:Statement` → `rdf:subject` → `biolink:EnvironmentalFeature`
- `rdf:Statement` → `rdf:subject` → `biolink:OrganismTaxon`

**Edge properties (predicate, property) only in VoID** (42)

- `kg:schema/ASSOCIATES_SaD` → `dct:source`
- `kg:schema/ASSOCIATES_SaD` → `kg:schema/cooccur`
- `kg:schema/ASSOCIATES_SaD` → `kg:schema/enrichment`
- `kg:schema/ASSOCIATES_SaD` → `kg:schema/fisher`
- `kg:schema/ASSOCIATES_SaD` → `kg:schema/odds`
- `kg:schema/CONTRAINDICATES_CcD` → `dct:source`
- `kg:schema/CONTRAINDICATES_CcD` → `kg:schema/act_sources`
- `kg:schema/FOUNDIN_CfL` → `dct:source`
- `kg:schema/FOUNDIN_CfL` → `kg:schema/metrics`
- `kg:schema/FOUNDIN_CfL` → `kg:schema/unit`
- `kg:schema/FOUNDIN_CfL` → `kg:schema/value`
- `kg:schema/FOUNDIN_CfL` → `kg:schema/year`
- `kg:schema/FOUNDIN_EfL` → `dct:source`
- `kg:schema/FOUNDIN_EfL` → `kg:schema/metrics`
- `kg:schema/FOUNDIN_EfL` → `kg:schema/unit`
- `kg:schema/FOUNDIN_EfL` → `kg:schema/value`
- `kg:schema/FOUNDIN_EfL` → `kg:schema/year`
- `kg:schema/HASROLE_ChC` → `dct:source`
- `kg:schema/INTERACTS_CiC` → `dct:source`
- `kg:schema/INTERACTS_CiC` → `rdfs:comment`
- `kg:schema/ISA_CiC` → `dct:source`
- `kg:schema/ISA_DiD` → `dct:source`
- `kg:schema/ISOLATEDIN_OiL` → `dct:source`
- `kg:schema/MORTALITY_DmL` → `dct:source`
- `kg:schema/MORTALITY_DmL` → `kg:schema/value`
- … 17 more (see comparison.json)

**Edge properties (predicate, property) only curated** (9)

- `ASSOCIATES_SaD; RESEMBLES_DrD` → `kg:schema/cooccur`
- `ASSOCIATES_SaD; RESEMBLES_DrD` → `kg:schema/enrichment`
- `ASSOCIATES_SaD; RESEMBLES_DrD` → `kg:schema/fisher`
- `ASSOCIATES_SaD; RESEMBLES_DrD` → `kg:schema/odds`
- `CONTRAINDICATES_CcD; TREATS_CtD` → `kg:schema/act_sources`
- `FOUNDIN_CfL; FOUNDIN_EfL` → `kg:schema/metrics`
- `FOUNDIN_CfL; FOUNDIN_EfL` → `kg:schema/unit`
- `FOUNDIN_CfL; FOUNDIN_EfL; MORTALITY_DmL; PREVALENCE_DpL; PREVALENCEIN_SpL` → `kg:schema/value`
- `FOUNDIN_CfL; FOUNDIN_EfL; PREVALENCE_DpL; PREVALENCEIN_SpL` → `kg:schema/year`

**Curated class labels that resolve to no URI** (5)

- `ASSOCIATES_SaD; RESEMBLES_DrD`
- `CONTRAINDICATES_CcD; TREATS_CtD`
- `FOUNDIN_CfL; FOUNDIN_EfL`
- `FOUNDIN_CfL; FOUNDIN_EfL; MORTALITY_DmL; PREVALENCE_DpL; PREVALENCEIN_SpL`
- `FOUNDIN_CfL; FOUNDIN_EfL; PREVALENCE_DpL; PREVALENCEIN_SpL`

## sudokn

Curated row types: {'Class': 56, 'NodeProperty': 20, 'Predicate': 27}

**Classes only in VoID** (782)

- `http://asu.edu/semantics/SUDOKN/5-AxisMachiningCapability`
- `http://asu.edu/semantics/SUDOKN/7-AxisMachiningCapability`
- `http://asu.edu/semantics/SUDOKN/ABSProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AS9000Certificate`
- `http://asu.edu/semantics/SUDOKN/AS9003Certificate`
- `http://asu.edu/semantics/SUDOKN/AS9102Certificate`
- `http://asu.edu/semantics/SUDOKN/AS9120Certificate`
- `http://asu.edu/semantics/SUDOKN/ASMECertificate`
- `http://asu.edu/semantics/SUDOKN/AWSWelderCertificate`
- `http://asu.edu/semantics/SUDOKN/AbrasiveCleaningCapability`
- `http://asu.edu/semantics/SUDOKN/AbrasiveFinishingCapability`
- `http://asu.edu/semantics/SUDOKN/AbrassiveMachiningCapability`
- `http://asu.edu/semantics/SUDOKN/AcetalProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AcetronProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AcrylicProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AdhesiveBondingCapability`
- `http://asu.edu/semantics/SUDOKN/AerospaceQualityCertificate`
- `http://asu.edu/semantics/SUDOKN/AgeHardeningCapability`
- `http://asu.edu/semantics/SUDOKN/AgricultureIndustry`
- `http://asu.edu/semantics/SUDOKN/AirQuenchHardeningCapability`
- `http://asu.edu/semantics/SUDOKN/AlkalineOxideConversionCoatingCapability`
- `http://asu.edu/semantics/SUDOKN/AlloyProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AlloySteelProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AluminosilicateGlassProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/AnnealingCapability`
- … 757 more (see comparison.json)

**Classes only curated** (16)

- `http://asu.edu/semantics/SUDOKN/Certificate`
- `http://asu.edu/semantics/SUDOKN/Classifier`
- `http://asu.edu/semantics/SUDOKN/County`
- `http://asu.edu/semantics/SUDOKN/ManufacturingProcessCapability`
- `http://asu.edu/semantics/SUDOKN/MaterialProcessingCapability`
- `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `http://asu.edu/semantics/SUDOKN/OwnershipStatusClassifier`
- `http://asu.edu/semantics/SUDOKN/ProductCategoryClassifier`
- `http://asu.edu/semantics/SUDOKN/QualityManagementCapability`
- `http://asu.edu/semantics/SUDOKN/TwoDimensionalCartesianSpatialCoordinateDatum`
- `http://asu.edu/semantics/SUDOKN/USPostalCode`
- `http://asu.edu/semantics/SUDOKN/WomenOwned`
- `https://spec.industrialontologies.org/ontology/core/Core/Capability`
- `https://spec.industrialontologies.org/ontology/core/Core/Organization`
- `https://spec.industrialontologies.org/ontology/supplychain/SupplyChain/GeospatialSite`
- `https://spec.industrialontologies.org/ontology/supplychain/SupplyChain/Industry`

**Predicates only in VoID** (36)

- `http://asu.edu/semantics/SUDOKN/CityOf`
- `http://asu.edu/semantics/SUDOKN/countryOf`
- `http://asu.edu/semantics/SUDOKN/countyOf`
- `http://asu.edu/semantics/SUDOKN/hasIntegerValue`
- `http://asu.edu/semantics/SUDOKN/hasNAICSCodeValue`
- `http://asu.edu/semantics/SUDOKN/hasNAICSTextValue`
- `http://asu.edu/semantics/SUDOKN/hasName`
- `http://asu.edu/semantics/SUDOKN/stateOf`
- `dct:creator`
- `dct:description`
- `dct:license`
- `dct:source`
- `dct:title`
- `rdf:first`
- `rdf:rest`
- `rdfs:comment`
- `rdfs:definition`
- `rdfs:domain`
- `rdfs:range`
- `rdfs:subClassOf`
- `rdfs:subPropertyOf`
- `owl:disjointWith`
- `owl:imports`
- `owl:intersectionOf`
- `owl:inverseOf`
- … 11 more (see comparison.json)

**(source class, predicate) only in VoID** (69)

- `http://asu.edu/semantics/SUDOKN/GeospatialLocation` → `http://asu.edu/semantics/SUDOKN/hasLatitudeValue`
- `http://asu.edu/semantics/SUDOKN/GeospatialLocation` → `http://asu.edu/semantics/SUDOKN/hasLongitudeValue`
- `http://asu.edu/semantics/SUDOKN/NAICSClassifier` → `http://asu.edu/semantics/SUDOKN/hasNAICSCodeValue`
- `http://asu.edu/semantics/SUDOKN/NAICSClassifier` → `http://asu.edu/semantics/SUDOKN/hasNAICSTextValue`
- `http://asu.edu/semantics/SUDOKN/VirtualLocationIdentifier` → `http://asu.edu/semantics/SUDOKN/hasVirtualLocationIdentifierValue`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/hasLatitudeValue`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/hasLongitudeValue`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/locatedInCity`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/locatedInCountry`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/locatedInState`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry`
- `http://www.opengis.net/ont/geosparql#Feature` → `rdfs:label`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://schema.org/faxNumber`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://schema.org/postalCode`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://schema.org/streetAddress`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://schema.org/telephone`
- `owl:AllDisjointClasses` → `owl:members`
- `owl:Class` → `dct:source`
- `owl:Class` → `rdfs:comment`
- `owl:Class` → `rdfs:definition`
- `owl:Class` → `rdfs:label`
- `owl:Class` → `rdfs:subClassOf`
- `owl:Class` → `owl:disjointWith`
- `owl:Class` → `owl:intersectionOf`
- `owl:Class` → `skos:altLabel`
- … 44 more (see comparison.json)

**Edges only in VoID** (852)

- `http://asu.edu/semantics/SUDOKN/GeospatialSite` → `http://asu.edu/semantics/SUDOKN/hasGeospatialLocation` → `http://asu.edu/semantics/SUDOKN/GeospatialLocation`
- `http://asu.edu/semantics/SUDOKN/GeospatialSite` → `http://asu.edu/semantics/SUDOKN/hasGeospatialLocation` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://asu.edu/semantics/SUDOKN/GeospatialSite` → `http://asu.edu/semantics/SUDOKN/hasGeospatialLocation` → `https://schema.org/Place`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/locatedInCity` → `http://asu.edu/semantics/SUDOKN/City`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/locatedInCountry` → `http://asu.edu/semantics/SUDOKN/Country`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://asu.edu/semantics/SUDOKN/locatedInState` → `http://asu.edu/semantics/SUDOKN/State`
- `http://www.opengis.net/ont/geosparql#Feature` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`
- `http://www.opengis.net/ont/geosparql#Geometry` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `owl:Class` → `rdfs:subClassOf` → `owl:Class`
- `owl:Class` → `owl:disjointWith` → `owl:Class`
- `owl:DatatypeProperty` → `rdfs:domain` → `owl:Class`
- `owl:DatatypeProperty` → `rdfs:subPropertyOf` → `owl:DatatypeProperty`
- `owl:ObjectProperty` → `rdfs:domain` → `owl:Class`
- `owl:ObjectProperty` → `rdfs:range` → `owl:Class`
- `owl:ObjectProperty` → `rdfs:subPropertyOf` → `owl:ObjectProperty`
- `owl:ObjectProperty` → `owl:inverseOf` → `owl:ObjectProperty`
- `https://schema.org/Place` → `http://asu.edu/semantics/SUDOKN/locatedInCity` → `http://asu.edu/semantics/SUDOKN/City`
- `https://schema.org/Place` → `http://asu.edu/semantics/SUDOKN/locatedInCountry` → `http://asu.edu/semantics/SUDOKN/Country`
- `https://schema.org/Place` → `http://asu.edu/semantics/SUDOKN/locatedInState` → `http://asu.edu/semantics/SUDOKN/State`
- `https://schema.org/Place` → `http://www.opengis.net/ont/geosparql#hasGeometry` → `http://www.opengis.net/ont/geosparql#Geometry`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9000Certificate`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9003Certificate`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9100Certificate`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9102Certificate`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/AS9120Certificate`
- … 827 more (see comparison.json)

**Edges only curated** (7)

- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasCertificate` → `http://asu.edu/semantics/SUDOKN/Certificate`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasMaterialCapability` → `http://asu.edu/semantics/SUDOKN/MaterialProcessingCapability`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasOwnershipStatusClassifier` → `http://asu.edu/semantics/SUDOKN/OwnershipStatusClassifier`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasPrimaryNAICSClassifier` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasProcessCapability` → `http://asu.edu/semantics/SUDOKN/ManufacturingProcessCapability`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/hasSecondaryNAICSClassifier` → `http://asu.edu/semantics/SUDOKN/NAICSClassifier`
- `https://spec.industrialontologies.org/ontology/core/Core/Manufacturer` → `http://asu.edu/semantics/SUDOKN/suppliesToIndustry` → `https://spec.industrialontologies.org/ontology/supplychain/SupplyChain/Industry`

**Descriptions that differ** (15)

- `http://asu.edu/semantics/SUDOKN/MachiningCapability`<br>curated: A capability to perform machining operations.<br>KG: A process where material is selectively removed from a workpiece using cutting tools to create specific dimensions and surface quality.
- `http://asu.edu/semantics/SUDOKN/CastingCapability`<br>curated: A capability to perform casting operations.<br>KG: The process is where a liquid material, often molten metal poured or injected into a mold.
- `http://asu.edu/semantics/SUDOKN/CoatingCapability`<br>curated: A capability to perform coating operations.<br>KG: A process where a substrate is covered with a layer of material to improve surface properties such as appearance, adhesion, wetability, corrosion resistance, or wear resistance.
- `http://asu.edu/semantics/SUDOKN/FabricatingCapability`<br>curated: A capability to fabricate materials.<br>KG: A process that involves cutting, shaping, and assembling components to create finished products from raw or semi-finished materials.
- `http://asu.edu/semantics/SUDOKN/FormingCapability`<br>curated: A capability to form materials.<br>KG: A process where materials are deformed or reshaped without adding or removing material, typically involving bending, stretching, or compressing.
- `http://asu.edu/semantics/SUDOKN/JoiningCapability`<br>curated: A capability to join materials.<br>KG: A process where two or more materials are combined through methods such as welding, adhesive bonding, or mechanical fastening to form a single entity.
- `http://asu.edu/semantics/SUDOKN/CNCMachiningCapability`<br>curated: A capability to perform CNC machining.<br>KG: A process that utilizes computer-controlled machine tools to remove material from a workpiece, following a pre-programmed path, to create precise parts.
- `http://asu.edu/semantics/SUDOKN/AdditiveManufacturingCapability`<br>curated: A capability for additive manufacturing (3D printing).<br>KG: The process that creates three-dimensional objects by building them layer by layer from a digital model.
- `http://asu.edu/semantics/SUDOKN/attestsTo`<br>curated: Links a certificate to the capability it attests to. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- `http://asu.edu/semantics/SUDOKN/hasManagementCapability`<br>curated: Links an organization to a quality management capability. Declared in the schema but not populated in the current release.<br>KG: Declared in the schema but used in no triple or class axiom.
- … 5 more (see comparison.json)

## ufokn

Curated row types: {'Class': 6, 'Predicate': 17}

**(source class, predicate) only in VoID** (29)

- `https://schema.org/GeoCoordinates` → `https://schema.org/elevation`
- `https://schema.org/GeoCoordinates` → `https://schema.org/latitude`
- `https://schema.org/GeoCoordinates` → `https://schema.org/longitude`
- `https://schema.org/GeoShape` → `http://www.opengis.net/ont/geosparql#asWKT`
- `https://schema.org/GeoShape` → `https://schema.org/identifier`
- `https://schema.org/Observation` → `https://schema.org/description`
- `https://schema.org/Observation` → `https://schema.org/measuredProperty`
- `https://schema.org/Observation` → `https://schema.org/name`
- `https://schema.org/Observation` → `https://schema.org/observationAbout`
- `https://schema.org/Observation` → `https://schema.org/observationDate`
- `https://schema.org/Observation` → `https://schema.org/value`
- `https://schema.org/Observation` → `https://schema.org/variableMeasured`
- `https://schema.org/Place` → `https://schema.org/additionalType`
- `https://schema.org/Place` → `https://schema.org/description`
- `https://schema.org/Place` → `https://schema.org/geo`
- `https://schema.org/Place` → `https://schema.org/identifier`
- `https://schema.org/Place` → `https://schema.org/name`
- `https://schema.org/Place` → `https://schema.org/variableMeasured`
- `https://schema.org/PropertyValue` → `https://schema.org/additionalType`
- `https://schema.org/PropertyValue` → `https://schema.org/description`
- `https://schema.org/PropertyValue` → `https://schema.org/name`
- `https://schema.org/PropertyValue` → `https://schema.org/propertyID`
- `https://schema.org/PropertyValue` → `https://schema.org/unitCode`
- `https://schema.org/PropertyValue` → `https://schema.org/unitText`
- `https://schema.org/PropertyValue` → `https://schema.org/value`
- … 4 more (see comparison.json)

**Edges only in VoID** (9)

- `https://schema.org/GeoShape` → `http://www.opengis.net/ont/geosparql#asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://schema.org/GeoShape` → `https://schema.org/identifier` → `https://schema.org/PropertyValue`
- `https://schema.org/GeoShape` → `https://schema.org/identifier` → `https://stko-kwg.geog.ucsb.edu/lod/ontology#S2Cell`
- `https://schema.org/Observation` → `https://schema.org/observationAbout` → `https://schema.org/Place`
- `https://schema.org/Observation` → `https://schema.org/variableMeasured` → `https://schema.org/PropertyValue`
- `https://schema.org/Place` → `https://schema.org/geo` → `https://schema.org/GeoCoordinates`
- `https://schema.org/Place` → `https://schema.org/geo` → `https://schema.org/GeoShape`
- `https://schema.org/Place` → `https://schema.org/identifier` → `https://schema.org/PropertyValue`
- `https://schema.org/Place` → `https://schema.org/variableMeasured` → `https://schema.org/PropertyValue`

## wildlifekn

Curated row types: {'Class': 15, 'EdgeProperty': 12, 'NodeProperty': 44, 'Predicate': 18}

**(source class, predicate) only in VoID** (16)

- `http://www.opengis.net/ont/geosparql#Feature` → `rdfs:label`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/IN_STATE`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/additional_notes`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/api_url`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/county_fips`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/geo_asWKT`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/kwgIRI`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/lat4`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/latitude_dd`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/lon4`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/longitude_dd`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/old_name`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/site4key`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/state_abbrev`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/state_fips`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/state_name`

**Edges only in VoID** (8)

- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/IN_STATE` → `http://www.opengis.net/ont/geosparql#Feature`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/IN_STATE` → `https://kn-wildlife.crc.nd.edu/kg/State`
- `http://www.opengis.net/ont/geosparql#Feature` → `https://kn-wildlife.crc.nd.edu/kg/geo_asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://kn-wildlife.crc.nd.edu/kg/County` → `https://kn-wildlife.crc.nd.edu/kg/IN_STATE` → `http://www.opengis.net/ont/geosparql#Feature`
- `https://kn-wildlife.crc.nd.edu/kg/County` → `https://kn-wildlife.crc.nd.edu/kg/geo_asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://kn-wildlife.crc.nd.edu/kg/Observation` → `https://kn-wildlife.crc.nd.edu/kg/OBSERVED_IN` → `http://www.opengis.net/ont/geosparql#Feature`
- `https://kn-wildlife.crc.nd.edu/kg/Site` → `https://kn-wildlife.crc.nd.edu/kg/geo_asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
- `https://kn-wildlife.crc.nd.edu/kg/State` → `https://kn-wildlife.crc.nd.edu/kg/geo_asWKT` → `http://www.opengis.net/ont/geosparql#wktLiteral`
