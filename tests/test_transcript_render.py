import tempfile

import pytest
from mcp.types import ResourceLink, TextContent

from mcp_okn import session
from mcp_okn.server import (
    create_chat_transcript,
    latest_transcript_html_resource,
    latest_transcript_pdf_resource,
    latest_transcript_resource,
)
from mcp_okn.tools import transcript as transcript_mod
from mcp_okn.transcript_render import (
    MERMAID_JS_URL,
    MERMAID_LABEL,
    PdfRendererUnavailable,
    markdown_to_html,
)


@pytest.fixture(autouse=True)
def clean_log():
    session.reset()
    yield
    session.reset()


DIAGRAM = "classDiagram\nclass Gene\nGene --> Gene : IS_ORTHOLOG_MGiG"
EXCHANGES = [
    {
        "prompt": "Visualize the schema",
        "answer": "Here is the **schema**.",
        "mermaid": DIAGRAM,
    }
]
QUERY = (
    "SELECT ?s WHERE { GRAPH <https://purl.org/okn/frink/kg/spoke-genelab> "
    "{ ?s a <https://w3id.org/biolink/vocab/Study> } } LIMIT 1"
)


def _log_query(label="Study <script>alert(1)</script> | x"):
    session.record(
        QUERY,
        "json",
        result={"vars": ["s"], "rows": [{"s": label}], "row_count": 1},
    )


def test_mermaid_tracks_latest_12x():
    # A major-version range: jsDelivr serves the newest 12.x release.
    assert "/npm/mermaid@12/dist/mermaid.min.js" in MERMAID_JS_URL
    assert MERMAID_LABEL == "Mermaid 12.x"


def test_markdown_to_html_draws_mermaid_without_showing_source_fence():
    md = f"# T\n\n```mermaid\n{DIAGRAM}\n```\n\n```sparql\nSELECT * {{}}\n```\n"
    page = markdown_to_html(md, "T")
    assert page.startswith("<!doctype html>")
    assert '<pre class="mermaid">' in page
    assert "```mermaid" not in page
    assert "Gene --&gt; Gene" in page  # escaped, handed to Mermaid to draw
    assert '<code class="language-sparql">' in page  # other fences stay code
    assert f'<script src="{MERMAID_JS_URL}"></script>' in page
    assert MERMAID_LABEL in page


def test_markdown_to_html_without_diagrams_loads_no_script():
    page = markdown_to_html("# T\n\nplain text\n", "T")
    assert "<script" not in page
    assert "<p>plain text</p>" in page


def test_markdown_to_html_escapes_raw_html_and_wraps_tables():
    md = "| a |\n|---|\n| <script>x</script> |\n"
    page = markdown_to_html(md, "<T>")
    assert "<script>x</script>" not in page
    assert "&lt;script&gt;x&lt;/script&gt;" in page
    assert '<div class="table-wrap"><table>' in page
    assert "<title>&lt;T&gt;</title>" in page


async def test_html_format_returns_page_and_publishes_resources():
    _log_query()
    page = await create_chat_transcript(
        model="claude-opus-5-5", exchanges=EXCHANGES, format="html", skills=["s v1"]
    )
    assert page.startswith("<!doctype html>")
    assert page.count('<pre class="mermaid">') == 2  # inline diagram + query diagram
    assert "```" not in page
    # A KG literal can never inject markup into the page.
    assert "<script>alert(1)</script>" not in page
    assert latest_transcript_html_resource() == page
    # The markdown it was converted from is still published as before.
    assert latest_transcript_resource().startswith("# Proto-OKN Chat Transcript")


async def test_html_format_prepends_warnings_as_comments():
    page = await create_chat_transcript(
        model="claude-opus-5-5", exchanges=EXCHANGES, format="html"
    )
    assert page.startswith("<!-- mcp-okn WARNING: no `skills=` passed")
    assert "<!doctype html>" in page


async def test_html_format_over_limit_returns_stub_pointing_at_html_resource():
    _log_query()
    out = await create_chat_transcript(
        model="claude-opus-5-5",
        exchanges=EXCHANGES,
        format="html",
        skills=["s v1"],
        max_inline_chars=500,
    )
    assert "full transcript delivered via resource" in out
    assert "`transcript://session/latest.html`" in out
    assert latest_transcript_html_resource().startswith("<!doctype html>")


async def test_pdf_format_reports_missing_renderer(monkeypatch):
    async def unavailable(page_html):
        raise PdfRendererUnavailable("no chromium")

    monkeypatch.setattr(transcript_mod, "html_to_pdf", unavailable)
    out = await create_chat_transcript(
        model="claude-opus-5-5", exchanges=EXCHANGES, format="pdf", skills=["s v1"]
    )
    assert out["error"] == "no chromium"
    assert out["html_resource"] == "transcript://session/latest.html"
    # The HTML rendering is still available as the fallback.
    assert latest_transcript_html_resource().startswith("<!doctype html>")


async def test_pdf_format_links_resource_and_writes_file(monkeypatch, tmp_path):
    seen = {}

    async def fake_pdf(page_html):
        seen["html"] = page_html
        return b"%PDF-1.7 fake"

    monkeypatch.setattr(transcript_mod, "html_to_pdf", fake_pdf)
    monkeypatch.setattr(tempfile, "tempdir", str(tmp_path))
    out = await create_chat_transcript(
        model="claude-opus-5-5",
        exchanges=EXCHANGES,
        format="pdf",
        title="My Transcript",
        date="2026-10-14",
        skills=["s v1"],
    )
    text, link = out
    assert isinstance(text, TextContent)
    assert isinstance(link, ResourceLink)
    assert str(link.uri) == "transcript://session/latest.pdf"
    assert link.mimeType == "application/pdf"
    assert MERMAID_LABEL in text.text
    assert '<pre class="mermaid">' in seen["html"]  # printed from the HTML page
    written = tmp_path / "mcp-okn-transcripts" / "my-transcript-2026-10-14.pdf"
    assert written.read_bytes() == b"%PDF-1.7 fake"
    assert latest_transcript_pdf_resource() == b"%PDF-1.7 fake"


def test_pdf_resource_fails_loudly_before_any_pdf():
    with pytest.raises(ValueError, match="No PDF transcript yet"):
        latest_transcript_pdf_resource()


async def test_unsupported_format_lists_all_formats():
    out = await create_chat_transcript(model="m", format="docx")
    assert "'markdown', 'html', 'pdf', or 'json'" in out["error"]
