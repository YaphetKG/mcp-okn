"""Render a transcript's Markdown as a standalone HTML page or a PDF.

``create_chat_transcript`` builds every transcript as Markdown first; the ``html``
and ``pdf`` formats are conversions of that exact document, so the queries, result
tables, and answer text are identical across formats. What changes is the diagrams:
each fenced ```mermaid block is drawn as an image by the latest release of one
Mermaid major version (``MERMAID_VERSION``) instead of being shown as source, so the
picture does not depend on whichever (often older) Mermaid the viewer — GitHub, an
IDE preview, … — happens to bundle.

- HTML: the page loads the newest ``MERMAID_VERSION``.x build from jsDelivr when
  opened and draws the diagrams, so it tracks Mermaid's 12.x releases (the same
  line mermaid.live runs). Only the drawn diagram is shown; the source is a hidden
  fallback that is revealed only if the script cannot load (e.g. offline).
- PDF: the same HTML page is opened in headless Chromium, the diagrams are drawn,
  and the page is printed. This needs the optional ``pdf`` extra
  (``pip install 'mcp-okn[pdf]'``) plus a Chromium — ``playwright install chromium``
  or an installed Google Chrome.
"""

from __future__ import annotations

import html as _html
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML

#: The Mermaid MAJOR version that draws diagrams in HTML/PDF transcripts. jsDelivr
#: resolves ``mermaid@12`` to the newest 12.x release, so diagrams pick up Mermaid's
#: fixes without a code change. (A moving file cannot carry a Subresource Integrity
#: hash; pin an exact version + SRI instead if reproducible rendering is ever needed.)
MERMAID_VERSION = "12"
MERMAID_LABEL = f"Mermaid {MERMAID_VERSION}.x"
MERMAID_JS_URL = (
    f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.min.js"
)

#: How long the PDF renderer waits for the diagrams to finish drawing.
PDF_RENDER_TIMEOUT_MS = 120_000

PDF_INSTALL_HINT = (
    "PDF rendering needs headless Chromium on the machine running mcp-okn: "
    "install the optional extra (`pip install 'mcp-okn[pdf]'`) and then a browser "
    "(`playwright install chromium`, or have Google Chrome installed). Until then, "
    "use format='html' and print the page to PDF from a browser — the diagrams are "
    f"drawn by the same {MERMAID_LABEL}."
)


class PdfRendererUnavailable(RuntimeError):
    """Raised when no headless Chromium is available to print the PDF."""


_CSS = """
:root { color-scheme: light; }
body {
  margin: 0 auto; max-width: 1100px; padding: 24px 16px 48px;
  font: 15px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial,
    sans-serif;
  color: #1f2328; background: #ffffff;
}
h1, h2, h3 { line-height: 1.25; margin: 1.6em 0 0.6em; }
h1 { font-size: 1.9em; border-bottom: 1px solid #d1d9e0; padding-bottom: 0.3em; }
h2 { font-size: 1.45em; border-bottom: 1px solid #d1d9e0; padding-bottom: 0.3em; }
h3 { font-size: 1.15em; }
a { color: #0969da; overflow-wrap: anywhere; }
hr { border: 0; border-top: 1px solid #d1d9e0; margin: 1.5em 0; }
code, pre { font: 12.5px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
:not(pre) > code { background: #eff1f3; padding: 0.15em 0.35em; border-radius: 4px; }
pre {
  background: #f6f8fa; border: 1px solid #d1d9e0; border-radius: 6px;
  padding: 12px 14px; overflow-x: auto;
}
blockquote { margin: 1em 0; padding: 0 1em; color: #59636e; border-left: 4px solid #d1d9e0; }
.table-wrap { overflow-x: auto; margin: 1em 0; }
table { border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #d1d9e0; padding: 5px 10px; text-align: left; vertical-align: top; }
th { background: #f6f8fa; }
.diagram { margin: 1em 0; text-align: center; overflow-x: auto; }
.diagram svg { max-width: 100%; height: auto; }
pre.mermaid { background: none; border: 0; padding: 0; }
pre.mermaid:not([data-processed]) { visibility: hidden; height: 0; margin: 0; }
html[data-mermaid="unavailable"] pre.mermaid {
  visibility: visible; height: auto; text-align: left;
  background: #f6f8fa; border: 1px solid #d1d9e0; padding: 12px 14px;
}
.render-note { display: none; color: #59636e; font-size: 13px; }
html[data-mermaid="unavailable"] .render-note { display: block; }
footer { margin-top: 3em; color: #59636e; font-size: 12px; }
@media print {
  body { max-width: none; padding: 0; font-size: 11pt; }
  pre { white-space: pre-wrap; overflow-wrap: anywhere; }
  .diagram, table, pre { break-inside: avoid; }
  h1, h2, h3 { break-after: avoid; }
}
"""

# Draw every diagram, then flag completion on <html data-mermaid="done"> — the PDF
# renderer waits on that flag. If the Mermaid script failed to load (e.g. offline),
# flag "unavailable" so the CSS reveals the diagram source
# instead of leaving blank space.
_SCRIPT = """
(function () {
  var root = document.documentElement;
  if (typeof mermaid === "undefined") { root.dataset.mermaid = "unavailable"; return; }
  mermaid.initialize({ startOnLoad: false, securityLevel: "strict", maxTextSize: 1000000 });
  mermaid.run({ querySelector: "pre.mermaid", suppressErrors: true })
    .catch(function (err) { console.error(err); })
    .finally(function () { root.dataset.mermaid = "done"; });
})();
"""


def _markdown_renderer() -> MarkdownIt:
    """Return a GitHub-like Markdown renderer that turns mermaid fences into diagrams.

    Raw HTML in the Markdown is escaped, not passed through: result-table cells hold
    knowledge-graph literals verbatim, and a stray ``<script>`` in one must never run.
    """
    md = MarkdownIt("gfm-like", {"html": False})

    def fence(
        self: Any, tokens: Any, idx: int, options: Any, env: Any
    ) -> str:  # markdown-it render-rule signature
        token = tokens[idx]
        if token.info.strip().split(" ", 1)[0].lower() == "mermaid":
            return (
                '<div class="diagram"><pre class="mermaid">'
                f"{_html.escape(token.content)}</pre></div>\n"
            )
        return RendererHTML.fence(self, tokens, idx, options, env)

    md.add_render_rule("fence", fence)

    def table_open(self: Any, tokens: Any, idx: int, options: Any, env: Any) -> str:
        return '<div class="table-wrap"><table>\n'

    def table_close(self: Any, tokens: Any, idx: int, options: Any, env: Any) -> str:
        return "</table></div>\n"

    md.add_render_rule("table_open", table_open)
    md.add_render_rule("table_close", table_close)
    return md


def markdown_to_html(markdown: str, title: str) -> str:
    """Convert a transcript's Markdown into a standalone HTML page.

    Args:
        markdown: The complete transcript Markdown, exactly as
            ``create_chat_transcript`` renders it.
        title: Page title (the transcript's H1 text).

    Returns:
        A single self-contained HTML document. Diagrams are drawn in the browser by
        the latest Mermaid ``MERMAID_VERSION``.x; everything else is static HTML.
    """
    body = _markdown_renderer().render(markdown)
    has_diagrams = 'class="mermaid"' in body
    script = (
        f'<script src="{MERMAID_JS_URL}"></script>\n<script>{_SCRIPT}</script>\n'
        if has_diagrams
        else ""
    )
    note = (
        '<p class="render-note">Diagrams are drawn by '
        f"{MERMAID_LABEL}, loaded from jsDelivr; it could not be loaded, so their "
        "source is shown instead.</p>\n"
        if has_diagrams
        else ""
    )
    footer = (
        f"<footer>Diagrams rendered with {MERMAID_LABEL}.</footer>\n"
        if has_diagrams
        else ""
    )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_html.escape(title)}</title>\n"
        f"<style>{_CSS}</style>\n</head>\n<body>\n"
        f"{note}{body}{footer}{script}</body>\n</html>\n"
    )


async def html_to_pdf(page_html: str) -> bytes:
    """Print an HTML transcript page to PDF in headless Chromium.

    Opens the page, waits for Mermaid to finish drawing every diagram, and prints it
    (US Letter, backgrounds on). Uses Playwright's bundled Chromium when installed,
    otherwise an installed Google Chrome.

    Raises:
        PdfRendererUnavailable: Playwright or a Chromium is missing, or the
            Mermaid script could not be loaded (so the diagrams would be missing).
    """
    try:
        from playwright.async_api import Error as PlaywrightError
        from playwright.async_api import async_playwright
    except ImportError as exc:
        raise PdfRendererUnavailable(PDF_INSTALL_HINT) from exc

    async with async_playwright() as p:
        browser = None
        # Playwright's own Chromium first, then an installed Google Chrome.
        for channel in (None, "chrome"):
            try:
                browser = await p.chromium.launch(channel=channel)
                break
            except PlaywrightError:
                continue
        if browser is None:
            raise PdfRendererUnavailable(PDF_INSTALL_HINT)
        try:
            page = await browser.new_page()
            await page.set_content(page_html, wait_until="load")
            if '<pre class="mermaid">' in page_html:
                await page.wait_for_function(
                    "document.documentElement.dataset.mermaid !== undefined",
                    timeout=PDF_RENDER_TIMEOUT_MS,
                )
                state = await page.evaluate("document.documentElement.dataset.mermaid")
                if state != "done":
                    raise PdfRendererUnavailable(
                        f"{MERMAID_LABEL} could not be loaded from "
                        f"{MERMAID_JS_URL}, so the PDF would have no diagrams. Check "
                        "that this machine can reach jsDelivr."
                    )
            pdf = await page.pdf(
                format="Letter",
                print_background=True,
                margin={
                    "top": "0.6in",
                    "bottom": "0.6in",
                    "left": "0.5in",
                    "right": "0.5in",
                },
            )
        finally:
            await browser.close()
    return bytes(pdf)
