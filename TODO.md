# TODO

Outstanding items across the guide, organized by chapter.

---

1. ~~Update the index~~ Done. Fixed chapter 5 section number shifts, added §10.6 example models entries, corrected chapter 12 section references, added new entries (default Axis direction, retaining wall, specification gaps).
2. ~~Are the restructure.py and remove_sections.py scripts are needed. If so, document them and move them to a scripts folder under the main folder, otherwise delete them.~~ Both were one-time restructuring helpers with stale filenames; deleted.
3. ~~Spell and grammar check the entire document. Did I use forward where I should have used foreword?~~ Done. Fixed 9 typos across chapters 2–5; "forward" vs "foreword" usage is correct throughout.
4. Should this document contain a list of figures? — *Handled by #7; Word auto-generates a Table of Figures from figure captions.*
5. Should this document contain a list of tables? — *Handled by #7; Word auto-generates a Table of Tables from table captions.*
6. ~~Update `make_pdf.py` to add sequential arabic page numbering.~~ Done. `make_pdf.py` is retained as a quick HTML/PDF preview tool. Canonical PDF publication uses the `make_docx.py` → Word pipeline (#7), which handles page numbers, TOC, and list of figures natively.
7. ~~Create a `make_docx.py` script using Pandoc to convert all chapters into a single `.docx`.~~ Done. Script written. Requires Pandoc to be installed (https://pandoc.org/installing.html). First run generates a `reference.docx` style template to customize in Word; subsequent runs produce the final `IFC_Alignment_Guide.docx`. Math converts to OMML automatically — validate rendering quality on first run.
8. ~~Suggest where I might add a notice that some content in this document was created with the assistance of AI. Also suggest what that notice would say.~~ Done. Added a paragraph at the end of the Foreword (before the signature).
9. Fix IfcOpenShell `IfcSectionedSolidHorizontal` implementation: cross-section is not rotated based on cant from `IfcSegmentedReferenceCurve`. The minimal example (§10.6.2.1) uses a Bloss cant transition but the rendered solid shows no banking — the profile remains unrotated regardless of the cant value.
