# TODO

Outstanding items across the guide, organized by chapter.

---

## Chapter 1 — IFC Alignment Concepts

1. ~~Revisit language that describes IFC4x3 as "new." ISO 16739-1:2024 has been published; IFC4x3 is the current standard, not an emerging one. Reframe: adoption is lagging not because the standard is new but because implementation guidance has been scarce — which is the gap this guide addresses.~~

## Chapter 3 — Vertical Alignments

2. ~~Test VS to see if it catches a discrepancy between `IfcGradientCurve.EndPoint` and the zero-length closing segment.~~
3. ~~Check IfcOpenShell implementation to see if `IfcGradientCurve.EndPoint` is populated.~~

## Chapter 4 — Cant Alignments

4. ~~Test VS to see if it catches a discrepancy between `IfcSegmentedReferenceCurve.EndPoint` and the zero-length closing segment.~~
5. ~~Check IfcOpenShell implementation to see if `IfcSegmentedReferenceCurve.EndPoint` is populated.~~
6. ~~Review the overall organization of Chapter 4.~~

## Chapter 10 — Sectioned Surfaces and Solids

7. Create sample models for `IfcSectionedSolidHorizontal` showing the various cross-section transitions supported. (§10.0)
8. Validate section claims with models; this section currently contains assertions that need model-backed evidence. (§10.0)
9. ~~Clarify tag uniqueness for stringlines: when all guide curves share the same `BasisCurve` as the surface `Directrix`, tags are surface-unique; when guide curves use different basis curves, tags must be globally unique. This distinction is not clear in the IFC specification. (§10.0)~~
10. ~~Clarify which profile type uses `IfcCartesianPointList2D` — does this apply to polylines? (§10.2)~~
11. ~~The last sentence of §10.2 ("In the limiting case with infinitely dense sections...") appears redundant — review and remove or consolidate. (§10.2)~~
12. ~~§10.3.2 content appears redundant with §10.2 — review for overlap and consolidate. (§10.3.2)~~
13. ~~Review the claim in §10.3.2 that a guide curve's `BasisCurve` must equal the surface `Directrix` — flagged as potentially incorrect. (§10.3.2)~~
14. ~~Add reference in §10.4 to the discussion of the error in the IFC specification figure. (§10.4)~~
15. Back up the multiple independent superelevations discussion in §10.4.1 with examples. (§10.4.1)
17. Discuss the practical implications of the default `Axis` direction in `IfcAxis2PlacementLinear` for `IfcSectionedSurface` and `IfcSectionedSolidHorizontal`. Early IFC 4.3 development assumed `Axis = (0,0,1)` (always vertical); this was replaced through RC1–RC4/ADD1 revisions with an author-controlled `IfcAxis2PlacementLinear`. Different surfaces and solids result depending on the assumed default. Topic introduced in §8.3.2; see [IFC4.x-IF #125](https://github.com/buildingSMART/IFC4.x-IF/issues/125), [IFC4.x-development #732](https://github.com/buildingSMART/IFC4.x-development/issues/732), and [IFC4.x-development #731](https://github.com/buildingSMART/IFC4.x-development/issues/731). Support with two figures: one showing the result with `Axis = (0,0,1)` and one with `Axis` normal to the slope of the `Directrix`.

## Chapter 12 — Alignment Geometry Testset

16. ~~Create a linear placement testset: a model with a linear placement whose correct results (x, y, z + RefDir + Y + Axis) are known, to serve as a reference for verifying implementations.~~
