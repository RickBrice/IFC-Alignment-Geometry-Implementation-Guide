# IFC Alignment Geometry Implementation Guide

An implementation guide for developers adding IFC4x3 alignment geometry support to infrastructure software applications, developed by the **buildingSMART USA** chapter of buildingSMART International. It provides the mathematical reference for every horizontal, vertical, and cant curve type defined in IFC4x3, together with guidance on placement, referencing, and alignment-based geometry.

The guide is published as two separate documents. Chapter, section, figure, and table numbers are continuous across both.

| Part | Title | Contents | Start here |
|------|-------|----------|------------|
| 1 | Fundamentals — Alignment Curve Geometry | Ch. 1–5, Appendix A | [Part 1 Table of Contents](Part1/TableOfContents.md) |
| 2 | Advanced Topics — Placement, Referencing, and Derived Geometry | Ch. 6–12 | [Part 2 Table of Contents](Part2/TableOfContents.md) |

## Repository layout

```
Part1/      Part 1 chapters, front/back matter, images/, figures/ (figure generators)
Part2/      Part 2 chapters, front/back matter, images/, examples/ (IFC example models)
FutureWork.md  Gaps in the guide's own coverage (topics to add or expand)
common/     Material shared by both parts
  References.md, Notices.md     back/front matter included in both builds
  testset/                      alignment geometry test set (Part 1, Chapter 5)
  BIM_Fit_Check_testset/        bS-Germany BIM Fit Check atomic test set
  tools/                        make_docx.py, style_reference_docx.py, reference.docx
  branding/                     bSI and bS-USA cover logos
  archive/                      old single-volume docx/pdf, Foreword, pre-split revision log
```

## Building the Word editions

```
python common/tools/make_docx.py            # both parts
python common/tools/make_docx.py --part 1   # one part
```

Requires Pandoc, Inkscape, and python-docx. The template styling is regenerated with `python common/tools/style_reference_docx.py`.

## License

Copyright © 2026 buildingSMART USA. The guide is licensed under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). Reuse requires credit to buildingSMART USA and buildingSMART International. See [LICENSE](LICENSE).
