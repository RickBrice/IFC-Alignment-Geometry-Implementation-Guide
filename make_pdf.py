#!/usr/bin/env python3
"""Combine IFC Alignment Guide chapters into a single PDF via Playwright."""

import re
from pathlib import Path

import mistune

ROOT = Path(__file__).parent
OUTPUT_HTML = ROOT / "IFC_Alignment_Guide.html"
OUTPUT_PDF = ROOT / "IFC_Alignment_Guide.pdf"

CHAPTERS = [
    "Cover.md",
    "Foreword.md",
    "TableOfContents.md",
    "Notation.md",
    "1_Introduction.md",
    "2_Horizontal.md",
    "3_Vertical.md",
    "4_Cant.md",
    "5_LinearPlacement.md",
    "6_OffsetCurves.md",
    "7_Referents_and_Stationing.md",
    "8_Specialized_Infrastructure_Geometry.md",
    "9_LandXML.md",
    "10_Precision_and_Tolerance.md",
    "11_Examples_and_Validation_Data.md",
]

# ── Math protection ──────────────────────────────────────────────────────────
# mistune may mangle LaTeX inside $...$ / $$...$$. We swap them with
# opaque placeholders before conversion and restore them after.

_math_store: list[tuple[str, str]] = []  # (tag, original)


def _protect_math(text: str) -> str:
    """Replace $$...$$ and $...$ spans with placeholders."""
    _math_store.clear()
    out = []
    i = 0
    n = len(text)
    while i < n:
        # Display math $$...$$
        if text[i : i + 2] == "$$":
            end = text.find("$$", i + 2)
            if end != -1:
                original = text[i : end + 2]
                tag = f"XMATHBLOCKX{len(_math_store)}XMATHBLOCKX"
                _math_store.append((tag, original))
                out.append(tag)
                i = end + 2
                continue
        # Inline math $...$  (must not span a newline)
        if text[i] == "$":
            end = text.find("$", i + 1)
            if end != -1 and "\n" not in text[i + 1 : end]:
                original = text[i : end + 1]
                tag = f"XMATHINLINEX{len(_math_store)}XMATHINLINEX"
                _math_store.append((tag, original))
                out.append(tag)
                i = end + 1
                continue
        out.append(text[i])
        i += 1
    return "".join(out)


def _restore_math(html: str) -> str:
    for tag, original in _math_store:
        html = html.replace(tag, original)
    return html


# ── Markdown → HTML ──────────────────────────────────────────────────────────

_md = mistune.create_markdown(plugins=["table", "footnotes", "url"], escape=False)


def _chapter_html(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    protected = _protect_math(text)
    html = _md(protected)
    html = _restore_math(html)
    return html


def _fix_img_paths(html: str) -> str:
    """Make relative img src paths absolute so Edge can load them."""

    def repl(m: re.Match) -> str:
        src = m.group(1)
        if re.match(r"(https?://|data:|file://)", src):
            return m.group(0)
        abs_path = (ROOT / src).resolve()
        return f'src="file:///{abs_path.as_posix()}"'

    return re.sub(r'src="([^"]*)"', repl, html)


# ── HTML shell ───────────────────────────────────────────────────────────────

HTML_HEAD = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>IFC4x3 Alignment Geometry Implementation Guide</title>
<script>
MathJax = {
  tex: {
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']],
    processEscapes: true,
    tags: 'ams',
  },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre'] },
};
</script>
<script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
<style>
@page { size: letter; margin: 0.9in 0.85in; }
body {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 12pt;
  line-height: 1.65;
  color: #111;
  max-width: none;
}
h1 { font-size: 1.9em; border-bottom: 2px solid #222; margin-top: 2em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-size: 1.45em; border-bottom: 1px solid #555; margin-top: 1.4em; }
h3 { font-size: 1.18em; margin-top: 1.1em; }
h4 { font-size: 1.05em; }
h5, h6 { font-size: 1em; font-style: italic; }
code {
  font-family: Consolas, 'Courier New', monospace;
  background: #f2f2f2;
  padding: 0.1em 0.3em;
  border-radius: 3px;
  font-size: 0.88em;
}
pre {
  background: #f2f2f2;
  border: 1px solid #ccc;
  border-radius: 4px;
  padding: 0.75em 1em;
  overflow-x: auto;
  font-size: 0.83em;
  line-height: 1.45;
  page-break-inside: avoid;
}
pre code { background: none; padding: 0; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; page-break-inside: avoid; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  font-size: 0.9em;
  page-break-inside: avoid;
}
th, td { border: 1px solid #bbb; padding: 0.35em 0.6em; text-align: left; }
th { background: #e8e8e8; font-weight: bold; }
tr:nth-child(even) { background: #f9f9f9; }
blockquote {
  border-left: 4px solid #999;
  margin: 1em 0 1em 1em;
  padding: 0.4em 1em;
  color: #444;
}
hr { border: none; border-top: 1px solid #bbb; margin: 2em 0; }
.chapter-sep { page-break-before: always; }
a { color: #1a4f8a; }
</style>
</head>
<body>
"""

HTML_TAIL = "\n</body>\n</html>\n"


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Building combined HTML...")
    parts: list[str] = []

    for i, name in enumerate(CHAPTERS):
        path = ROOT / name
        if not path.exists():
            print(f"  SKIP (not found): {name}")
            continue
        print(f"  {name}")
        html = _chapter_html(path)
        html = _fix_img_paths(html)
        sep = "" if i == 0 else '<div class="chapter-sep"></div>\n'
        parts.append(sep + html)

    body = "\n".join(parts)
    full = HTML_HEAD + body + HTML_TAIL
    OUTPUT_HTML.write_text(full, encoding="utf-8")
    print(f"HTML -> {OUTPUT_HTML}")

    print("Rendering PDF via Playwright (this may take ~60 s for MathJax)...")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright first:")
        print("  pip install playwright && playwright install chromium")
        return

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(f"file:///{OUTPUT_HTML.as_posix()}", wait_until="networkidle")
        # Wait for MathJax to finish typesetting before capturing the PDF.
        try:
            page.wait_for_function(
                "window.MathJax && window.MathJax.startup && window.MathJax.startup.promise",
                timeout=45_000,
            )
            page.evaluate("() => window.MathJax.startup.promise")
        except Exception:
            pass  # proceed even if MathJax times out
        page.wait_for_timeout(2_000)
        page.pdf(
            path=str(OUTPUT_PDF),
            format="Letter",
            display_header_footer=False,
            print_background=True,
        )
        browser.close()

    if OUTPUT_PDF.exists() and OUTPUT_PDF.stat().st_size > 1000:
        size_mb = OUTPUT_PDF.stat().st_size / 1_048_576
        print(f"PDF -> {OUTPUT_PDF}  ({size_mb:.1f} MB)")
    else:
        print("PDF generation may have failed.")


if __name__ == "__main__":
    main()
