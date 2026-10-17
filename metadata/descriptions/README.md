# KG descriptions

One plain-text description per knowledge graph, `<shortname>.txt`. `describe_kg`
appends the file to the registry text under a `Summary` heading, as mcp-proto-okn did.

40 of the files were copied verbatim from `sbl-sdsc/mcp-proto-okn`
(`metadata/descriptions/`, commit `4f3a4e9`) on 2026-10-16, so mcp-okn no longer reads
anything from that repository. They are maintained here from now on.

mcp-proto-okn had no file for five KGs. Those five were written here on 2026-10-16:
`babel`, `identifier-mappings`, `okn-void`, `ubergraph` and `wikidata`. Their facts
come from:
- the KG's registry entry;
- this server's own usage notes and crosswalks;
- counts taken that day, from the `okn-void` statistics and from live queries of
  the graphs (identifier-mappings' link targets and ubergraph's ontology list).

Re-check those counts after a redeploy.

A KG with no file gets the registry text alone in `describe_kg`.

The one-line descriptions in `list_kgs` and the longer text in `describe_kg` still come
from the KG registry, `frink-okn/okn-registry`, which the KGs' maintainers publish.
