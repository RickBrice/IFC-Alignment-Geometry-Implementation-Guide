---
name: project-make-docx
description: make_docx.py build script that converts markdown chapters to a Word docx via Pandoc with python-docx post-processing for page numbers and image sizing
metadata:
  type: project
---

`make_docx.py` builds `IFC_Alignment_Geometry_Implementation_Guide.docx` by:

1. Reading all chapter markdown files listed in `CHAPTERS`
2. Converting SVG images to PNG via Inkscape (`convert_svgs`)
3. Preprocessing markdown text per chapter (TOC field injection, front/back matter heading styles, cover image sizing, Figure 12.2.5-1 size attribute)
4. Running Pandoc with `--from markdown+tex_math_dollars+raw_html-implicit_figures`
5. Post-processing the docx with python-docx: `add_page_numbers` (Roman numerals for front matter, Arabic from Chapter 1) and `resize_tall_images` (sets images taller than 8.5" to 6.5"×8")

**Why:** Pandoc image attributes (`{width=...}`) are unreliable for docx output when `implicit_figures` is disabled; python-docx post-processing is used as the reliable fix. See [[feedback-pandoc-image-sizing]].
