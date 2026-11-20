#!/usr/bin/env python3
"""Apply buildingSMART-style formatting to the Pandoc reference template.

Usage:
    python common/tools/style_reference_docx.py

Rewrites common/tools/reference.docx in place. make_docx.py passes that file
to Pandoc as --reference-doc, so every style set here (fonts, colours, table
borders, page size) flows into both parts of the guide.

There is no official buildingSMART Word template. The styling follows the
published bSI implementation documents (ifcXML4 Specification Methodology,
ifcXML Implementation Guide, IFC Header Data Implementation Guide): A4 pages,
Cambria headings in bSI teal, Calibri body text, grid tables with a shaded
header row, and a teal rule under the cover title.

Requirements:
    python-docx
"""

from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

REFERENCE_DOCX = Path(__file__).resolve().parent / "reference.docx"

# Colours sampled from the bSI ifcXML4 Specification Methodology document.
TEAL = RGBColor(0x00, 0xA0, 0xAF)        # headings, title
TEAL_DARK = RGBColor(0x31, 0x84, 0x9B)   # subtitle, lower-level headings
BLUE = RGBColor(0x01, 0x47, 0x8C)        # hyperlinks
TEXT = RGBColor(0x26, 0x26, 0x26)
TABLE_HEADER_FILL = "DAEEF3"
TABLE_BORDER = "A6A6A6"

HEADING_FONT = "Cambria"
BODY_FONT = "Calibri"


def set_font(style, name=None, size=None, color=None, bold=None, italic=None):
    font = style.font
    if name:
        font.name = name
        rpr = style.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.insert(0, rfonts)
        # Clear theme-font attributes so the explicit font wins.
        for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            rfonts.attrib.pop(qn(attr), None)
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            rfonts.set(qn(attr), name)
    if size is not None:
        font.size = Pt(size)
    if color is not None:
        font.color.rgb = color
    if bold is not None:
        font.bold = bold
    if italic is not None:
        font.italic = italic


def set_spacing(style, before=None, after=None, keep_next=None):
    pf = style.paragraph_format
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if keep_next is not None:
        pf.keep_with_next = keep_next


def set_bottom_border(style, color_hex, size=12):
    ppr = style.element.get_or_add_pPr()
    for old in ppr.findall(qn("w:pBdr")):
        ppr.remove(old)
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), color_hex)
    pbdr.append(bottom)
    ppr.append(pbdr)


def clear_border(style):
    ppr = style.element.get_or_add_pPr()
    for old in ppr.findall(qn("w:pBdr")):
        ppr.remove(old)


def get_or_add_style(doc, name, base):
    try:
        return doc.styles[name]
    except KeyError:
        style = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = doc.styles[base]
        return style


def style_table(doc):
    """Grid borders on every cell and a shaded, bold header row."""
    tbl_style = doc.styles["Table"]
    el = tbl_style.element

    tblpr = el.find(qn("w:tblPr"))
    if tblpr is None:
        tblpr = OxmlElement("w:tblPr")
        el.append(tblpr)
    for old in tblpr.findall(qn("w:tblBorders")):
        tblpr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b = OxmlElement(f"w:{edge}")
        b.set(qn("w:val"), "single")
        b.set(qn("w:sz"), "4")
        b.set(qn("w:space"), "0")
        b.set(qn("w:color"), TABLE_BORDER)
        borders.append(b)
    tblpr.append(borders)
    for old in tblpr.findall(qn("w:tblCellMar")):
        tblpr.remove(old)
    mar = OxmlElement("w:tblCellMar")
    for edge, w in (("top", 29), ("left", 85), ("bottom", 29), ("right", 85)):
        m = OxmlElement(f"w:{edge}")
        m.set(qn("w:w"), str(w))
        m.set(qn("w:type"), "dxa")
        mar.append(m)
    tblpr.append(mar)

    for old in el.findall(qn("w:tblStylePr")):
        if old.get(qn("w:type")) == "firstRow":
            el.remove(old)
    first = OxmlElement("w:tblStylePr")
    first.set(qn("w:type"), "firstRow")
    rpr = OxmlElement("w:rPr")
    rpr.append(OxmlElement("w:b"))
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1F3B4D")
    rpr.append(color)
    first.append(rpr)
    tcpr = OxmlElement("w:tcPr")
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), TABLE_HEADER_FILL)
    tcpr.append(shd)
    first.append(tcpr)
    el.append(first)


def set_page(doc):
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.left_margin = section.right_margin = Mm(25)
        section.top_margin = Mm(25)
        section.bottom_margin = Mm(22)
        section.header_distance = Mm(12)
        section.footer_distance = Mm(10)


def main() -> None:
    doc = Document(str(REFERENCE_DOCX))
    s = doc.styles

    set_font(s["Normal"], BODY_FONT, 10.5, TEXT)
    for name in ("Body Text", "First Paragraph", "Compact"):
        set_spacing(s[name], before=3, after=6)

    sizes = {1: 18, 2: 14, 3: 12, 4: 11, 5: 10.5, 6: 10.5}
    for level, size in sizes.items():
        st = s[f"Heading {level}"]
        set_font(st, HEADING_FONT, size, TEAL if level <= 3 else TEAL_DARK, bold=level >= 2)
        set_spacing(st, before=18 if level == 1 else 12, after=6, keep_next=True)

    title = s["Title"]
    set_font(title, HEADING_FONT, 32, TEAL, bold=False)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_spacing(title, before=24, after=6)
    set_bottom_border(title, "00A0AF", size=12)

    subtitle = s["Subtitle"]
    set_font(subtitle, HEADING_FONT, 20, TEAL, italic=False)
    subtitle.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    clear_border(subtitle)
    set_spacing(subtitle, before=6, after=18)

    cover = s["Cover Text"]
    set_font(cover, BODY_FONT, 11, TEXT)
    cover.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_spacing(cover, before=2, after=6)

    for name in ("Frontmatter Heading", "Backmatter Heading"):
        st = get_or_add_style(doc, name, "Title")
        set_font(st, HEADING_FONT, 18, TEAL, bold=False)
        st.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        clear_border(st)
        set_spacing(st, before=0, after=12, keep_next=True)

    for name in ("Caption", "Table Caption", "Image Caption"):
        set_font(s[name], BODY_FONT, 9.5, TEAL_DARK, italic=True)

    set_font(s["Hyperlink"], color=BLUE)
    set_font(s["Verbatim Char"], "Consolas", 9.5)

    style_table(doc)
    set_page(doc)

    doc.save(str(REFERENCE_DOCX))
    print(f"Styled {REFERENCE_DOCX}")


if __name__ == "__main__":
    main()
