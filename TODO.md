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

7. ~~Create sample models for `IfcSectionedSolidHorizontal` showing the various cross-section transitions supported. (§10.0)~~ *(minimal definition complete as §10.6.7; remaining cases tracked as items 18–21)*
8. Validate section claims with models; this section currently contains assertions that need model-backed evidence. (§10.0)
9. ~~Clarify tag uniqueness for stringlines: when all guide curves share the same `BasisCurve` as the surface `Directrix`, tags are surface-unique; when guide curves use different basis curves, tags must be globally unique. This distinction is not clear in the IFC specification. (§10.0)~~
10. ~~Clarify which profile type uses `IfcCartesianPointList2D` — does this apply to polylines? (§10.2)~~
11. ~~The last sentence of §10.2 ("In the limiting case with infinitely dense sections...") appears redundant — review and remove or consolidate. (§10.2)~~
12. ~~§10.3.2 content appears redundant with §10.2 — review for overlap and consolidate. (§10.3.2)~~
13. ~~Review the claim in §10.3.2 that a guide curve's `BasisCurve` must equal the surface `Directrix` — flagged as potentially incorrect. (§10.3.2)~~
14. ~~Add reference in §10.4 to the discussion of the error in the IFC specification figure. (§10.4)~~
15. Back up the multiple independent superelevations discussion in §10.4.1 with examples. (§10.4.1) *(will be addressed by item 19)*
17. Author two figures for §10.5 "Cross-Section Orientation: Default Axis Direction" and replace the placeholder markers: one with `Axis = (0,0,1)`, one with `Axis` perpendicular to the 3D tangent. Requires the Jupyter notebook from the IfcAlignmentDrive machine.
18. Author example model and build script for §10.6.9 — `IfcSectionedSolidHorizontal` with single superelevation via `IfcDerivedProfileDef`.
19. Author example model and build script for §10.6.10 — `IfcSectionedSolidHorizontal` with multiple independent superelevations using tagged points and guide curves.
20. Author example model and build script for §10.6.11 — `IfcSectionedSolidHorizontal` with stringlines whose `BasisCurve` matches the solid `Directrix`.
21. Author example model and build script for §10.6.12 — `IfcSectionedSolidHorizontal` with stringlines using an independent `BasisCurve`.
23. Author example model and build script for `IfcSectionedSurface` using an `IfcSegmentedReferenceCurve` as the `Directrix`, so the cross-section profile rotates with cant. Verify that IfcOpenShell correctly banks the surface sections.
24. Figure 10.5-2 - this figure represents default Axis. add another figure of same model where different assumption about default Axis was made. 

## IfcOpenShell Implementation Issues

22. Fix IfcOpenShell `IfcSectionedSolidHorizontal` implementation: cross-section is not rotated based on cant from `IfcSegmentedReferenceCurve`. The minimal example (§10.6.7) uses a Bloss cant transition but the rendered solid shows no banking — the profile remains unrotated regardless of the cant value.

## Chapter 12 — Alignment Geometry Testset

16. ~~Create a linear placement testset: a model with a linear placement whose correct results (x, y, z + RefDir + Y + Axis) are known, to serve as a reference for verifying implementations.~~
