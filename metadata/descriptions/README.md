# KG descriptions

One plain-text description per knowledge graph, `<shortname>.txt`. `describe_kg`
appends the file to the registry text under a `Summary` heading, as mcp-proto-okn did.

The 40 files were copied verbatim from `sbl-sdsc/mcp-proto-okn`
(`metadata/descriptions/`, commit `4f3a4e9`) on 2026-10-16, so mcp-okn no longer reads
anything from that repository. They are maintained here from now on.

Five KGs have no file: `babel`, `identifier-mappings`, `okn-void`, `ubergraph` and
`wikidata`. For those, `describe_kg` returns the registry text alone.

The one-line descriptions in `list_kgs` and the longer text in `describe_kg` still come
from the KG registry, `frink-okn/okn-registry`, which the KGs' maintainers publish.
