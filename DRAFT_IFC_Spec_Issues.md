# IFC Specification Gaps — Implementation Guide Findings

---

## Chapter 1 — IFC Alignment Concepts

1. The order of layout sub-objects (Horizontal, Vertical, Cant) within a nest is not explicitly stated; it must be inferred from diagrams in the `IfcAlignment` documentation.

2. The ordering of `IfcAlignmentSegment` instances within each layout's nest is not specified by the schema.

3. No guidance is given on the proper `RepresentationIdentifier` or `RepresentationType` for `IfcPolyline` and `IfcOffsetCurveByDistances` alignment representations.

4. No guidance is provided on how to define complete 3D geometry in regions of the horizontal alignment that do not overlap with the vertical or cant curves.

---

## Chapter 2 — Horizontal Alignments

5. `IfcAlignmentHorizontalSegment` implies the cubic formula coefficient must carry units of Length⁻², directly contradicting `IfcPolynomialCurve`, which declares all coefficients as dimensionless `IfcReal` scalars.

---

## Chapter 3 — Vertical Alignments

6. The geometric mapping for `IfcClothoid` in a vertical context is undocumented; the only available reference implementation produces degenerate zero-length results and cannot serve as a reference.

7. `IfcAlignmentVerticalSegment.RadiusOfCurvature` is optional and may be absent or inconsistent with the required attributes; the spec does not mandate that it be derivable from them.

---

## Chapter 4 — Cant Alignments

8. The cant transition type should match the horizontal transition type and segment length, but IFC does not enforce this constraint.

9. The EnrichIfc4x3 reference implementation contains compensating errors in cant coefficient mapping that produce correct deviating elevation values; mixing that mapping with independently derived equations produces results off by a factor of L.

---

## Chapter 5 — Offset Curves

10. The spec does not require `IfcOffsetCurveByDistances.BasisCurve` and the `BasisCurve` of its `OffsetValues` to reference the same curve object; this constraint is also not enforced by the bSI Validation Service.

11. No interpolation method is prescribed between consecutive `IfcPointByDistanceExpression` entries; multiple valid methods exist, and different implementations may render the same model differently from identical data.

12. Because no interpolation method is mandated, distance along an offset curve is approximate and not reproducible across implementations.

13. The spec does not prohibit a "split-basis" configuration (where the outer `BasisCurve` and the `OffsetValues` `BasisCurve` differ), despite this configuration being semantically meaningless; it passes all validation service checks.

---

## Chapter 6 — Approximate Alignment Geometry

14. No concept templates exist showing how `IfcPolyline` or `IfcIndexedPolyCurve` provide a geometric representation of `IfcAlignment` (the same gap applies to `IfcOffsetCurveByDistances`).

15. The `IfcPolyline` WHERE rule WR1 prohibits coincident vertices, making it structurally incompatible with the zero-length segments required by a complete semantic alignment layout; the two representations are mutually exclusive in IFC4x3.

---

## Chapter 7 — Alignments Reusing Horizontal Layout

16. No concept template exists for geometric representation when reusing horizontal layout; four questions remain open: representation ownership, horizontal curve ownership, whether geometry must be all-or-nothing, and whether mixed representation types are permitted.

17. Dual-track and dual-carriageway configurations are common in practice but cannot be fully represented; no concept template supports these use cases.

---

## Chapter 8 — Linear Placement

18. The default value of the `Axis` attribute in `IfcAxis2PlacementLinear` when omitted is not unambiguously defined; two conflicting interpretations exist in practice and the issue is tracked as open in the buildingSMART community.

19. Distance along `IfcOffsetCurveByDistances` is only approximate; two implementations using different sampling densities may compute different positions for the same `DistanceAlong` value.

---

## Chapter 9 — Referents and Stationing

20. Whether layout sub-objects and referents should share a single `IfcRelNests` relationship or use separate ones is not resolved; two patterns exist in practice.

21. For `INTERSECTION` referents, the spec does not define which crossing alignment's curve should serve as the `BasisCurve` in `IfcPointByDistanceExpression`; no normative guidance exists.

---

## Chapter 10 — Sectioned Surfaces and Solids

22. It is unclear whether all tagged cross-section vertices independently participate in guide-curve matching or whether some may fall back to linear interpolation between authored sections.

23. The spec does not clarify whether guide curve `BasisCurve`s must match the surface/solid `Directrix`; this affects tag scoping and will produce incompatible results across implementations.

24. Behavior is undefined when a tagged cross-section vertex has no corresponding guide curve; it is unclear whether the vertex falls back to linear interpolation or whether the model is in error.

25. When a cross-section vertex and a guide curve with a matching tag occupy different positions at the same cross-section, the spec does not say which governs.

26. The default `Axis` direction in `IfcAxis2PlacementLinear` for cross-section positions is undefined (the same ambiguity as §8.3.2); interpretations diverge on graded alignments and are incompatible on canted alignments.

27. The `IfcSectionedSolidHorizontal` specification incorrectly states that the profile X axis aligns with `RefDirection`; this contradicts `IfcSectionedSurface` and would produce degenerate geometry if implemented as written.

28. Figure 8.8.3.35.C in the IFC spec incorrectly depicts sectioned solids extending to the directrix head and tail, contradicting the accompanying specification text.

29. Guide curves are geometrically referenced through the surface or solid (itself a rooted entity), but the bSI Validation Service does not trace that path and incorrectly flags them as unassociated.

30. When guide curves carry independent `BasisCurve`s whose lengths are mismatched to the directrix and cross-section endpoints, the spec does not define which geometry governs.

---

## Chapter 11 — Precision and Tolerance

31. The spec is silent on how implementations should respond when a computed segment endpoint does not match the stored start point of the next segment, even when a `CONTSAMEGRADIENT` or `CONTSAMEGRADIENTSAMECURVATURE` transition is declared.

32. No implementation agreement exists for how `Pset_Tolerance` and `Pset_Uncertainty` properties should be used; recommended properties carry no normative weight.
