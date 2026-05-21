# TODO

Outstanding items across the guide, organized by chapter.

---

## Chapter 1 — IFC Alignment Concepts

- [ ] Revisit language that describes IFC4x3 as "new." ISO 16739-1:2024 has been published; IFC4x3 is the current standard, not an emerging one. Reframe: adoption is lagging not because the standard is new but because implementation guidance has been scarce — which is the gap this guide addresses.

## Chapter 3 — Vertical Alignments

- [ ] Test VS to see if it catches a discrepancy between `IfcGradientCurve.EndPoint` and the zero-length closing segment.
- [ ] Check IfcOpenShell implementation to see if `IfcGradientCurve.EndPoint` is populated.

## Chapter 4 — Cant Alignments

- [ ] Test VS to see if it catches a discrepancy between `IfcSegmentedReferenceCurve.EndPoint` and the zero-length closing segment.
- [ ] Check IfcOpenShell implementation to see if `IfcSegmentedReferenceCurve.EndPoint` is populated.
- [ ] Review the overall organization of Chapter 4.

## Chapter 10 — Sectioned Surfaces and Solids

- [ ] Create sample models for `IfcSectionedSolidHorizontal` showing the various cross-section transitions supported. (§10.0)
- [ ] Add `IfcReferent` widening event markers to `IfcSectionedSurface_with_branching.ifc` (§10.6.2), similar to the superelevation event referents in `Superelevation.ifc`. (§10.0)
- [ ] Validate section claims with models; this section currently contains assertions that need model-backed evidence. (§10.0)
- [ ] Clarify tag uniqueness for stringlines: when all guide curves share the same `BasisCurve` as the surface `Directrix`, tags are surface-unique; when guide curves use different basis curves, tags must be globally unique. This distinction is not clear in the IFC specification. (§10.0)
- [ ] Clarify which profile type uses `IfcCartesianPointList2D` — does this apply to polylines? (§10.2)
- [ ] The last sentence of §10.2 ("In the limiting case with infinitely dense sections...") appears redundant — review and remove or consolidate. (§10.2)
- [ ] §10.3.2 content appears redundant with §10.2 — review for overlap and consolidate. (§10.3.2)
- [ ] Review the claim in §10.3.2 that a guide curve's `BasisCurve` must equal the surface `Directrix` — flagged as potentially incorrect. (§10.3.2)
- [ ] Add reference in §10.4 to the discussion of the error in the IFC specification figure. (§10.4)
- [ ] Back up the multiple independent superelevations discussion in §10.4.1 with examples. (§10.4.1)

## Chapter 12 — Alignment Geometry Testset

- [ ] Create a linear placement testset: a model with a linear placement whose correct results (x, y, z + RefDir + Y + Axis) are known, to serve as a reference for verifying implementations.
