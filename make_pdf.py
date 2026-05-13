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
    "1_IFC_Alignment_Concepts.md",
    "2_Horizontal_Alignments.md",
    "3_Vertical_Alignments.md",
    "4_Cant_Alignments.md",
    "5_OffsetCurves.md",
    "6_Approximate_Alignment_Geometry.md",
    "7_Alignments_Reusing_Horizontal_Layout.md",
    "8_LinearPlacement.md",
    "9_Referents_and_Stationing.md",
    "10_Specialized_Infrastructure_Geometry.md",
    "11_LandXML.md",
    "12_Precision_and_Tolerance.md",
    "13_Examples_and_Validation_Data.md",
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


def _md_to_html(text: str) -> str:
    protected = _protect_math(text)
    html = _md(protected)
    html = _restore_math(html)
    return html


def _chapter_html(path: Path) -> str:
    return _md_to_html(path.read_text(encoding="utf-8"))


# ── Bookmark extraction ───────────────────────────────────────────────────────

_INLINE_MD = re.compile(r'`([^`]+)`|\*\*([^*]+)\*\*|\*([^*]+)\*|\[([^\]]+)\]\([^)]+\)')


def _strip_inline(text: str) -> str:
    """Remove inline markdown formatting so heading text matches rendered PDF."""
    return _INLINE_MD.sub(lambda m: next(g for g in m.groups() if g is not None), text).strip()


def _extract_headings(text: str, max_level: int = 3) -> list[tuple[int, str]]:
    """Return (level, cleaned_text) for headings up to max_level in a markdown string."""
    headings = []
    pattern = re.compile(rf'^(#{{1,{max_level}}})\s+(.+)')
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            headings.append((len(m.group(1)), _strip_inline(m.group(2))))
    return headings


def _collapse_outline_items(writer) -> None:
    """Set all outline items to start collapsed (negative /Count)."""
    from pypdf.generic import NameObject, NumberObject

    root = writer._root_object
    outlines_key = NameObject("/Outlines")
    if outlines_key not in root:
        return

    def visit(node_obj: object) -> None:
        first_key = NameObject("/First")
        next_key = NameObject("/Next")
        count_key = NameObject("/Count")
        if first_key not in node_obj:
            return
        child_ref = node_obj[first_key]
        while child_ref is not None:
            child = child_ref.get_object()
            visit(child)
            if count_key in child and int(child[count_key]) > 0:
                child[count_key] = NumberObject(-int(child[count_key]))
            child_ref = child.get(next_key)

    visit(root[outlines_key].get_object())


def _add_pdf_bookmarks(pdf_path: Path, headings: list[tuple[int, str]]) -> None:
    """Post-process the PDF to insert an outline/bookmark tree."""
    try:
        import pypdf
    except ImportError:
        print("pypdf not installed; skipping bookmarks.  Run: pip install pypdf")
        return

    reader = pypdf.PdfReader(str(pdf_path))
    writer = pypdf.PdfWriter()
    writer.append(reader)

    page_texts = [page.extract_text() or "" for page in reader.pages]

    def find_page(text: str) -> int:
        for i, pt in enumerate(page_texts):
            if text in pt:
                return i
        return 0

    stack: list[tuple[int, object]] = []  # (level, outline_item)
    for level, text in headings:
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else None
        item = writer.add_outline_item(text, find_page(text), parent=parent)
        stack.append((level, item))

    _collapse_outline_items(writer)

    with open(str(pdf_path), "wb") as f:
        writer.write(f)

    print(f"Bookmarks: {len(headings)} entries added.")


def _fix_img_paths(html: str) -> str:
    """Make relative img src paths absolute so Edge can load them."""

    def repl(m: re.Match) -> str:
        src = m.group(1)
        if re.match(r"(https?://|data:|file://)", src):
            return m.group(0)
        abs_path = (ROOT / src).resolve()
        return f'src="file:///{abs_path.as_posix()}"'

    return re.sub(r'src="([^"]*)"', repl, html)


# ── Internal link translation ─────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """GitHub-compatible heading slug: lowercase, spaces→hyphens, strip punctuation."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)   # remove punctuation (keep word chars, spaces, hyphens)
    text = re.sub(r'\s+', '-', text)        # spaces → hyphens
    return re.sub(r'-{2,}', '-', text).strip('-')


def _add_heading_ids(html: str, seen: dict[str, int]) -> str:
    """Add id= attributes to every h1-h6 element using GitHub-style slugs.

    seen is a cross-chapter duplicate counter so the same heading text in
    different chapters gets a unique id (e.g. 'introduction', 'introduction-1').
    """
    def repl(m: re.Match) -> str:
        lvl, inner = m.group(1), m.group(2)
        plain = re.sub(r'<[^>]+>', '', inner)   # strip any nested HTML tags
        base = _slugify(plain)
        if base in seen:
            seen[base] += 1
            slug = f'{base}-{seen[base]}'
        else:
            seen[base] = 0
            slug = base
        return f'<h{lvl} id="{slug}">{inner}</h{lvl}>'

    return re.sub(r'<(h[1-6])>(.*?)</\1>', repl, html, flags=re.DOTALL)


def _fix_md_links(html: str) -> str:
    """Rewrite href="foo.md" and href="foo.md#anchor" to in-document anchors.

    foo.md          → #foo   (chapter anchor inserted by main())
    foo.md#section  → #section  (heading id inserted by _add_heading_ids())
    """
    def repl(m: re.Match) -> str:
        href = m.group(1)
        md_match = re.match(r'([^#"]+\.md)(#[^"]*)?', href, re.IGNORECASE)
        if not md_match:
            return m.group(0)
        stem = Path(md_match.group(1)).stem
        fragment = md_match.group(2)
        target = fragment if fragment else f'#{stem}'
        return f'href="{target}"'

    return re.sub(r'href="([^"]+\.md[^"]*)"', repl, html, flags=re.IGNORECASE)


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
    all_headings: list[tuple[int, str]] = []
    seen_slugs: dict[str, int] = {}   # cross-chapter duplicate tracker for heading ids

    for i, name in enumerate(CHAPTERS):
        path = ROOT / name
        if not path.exists():
            print(f"  SKIP (not found): {name}")
            continue
        print(f"  {name}")
        text = path.read_text(encoding="utf-8")
        if re.match(r'^\d+_', name):
            max_level = 2
        else:
            max_level = 1
        all_headings.extend(_extract_headings(text, max_level))
        html = _md_to_html(text)
        html = _fix_img_paths(html)
        html = _add_heading_ids(html, seen_slugs)
        # Chapter-level anchor so href="foo.md" links resolve to the chapter top.
        chapter_anchor = f'<a id="{Path(name).stem}"></a>\n'
        sep = "" if i == 0 else '<div class="chapter-sep"></div>\n'
        parts.append(sep + chapter_anchor + html)

    body = _fix_md_links("\n".join(parts))
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
        _add_pdf_bookmarks(OUTPUT_PDF, all_headings)
    else:
        print("PDF generation may have failed.")


if __name__ == "__main__":
    main()
