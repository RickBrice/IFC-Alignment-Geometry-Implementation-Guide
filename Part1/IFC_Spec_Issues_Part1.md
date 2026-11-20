# IFC Specification Issues — Part 1

*IFC Alignment Geometry Implementation Guide, Part 1 — Fundamentals: Alignment Curve Geometry*

This summary lists gaps, ambiguities, and errors in the IFC4x3 specification identified while preparing Chapters 1–5 and Appendix A of this guide. Each item cites the section of the guide where it is discussed. Items are numbered independently in each part of the guide.

---

## Chapter 1 — IFC Alignment Concepts

1. The order of layout sub-objects (Horizontal, Vertical, Cant) within a nest is not explicitly stated; it must be inferred from diagrams in the `IfcAlignment` documentation (§1.4).

2. The ordering of `IfcAlignmentSegment` instances within each layout's nest is not specified by the schema (§1.4).

3. No guidance is given on the proper `RepresentationIdentifier` or `RepresentationType` for `IfcPolyline` and `IfcOffsetCurveByDistances` alignment representations (§1.5.1).

4. No guidance is provided on how to define complete 3D geometry in regions of the horizontal alignment that do not overlap with the vertical or cant curves (§1.5.2.2).

---

## Chapter 2 — Horizontal Alignments

5. `IfcAlignmentHorizontalSegment` implies the cubic formula coefficient must carry units of Length⁻², directly contradicting `IfcPolynomialCurve`, which declares all coefficients as dimensionless `IfcReal` scalars (§2.6.2).

---

## Chapter 3 — Vertical Alignments

6. The geometric mapping for `IfcClothoid` in a vertical context is undocumented; the only available reference implementation produces degenerate zero-length results and cannot serve as a reference (§3.5).

7. `IfcGradientCurve.EndPoint` is optional and its consistency with the required zero-length closing segment is not enforced by the schema; a discrepancy between the two is a data error with no schema-level detection (§3.8).

8. `IfcAlignmentVerticalSegment.RadiusOfCurvature` is optional and may be absent or inconsistent with the required attributes; the spec does not mandate that it be derivable from them (§3.9).

---

## Chapter 4 — Cant Alignments

9. The cant transition type should match the horizontal transition type and segment length, but IFC does not enforce this constraint (§4.1.3).

10. The frame of a cant `IfcCurveSegment` in an `IfcSegmentedReferenceCurve` is not defined where the deviating elevation varies. `IfcSegmentedReferenceCurve` says only that, with no deviation, the `Axis` and `RefDirection` directions are interpolated between consecutive placements. It does not say how the slope of the deviating elevation orients the frame, and the cant placement mixes two coordinate conventions: `Location` and `RefDirection` are in the (distance along, deviating elevation) plane, while `Axis` is in the cross section with $y$ to the left and $z$ up. The guide pitches the cross section by the slope of the deviating elevation and rolls it by the cross slope, so that `RefDirection` is the tangent of the 3D curve and `Axis` is exactly perpendicular to the railheads. This follows `IfcAxis2PlacementLinear`, whose `Axis` is exact and whose `RefDirection` defaults to the curve tangent (§4.2).

11. The EnrichIfc4x3 reference implementation contains compensating errors in cant coefficient mapping that produce correct deviating elevation values; mixing that mapping with independently derived equations produces results off by a factor of L (§4.11).
