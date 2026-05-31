---
name: feedback-pandoc-image-sizing
description: Pandoc image attribute syntax {width=Xin height=Yin} does not reliably size images in docx output; python-docx post-processing is the correct approach
metadata:
  type: feedback
---

Do not rely on Pandoc's `{width=Xin height=Yin}` markdown attribute syntax to control image dimensions in docx output.

**Why:** When `implicit_figures` is disabled in the Pandoc `--from` flag (as in this project's `make_docx.py`), Pandoc does not reliably honor image dimension attributes for docx output. Two attempts at this approach failed for Figure 12.2.5-1.

**How to apply:** Use python-docx post-processing instead. After Pandoc produces the docx, iterate over `doc.inline_shapes` and set `shape.width` / `shape.height` directly in EMU (1 inch = 914,400 EMU). The `resize_tall_images()` function in `make_docx.py` implements this pattern — it finds images exceeding a height threshold and sets them to exact target dimensions.
