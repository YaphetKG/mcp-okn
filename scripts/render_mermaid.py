"""Render Mermaid diagrams in headless Chromium: a smoke test that they draw.

A diagram that is valid text can still fail to render, or render unreadably (bio101
once drew 246 classes in a 36,000 px row). This loads each diagram into the real
Mermaid library — the same major version the transcript HTML uses
(``transcript_render.MERMAID_VERSION``, newest release from jsDelivr) — parses and
renders it, reports the drawn size, and saves the image.

Targets are KG shortnames (the diagram comes from ``visualize_schema``, so
``MCP_OKN_ENTITY_METADATA_BASE`` applies) or ``.mmd`` files.

Needs Playwright (``pip install 'mcp-okn[pdf]'``) and a Chromium: Playwright's own
(``playwright install chromium``) or an installed Google Chrome. Needs network
access to cdn.jsdelivr.net.

Usage:
    uv run python scripts/render_mermaid.py spoke-genelab bio101
    uv run python scripts/render_mermaid.py diagram.mmd --format svg --out renders/
    MCP_OKN_ENTITY_METADATA_BASE=metadata/void_entities \\
        uv run python scripts/render_mermaid.py bio101

Exit codes: 0 every diagram rendered, 1 a diagram failed to parse or render,
2 no Playwright/Chromium or Mermaid could not be loaded.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp_okn import schema
from mcp_okn.transcript_render import MERMAID_VERSION

#: Screenshots wider than this are clipped (Chromium's texture limit is ~16k px).
MAX_SCREENSHOT_PX = 16000
RENDER_TIMEOUT_MS = 180_000


def _js_string(text: str) -> str:
    """A JS string literal safe inside <script>: ``</`` would end the element."""
    return json.dumps(text).replace("</", "<\\/")


def page_html(source: str, version: str) -> str:
    """A page that parses and renders one diagram at its natural size.

    It sets ``window.result`` to ``"ok"`` or ``"ERROR <message>"``, or
    ``"LOAD-FAILED"`` when the Mermaid module itself cannot be imported.
    """
    url = f"https://cdn.jsdelivr.net/npm/mermaid@{version}/dist/mermaid.esm.min.mjs"
    return f"""<!doctype html><html><body style="margin:0;background:#fff">
<div id="out"></div>
<script type="module">
  let mermaid;
  try {{ mermaid = (await import({json.dumps(url)})).default; }}
  catch (e) {{ window.result = "LOAD-FAILED " + (e.message || e); }}
  if (mermaid) {{
    mermaid.initialize({{ startOnLoad: false, maxTextSize: 500000,
                          class: {{ useMaxWidth: false }}, flowchart: {{ useMaxWidth: false }} }});
    const src = {_js_string(source)};
    try {{
      await mermaid.parse(src);
      const r = await mermaid.render("diagram", src);
      document.getElementById("out").innerHTML = r.svg;
      window.result = "ok";
    }} catch (e) {{ window.result = "ERROR " + (e.message || e); }}
  }}
</script></body></html>"""


async def _diagram_for(target: str) -> tuple[str, str, str]:
    """``(name, mermaid source, note)`` for a ``.mmd`` path or a KG shortname."""
    path = Path(target)
    if path.suffix == ".mmd" or path.exists():
        return path.stem, path.read_text(), ""
    result = await schema.visualize_schema(target)
    if "error" in result:
        raise ValueError(f"{target}: {result['error']}")
    return target, result["mermaid"], result.get("note", "")


async def render_all(targets: list[str], out: Path, fmt: str, version: str) -> int:
    try:
        from playwright.async_api import Error as PlaywrightError
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright is not installed: pip install 'mcp-okn[pdf]'")
        return 2

    out.mkdir(parents=True, exist_ok=True)
    failed = 0
    async with async_playwright() as p:
        browser = None
        for channel in (None, "chrome"):  # Playwright's Chromium, then Google Chrome
            try:
                browser = await p.chromium.launch(channel=channel)
                break
            except PlaywrightError:
                continue
        if browser is None:
            print("No Chromium: run `playwright install chromium` or install Chrome")
            return 2
        for target in targets:
            try:
                name, source, note = await _diagram_for(target)
            except (OSError, ValueError) as exc:
                print(f"FAIL  {target}: {exc}")
                failed += 1
                continue
            # A fresh page per diagram: set_content keeps the old window, so the
            # previous diagram's window.result would end the wait immediately.
            page = await browser.new_page(viewport={"width": 1600, "height": 1200})
            await page.set_content(page_html(source, version))
            try:
                await page.wait_for_function(
                    "window.result !== undefined", timeout=RENDER_TIMEOUT_MS
                )
            except PlaywrightError:
                print(f"FAIL  {name}: not drawn within {RENDER_TIMEOUT_MS // 1000} s")
                failed += 1
                await page.close()
                continue
            result = await page.evaluate("window.result")
            if result.startswith("LOAD-FAILED"):
                print(f"Mermaid {version} could not be loaded from jsDelivr: {result}")
                await browser.close()
                return 2
            if result != "ok":
                print(f"FAIL  {name}: {result}")
                failed += 1
                await page.close()
                continue
            stats: dict[str, Any] | None = await page.evaluate(
                """(() => { const s = document.querySelector('#out svg');
                    if (!s) return null;
                    const b = s.getBBox();
                    return {w: Math.round(b.width), h: Math.round(b.height),
                            nodes: s.querySelectorAll('g.node').length}; })()"""
            )
            if stats is None:
                print(f"FAIL  {name}: Mermaid reported success but drew no SVG")
                failed += 1
                await page.close()
                continue
            (out / f"{name}.mmd").write_text(
                source if source.endswith("\n") else source + "\n"
            )
            saved = []
            if fmt in ("svg", "both"):
                svg = await page.evaluate(
                    "document.querySelector('#out svg').outerHTML"
                )
                (out / f"{name}.svg").write_text(svg)
                saved.append(f"{name}.svg")
            if fmt in ("png", "both"):
                width = min(stats["w"] + 40, MAX_SCREENSHOT_PX)
                await page.set_viewport_size({"width": width, "height": 1200})
                await page.locator("#out svg").screenshot(path=str(out / f"{name}.png"))
                saved.append(f"{name}.png")
            clipped = " (PNG clipped)" if stats["w"] + 40 > MAX_SCREENSHOT_PX else ""
            print(
                f"OK    {name}: {stats['w']:,} x {stats['h']:,} px, {stats['nodes']} "
                f"boxes{clipped} -> {', '.join(saved)}"
            )
            if note:
                print(f"      note: {note}")
            await page.close()
        await browser.close()
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("targets", nargs="+", help="KG shortnames or .mmd files")
    parser.add_argument(
        "--out", type=Path, default=Path("diagram_renders"), help="output directory"
    )
    parser.add_argument("--format", choices=("png", "svg", "both"), default="png")
    parser.add_argument(
        "--mermaid",
        default=MERMAID_VERSION,
        help="Mermaid version (default: %(default)s)",
    )
    args = parser.parse_args()
    return asyncio.run(render_all(args.targets, args.out, args.format, args.mermaid))


if __name__ == "__main__":
    sys.exit(main())
