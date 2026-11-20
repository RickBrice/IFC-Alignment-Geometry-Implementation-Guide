#!/usr/bin/env python3
"""Build the Word .docx edition of one or both parts of the guide using Pandoc.

Usage:
    python common/tools/make_docx.py            # build Part 1 and Part 2
    python common/tools/make_docx.py --part 1   # build Part 1 only
    python common/tools/make_docx.py --part 2   # build Part 2 only

Each part is a separate publication. Its output is written to its own folder:
    Part1/IFC_Alignment_Geometry_Implementation_Guide_Part1.docx
    Part2/IFC_Alignment_Geometry_Implementation_Guide_Part2.docx

Styling comes from common/tools/reference.docx, which is generated from
Pandoc's default template by style_reference_docx.py (buildingSMART-style
fonts, colours, tables and A4 page size). If reference.docx is missing, this
script extracts Pandoc's default and asks you to run the styler.

The buildingSMART International and buildingSMART USA logos in
common/branding/ are placed side by side at the top of the cover, scaled to
the same height (see common/branding/README.md). A missing logo file is
skipped.

After opening the output in Word:
    1. Accept the prompt to update fields — the TOC populates automatically.
    2. Inspect math equations — Pandoc converts LaTeX to OMML (Word equations).
       Complex expressions may need manual correction.
    3. Export to PDF: File > Export > Create PDF/XPS.

Requirements:
    pandoc       — https://pandoc.org/installing.html
    inkscape     — https://inkscape.org  (for SVG → PNG conversion)
    python-docx  — pip install python-docx
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Mm, Pt, RGBColor
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False

TOOLS = Path(__file__).resolve().parent
COMMON = TOOLS.parent
ROOT = COMMON.parent
REFERENCE_DOCX = TOOLS / "reference.docx"
# Cover logos, left to right. Each is drawn LOGO_HEIGHT_IN tall.
LOGOS = [
    (COMMON / "branding" / "bsi_logo.png", "buildingSMART International"),
    (COMMON / "branding" / "bsusa_logo.png", "buildingSMART USA"),
]
LOGO_HEIGHT_IN = 0.45

INKSCAPE = Path("C:/Program Files/Inkscape/bin/inkscape.exe")

GUIDE_TITLE = "IFC Alignment Geometry Implementation Guide"
ORGANIZATION = "buildingSMART USA"
EDITORS = ["Richard Brice, PE", "Scott Lecher, PE"]
TEAL = "00A0AF"


@dataclass
class Part:
    number: int
    title: str
    folder: Path
    files: list[str]          # paths relative to the part folder
    first_chapter: str        # file that starts Arabic page numbering

    @property
    def output(self) -> Path:
        return self.folder / f"IFC_Alignment_Geometry_Implementation_Guide_Part{self.number}.docx"

    @property
    def full_title(self) -> str:
        return f"{GUIDE_TITLE} — Part {self.number}: {self.title}"


PARTS = {
    1: Part(
        1, "Fundamentals — Alignment Curve Geometry", ROOT / "Part1",
        [
            "Cover.md",
            "../common/Notices.md",
            "DocumentControl.md",
            "ExecutiveSummary.md",
            "TableOfContents.md",
            "Notation.md",
            "1_IFC_Alignment_Concepts.md",
            "2_Horizontal_Alignments.md",
            "3_Vertical_Alignments.md",
            "4_Cant_Alignments.md",
            "5_Alignment_Geometry_Testset.md",
            "Appendix_A_LandXML.md",
            "../common/References.md",
            "IFC_Spec_Issues_Part1.md",
            "Index.md",
        ],
        "1_IFC_Alignment_Concepts.md",
    ),
    2: Part(
        2, "Advanced Topics — Placement, Referencing, and Derived Geometry", ROOT / "Part2",
        [
            "Cover.md",
            "../common/Notices.md",
            "DocumentControl.md",
            "ExecutiveSummary.md",
            "TableOfContents.md",
            "6_OffsetCurves.md",
            "7_Approximate_Alignment_Geometry.md",
            "8_Alignments_Reusing_Horizontal_Layout.md",
            "9_LinearPlacement.md",
            "10_Referents_and_Stationing.md",
            "11_Sectioned_Surfaces_and_Solids.md",
            "12_Precision_and_Tolerance.md",
            "../common/References.md",
            "IFC_Spec_Issues_Part2.md",
            "Index.md",
        ],
        "6_OffsetCurves.md",
    ),
}

# Front matter: unnumbered pages before the first chapter, Roman page numbers,
# excluded from the TOC. Back matter: after the chapters, listed in the TOC.
FRONTMATTER = {"Notices.md", "DocumentControl.md", "ExecutiveSummary.md", "Notation.md"}
BACKMATTER = {"References.md", "IFC_Spec_Issues_Part1.md", "IFC_Spec_Issues_Part2.md", "Index.md"}

# Raw OpenXML TOC field injected in place of TableOfContents.md's static list.
# Word updates it on first open (w:dirty="true"). Chapter headings are Heading 1;
# back matter uses "Backmatter Heading", which the \t switch also collects.
_TOC_FIELD = (
    '\n\n```{=openxml}\n'
    '<w:p>'
    '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> TOC \\t "Heading 1,1,Backmatter Heading,1" \\h \\z </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    '</w:p>\n'
    '```\n'
)

# Section break injected before the first chapter. It ends the front matter
# section (cover through notation) with lowercase Roman page numbers; the
# document-level sectPr (configured in add_headers_footers) governs the chapters,
# with Arabic numbering restarting at 1.
_FRONT_MATTER_SECTION_BREAK = (
    '\n\n```{=openxml}\n'
    '<w:p><w:pPr><w:sectPr>'
    '<w:type w:val="nextPage"/>'
    '<w:pgSz w:w="11906" w:h="16838"/>'
    '<w:pgMar w:top="1417" w:right="1417" w:bottom="1247" w:left="1417" '
    'w:header="680" w:footer="567" w:gutter="0"/>'
    '<w:pgNumType w:fmt="lowerRoman" w:start="0"/>'
    '<w:titlePg/>'
    '</w:sectPr></w:pPr></w:p>\n'
    '```\n\n'
)

_PAGE_BREAK = '\n\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n\n'


def get_build_date() -> str:
    """Today's date in "D Mon YYYY" form, used on the cover, footer and metadata."""
    today = date.today()
    return f"{today.day} {today.strftime('%b %Y')}"


def check_pandoc() -> str:
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()[0]
    except FileNotFoundError:
        print("ERROR: pandoc not found on PATH.")
        print("Install from: https://pandoc.org/installing.html")
        sys.exit(1)


def generate_reference_docx() -> None:
    """Extract Pandoc's built-in reference.docx as a starting point."""
    with open(REFERENCE_DOCX, "wb") as f:
        subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], stdout=f, check=True)
    print(f"Generated default reference template: {REFERENCE_DOCX}")
    print("Run  python common/tools/style_reference_docx.py  to apply the guide's styling,")
    print("then re-run this script.")


def convert_svgs(texts: list[str], base_dirs: list[Path], png_dir: Path) -> list[str]:
    """Convert every SVG image reference to PNG (Pandoc cannot embed SVG in docx).

    Each text's relative image paths resolve against its own base directory.
    Converted references are rewritten to absolute PNG paths in png_dir.
    """
    if not INKSCAPE.exists():
        print(f"  WARNING: Inkscape not found at {INKSCAPE} — SVG images will be skipped.")
        return texts

    svg_pattern = re.compile(r'(!\[([^\]]*)\]\()([^)]+\.svg)(\))', re.IGNORECASE)
    converted: dict[Path, str] = {}
    n_ok = n_skip = 0

    def _convert(svg_abs: Path, original: str) -> str:
        nonlocal n_ok, n_skip
        if svg_abs in converted:
            return converted[svg_abs]
        if not svg_abs.exists():
            print(f"    SKIP (not found): {original}")
            converted[svg_abs] = original
            n_skip += 1
            return original
        png_abs = png_dir / (svg_abs.stem + ".png")
        if not png_abs.exists():
            result = subprocess.run(
                [str(INKSCAPE), f"--export-filename={png_abs}", str(svg_abs)],
                capture_output=True, text=True,
            )
            if result.returncode != 0 or not png_abs.exists():
                print(f"    WARN: Inkscape failed on {original}")
                converted[svg_abs] = original
                n_skip += 1
                return original
        converted[svg_abs] = png_abs.as_posix()
        n_ok += 1
        return converted[svg_abs]

    updated = []
    for text, base in zip(texts, base_dirs):
        updated.append(svg_pattern.sub(
            lambda m: m.group(1) + _convert((base / m.group(3)).resolve(), m.group(3)) + m.group(4),
            text,
        ))
    print(f"  SVG->PNG: {n_ok} converted, {n_skip} skipped")
    return updated


def absolutize_images(text: str, base: Path) -> str:
    """Rewrite relative image paths to absolute ones.

    Files from common/ sit in a different folder from the part's chapters, so
    a single Pandoc --resource-path cannot resolve every relative path.
    """
    def _repl(m: re.Match) -> str:
        target = m.group(3)
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or Path(target).is_absolute():
            return m.group(0)
        return m.group(1) + (base / target).resolve().as_posix() + m.group(4)
    return re.sub(r'(!\[([^\]]*)\]\()([^)\s]+)(\))', _repl, text)


def styled(style: str, text: str) -> str:
    return f':::{{custom-style="{style}"}}\n{text}\n:::'


def demote_subheadings(text: str) -> str:
    """Turn ##/### headings into bold paragraphs so Word does not number them,
    collect them into the TOC, or export them as PDF bookmarks."""
    text = re.sub(r'^## (.+)$', lambda m: f'**{m.group(1)}**', text, flags=re.MULTILINE)
    return re.sub(r'^### (.+)$', lambda m: f'***{m.group(1)}***', text, flags=re.MULTILINE)


def cover_field(text: str, name: str) -> str | None:
    """Value of a "Name: value" line in Cover.md (e.g. Version, Status)."""
    m = re.search(rf'^{name}:\s*(.+)$', text, re.MULTILINE)
    return m.group(1).strip() if m else None


def build_cover(text: str, part: Part, revision_date: str) -> str:
    """bSI-style cover: logos, document-control strip, title block, and origin."""
    out = []
    logos = [f"![{alt}]({path.as_posix()})" for path, alt in LOGOS if path.exists()]
    if logos:
        out.append(styled("Cover Text", "   ".join(logos)))

    status = cover_field(text, "Status") or "Draft"
    version = cover_field(text, "Version") or "—"
    out.append(
        "| Title | Organization | Editors | Version | Date | Status |\n"
        "|-------|--------------|---------|---------|------|--------|\n"
        f"| {GUIDE_TITLE}, Part {part.number} | {ORGANIZATION} | {"; ".join(EDITORS)} "
        f"| {version} | {revision_date} | {status} |"
    )
    out.append(styled("Cover Text", "\u00a0\n\n\u00a0\n\n\u00a0"))

    for block in re.split(r'\n\s*\n', text.strip()):
        block = block.strip()
        if block.startswith("# "):
            out.append(styled("Title", block[2:]))
        elif block.startswith("## "):
            out.append(styled("Subtitle", block[3:]))
        elif block.startswith("Status:"):
            out.append(styled("Cover Text", f"Revision: {revision_date}"))
            out.append(styled("Cover Text", block))
        elif block.startswith("Developed by"):
            out.append(styled("Cover Text", "\u00a0\n\n\u00a0"))
            out.append(styled("Cover Text", f"**{block}**"))
        else:
            out.append(styled("Cover Text", block))
    return "\n\n".join(out) + "\n"


def preprocess(path: Path, text: str, part: Part, revision_date: str) -> str:
    name = path.name
    if name == "Cover.md":
        return build_cover(text, part, revision_date)
    if name == "TableOfContents.md":
        m = re.match(r'^# (.+)$', text, re.MULTILINE)
        print("  Injected live TOC field")
        return styled("Frontmatter Heading", m.group(1) if m else "Table of Contents") + _TOC_FIELD
    if name in FRONTMATTER:
        text = text.replace("(build date)", revision_date)
        text = re.sub(r'^# (.+)$', lambda m: styled("Frontmatter Heading", m.group(1)), text, flags=re.MULTILINE)
        return demote_subheadings(text)
    if name in BACKMATTER:
        text = re.sub(r'^# (.+)$', lambda m: styled("Backmatter Heading", m.group(1)), text, flags=re.MULTILINE)
        # The index keeps its letter headings; other back matter is demoted.
        return text if name == "Index.md" else demote_subheadings(text)
    if name == "5_Alignment_Geometry_Testset.md":
        text = re.sub(
            r'(!\[[^\]]*\]\([^)]*Cant_HelmertCurve_100\.0_300_1000_Meter[^)]*\))(?!\{)',
            r'\1{width=6.3in height=8in}',
            text,
        )
    return text


def set_document_metadata(docx_path: Path, title: str, subject: str) -> None:
    """Set docx core properties. (Pandoc's --metadata title would also render a
    visible title paragraph, duplicating the cover.)"""
    doc = Document(str(docx_path))
    doc.core_properties.title = title
    doc.core_properties.subject = subject
    doc.core_properties.author = "; ".join(EDITORS)
    doc.core_properties.category = f"Developed by the {ORGANIZATION} chapter of buildingSMART International"
    doc.save(str(docx_path))
    print("  Set docx metadata")


def _border(para, edge: str, color: str = TEAL, size: int = 6) -> None:
    ppr = para._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    b = OxmlElement(f"w:{edge}")
    b.set(qn("w:val"), "single")
    b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "4")
    b.set(qn("w:color"), color)
    pbdr.append(b)
    ppr.append(pbdr)


def _field(run, instr: str) -> None:
    for fld_type, text in (("begin", None), (None, instr), ("end", None)):
        if fld_type:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), fld_type)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def add_headers_footers(docx_path: Path, part: Part, revision_date: str) -> None:
    """bSI-style running header and footer, A4 page setup, and page numbering.

    Header: guide title and part (left), organization (right), teal rule below.
    Footer: revision date (left), page number (right), teal rule above.
    The cover (first page of the first section) has neither.
    Front matter: lowercase Roman numerals. Chapters: Arabic, restarting at 1.
    """
    doc = Document(str(docx_path))
    sections = list(doc.sections)

    for idx, section in enumerate(sections):
        section.page_width, section.page_height = Mm(210), Mm(297)
        section.left_margin = section.right_margin = Mm(25)
        section.top_margin, section.bottom_margin = Mm(25), Mm(22)
        section.header_distance, section.footer_distance = Mm(12), Mm(10)
        section.different_first_page_header_footer = (idx == 0)
        usable = section.page_width - section.left_margin - section.right_margin

        header = section.header
        header.is_linked_to_previous = False
        for p in header.paragraphs:
            p.clear()
        hp = header.paragraphs[0]
        hp.paragraph_format.tab_stops.add_tab_stop(usable, WD_TAB_ALIGNMENT.RIGHT)
        r = hp.add_run(f"{GUIDE_TITLE} — Part {part.number}")
        r.font.size = Pt(8.5)
        hp.add_run().add_tab()
        r = hp.add_run(ORGANIZATION)
        r.font.size, r.font.bold = Pt(8.5), True
        r.font.color.rgb = RGBColor.from_string(TEAL)
        _border(hp, "bottom")

        footer = section.footer
        footer.is_linked_to_previous = False
        for p in footer.paragraphs:
            p.clear()
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fp.paragraph_format.tab_stops.add_tab_stop(usable, WD_TAB_ALIGNMENT.RIGHT)
        version = cover_field((part.folder / "Cover.md").read_text(encoding="utf-8-sig"), "Version")
        r = fp.add_run(f"Version {version}  ·  {revision_date}" if version else f"Revision {revision_date}")
        r.font.size = Pt(8.5)
        fp.add_run().add_tab()
        r = fp.add_run("Page ")
        r.font.size = Pt(8.5)
        r = fp.add_run()
        r.font.size = Pt(8.5)
        _field(r, " PAGE ")
        _border(fp, "top")

    last = sections[-1]._sectPr
    for existing in last.findall(qn("w:pgNumType")):
        last.remove(existing)
    pg = OxmlElement("w:pgNumType")
    pg.set(qn("w:fmt"), "decimal")
    pg.set(qn("w:start"), "1")
    last.append(pg)

    doc.save(str(docx_path))
    print(f"  Headers/footers added ({len(sections)} sections)")


def size_cover_logos(docx_path: Path) -> None:
    """Draw every cover logo at the same height, keeping each one's aspect ratio.

    The logos are the first inline images in the document (the cover comes first).
    """
    n = sum(1 for path, _ in LOGOS if path.exists())
    if not n:
        return
    doc = Document(str(docx_path))
    height = int(LOGO_HEIGHT_IN * 914400)
    for shape in list(doc.inline_shapes)[:n]:
        shape.width = int(shape.width * height / shape.height)
        shape.height = height
    doc.save(str(docx_path))
    print(f"  Sized {n} cover logo(s) to {LOGO_HEIGHT_IN} in tall")


def resize_tall_images(docx_path: Path, target_width_in: float, target_height_in: float,
                       threshold_in: float = 8.5) -> None:
    """Scale images taller than threshold_in to target size (EMU, 914400/in).
    Pandoc's {width=} attributes are unreliable for docx when implicit_figures
    is disabled, so sizing is applied here instead."""
    doc = Document(str(docx_path))
    threshold = int(threshold_in * 914400)
    resized = 0
    for shape in doc.inline_shapes:
        if shape.height is not None and shape.height > threshold:
            shape.width = int(target_width_in * 914400)
            shape.height = int(target_height_in * 914400)
            resized += 1
    if resized:
        doc.save(str(docx_path))
    print(f"  Resized {resized} oversized image(s)")


def build(part: Part, revision_date: str) -> None:
    print(f"\n=== Part {part.number}: {part.title}")
    paths = [(part.folder / f).resolve() for f in part.files]
    missing = [p for p in paths if not p.exists()]
    for p in missing:
        print(f"  WARNING: not found, skipping — {p}")
    paths = [p for p in paths if p.exists()]

    tmp = Path(tempfile.mkdtemp(prefix=f"make_docx_part{part.number}_"))
    try:
        texts = [p.read_text(encoding="utf-8-sig") for p in paths]
        print("Converting SVG images to PNG...")
        texts = convert_svgs(texts, [p.parent for p in paths], tmp)
        texts = [preprocess(p, absolutize_images(t, p.parent), part, revision_date)
                 for p, t in zip(paths, texts)]

        tmp_files = []
        for i, (path, text) in enumerate(zip(paths, texts)):
            if i == 0:
                content = text
            elif path.name == part.first_chapter:
                content = _FRONT_MATTER_SECTION_BREAK + text
            else:
                content = _PAGE_BREAK + text
            tmp_md = tmp / f"{i:02d}_{path.name}"
            tmp_md.write_text(content, encoding="utf-8")
            tmp_files.append(str(tmp_md))

        cmd = [
            "pandoc", *tmp_files,
            "--from", "markdown+tex_math_dollars+raw_html-implicit_figures",
            "--to", "docx",
            f"--reference-doc={REFERENCE_DOCX}",
            f"--resource-path={part.folder}",
            "--standalone",
            "--output", str(part.output),
        ]
        print(f"Running Pandoc on {len(tmp_files)} files...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(part.folder))
        if result.returncode != 0:
            print("ERROR from Pandoc:")
            print(result.stderr)
            sys.exit(1)
        for line in result.stderr.splitlines():
            print(f"  {line}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if _DOCX_AVAILABLE:
        set_document_metadata(part.output, part.full_title, f"Revision: {revision_date}")
        add_headers_footers(part.output, part, revision_date)
        size_cover_logos(part.output)
        resize_tall_images(part.output, target_width_in=6.3, target_height_in=8.0)
    else:
        print("  SKIP post-processing: python-docx not installed (pip install python-docx)")

    print(f"Output: {part.output}  ({part.output.stat().st_size / 1_048_576:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--part", type=int, choices=sorted(PARTS), help="build only this part")
    args = parser.parse_args()

    print(f"Using {check_pandoc()}")
    if not REFERENCE_DOCX.exists():
        print("No reference.docx found — generating default template...")
        generate_reference_docx()
        return

    revision_date = get_build_date()
    print(f"Revision date (today): {revision_date}")
    for n in ([args.part] if args.part else sorted(PARTS)):
        build(PARTS[n], revision_date)

    print()
    print("In Word, before exporting to PDF:")
    print("  1. Accept the prompt to update fields — TOC populates automatically")
    print("  2. Check math equations for OMML conversion quality")
    print("  3. File > Export > Create PDF/XPS")


if __name__ == "__main__":
    main()
