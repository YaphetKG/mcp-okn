"""Tests for scripts/render_mermaid.py (the page it builds; rendering needs Chromium)."""

import importlib.util
import json
from pathlib import Path

from mcp_okn.transcript_render import MERMAID_VERSION

_spec = importlib.util.spec_from_file_location(
    "render_mermaid", Path(__file__).parent.parent / "scripts" / "render_mermaid.py"
)
assert _spec and _spec.loader
render_mermaid = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(render_mermaid)


def test_page_loads_the_transcript_mermaid_version_and_embeds_the_source():
    src = 'classDiagram\n  class A["quoted </script> label"]\n'
    html = render_mermaid.page_html(src, MERMAID_VERSION)
    assert f"mermaid@{MERMAID_VERSION}/dist/mermaid.esm.min.mjs" in html
    assert "</script> label" not in html  # would close the page's <script> early
    assert json.dumps(src).replace("</", "<\\/") in html
    assert "useMaxWidth: false" in html  # natural size, not squeezed to the page
    assert "LOAD-FAILED" in html and 'window.result = "ok"' in html


async def test_mmd_targets_are_read_from_disk(tmp_path):
    f = tmp_path / "x.mmd"
    f.write_text("classDiagram\n  class A\n")
    assert await render_mermaid._diagram_for(str(f)) == (
        "x",
        "classDiagram\n  class A\n",
        "",
    )
