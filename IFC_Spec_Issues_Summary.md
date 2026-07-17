# IFC Specification Gaps — Implementation Guide Findings

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

10. The EnrichIfc4x3 reference implementation contains compensating errors in cant coefficient mapping that produce correct deviating elevation values; mixing that mapping with independently derived equations produces results off by a factor of L (§4.11).

---

## Chapter 5 — Offset Curves

11. The spec does not require `IfcOffsetCurveByDistances.BasisCurve` and the `BasisCurve` of its `OffsetValues` to reference the same curve object; this "split-basis" configuration is semantically ambiguous but passes all validation service checks (§5.1, §5.5.3).

12. No interpolation method is prescribed between consecutive `IfcPointByDistanceExpression` entries; multiple valid methods exist, and different implementations may render the same model differently from identical data (§5.3).

13. Because no interpolation method is mandated, distance along an offset curve is approximate and not reproducible across implementations (§5.2).

---

## Chapter 6 — Approximate Alignment Geometry

14. No concept templates exist showing how `IfcPolyline` or `IfcIndexedPolyCurve` provide a geometric representation of `IfcAlignment` (the same gap applies to `IfcOffsetCurveByDistances`) (§6.2).

15. The `IfcPolyline` WHERE rule WR1 prohibits coincident vertices, making it structurally incompatible with the zero-length segments required by a complete semantic alignment layout; the two representations are mutually exclusive in IFC4x3 (§6.2).

---

## Chapter 7 — Alignments Reusing Horizontal Layout

16. No concept template exists for geometric representation when reusing horizontal layout; four questions remain open: representation ownership, horizontal curve ownership, whether geometry must be all-or-nothing, and whether mixed representation types are permitted (§7.2).

17. Double-track and dual-carriageway configurations are common in practice but cannot be fully represented; no concept template supports these use cases (§7.5).

---

## Chapter 8 — Linear Placement

18. The default value of the `Axis` attribute in `IfcAxis2PlacementLinear` when omitted is not unambiguously defined; two conflicting interpretations exist in practice and the issue is tracked as open in the buildingSMART community (§8.3.2).

19. Distance along `IfcOffsetCurveByDistances` is only approximate; two implementations using different sampling densities may compute different positions for the same `DistanceAlong` value (§8.5.1).

---

## Chapter 9 — Referents and Stationing

20. The ordering of `IfcReferent` instances within `IfcRelNests.RelatedObjects` (by increasing `DistanceAlong`) is required only by the IFC concept template, not by a schema `WHERE` rule; a model with an unsorted list still validates (§9.3.1).

21. Whether layout sub-objects and referents should share a single `IfcRelNests` relationship or use separate ones is not resolved; two patterns exist in practice (§9.3.2).

22. The schema does not restrict `IfcReferent.ObjectPlacement` to `IfcLinearPlacement`; `IfcLocalPlacement` and `IfcGridPlacement` are schema-valid alternatives but carry no `DistanceAlong` value, leaving no reliable basis for ordering referents or performing station-to-distance conversions (§9.3.3).

23. At a station-equation overlap, a single station value maps to two geometrically valid `DistanceAlong` positions; the schema provides no way to disambiguate them, and implementations must apply a project-specific convention (§9.2.6).

24. Nothing in the schema formally correlates the two `INTERSECTION` referents that represent the same physical crossing (one per intersecting alignment, per ISO 19148 §6.2.12.1); the guide's `IfcGroup`/`IfcRelAssignsToGroup` convention records the correspondence, but the schema does not require or expose it as a formal relationship (§9.5).

---

## Chapter 10 — Sectioned Surfaces and Solids

25. Although required for the geometry to be unambiguous, the spec does not explicitly state that an `IfcOpenCrossProfileDef` segment's `Slope` and `Width` must be zero at a breakline's start/end distance along the directrix (§10.3.1).

26. It is unclear whether all tagged cross-section vertices independently participate in guide-curve matching, or whether an unmatched vertex falls back to linear interpolation between authored sections rather than being treated as a modeling error (§10.3.2, §10.5.2).

27. The spec does not state whether a guide curve's `BasisCurve` must match the surface/solid `Directrix`; three candidate tag-scoping rules exist (Local Scoping, Global Scoping, Representation Scoping), none has a basis in the specification text, and no implementation agreement designates which governs (§10.5.1).

28. IFC provides no forward reference (attribute, inverse relationship, or STEP entity identifier) from a tagged vertex to the guide curve controlling it; a consuming application must perform a global search of the model for a matching `Tag`, and tag scoping only disambiguates the results of that search rather than eliminating the need for it (§10.5.1).

29. Figure 8.8.3.35.C in the IFC specification incorrectly depicts sectioned solids extending to the directrix head and tail, contradicting the accompanying specification text (§10.5.3).

30. When a cross-section vertex and a guide curve with a matching tag occupy different positions at the same cross-section, the spec does not say which governs, nor whether the authored coordinate must be geometrically consistent with the guide curve or may serve only as a placeholder (§10.5.4).

31. The default `Axis` direction in `IfcAxis2PlacementLinear` for cross-section positions is undefined (the same ambiguity as §8.3.2); interpretations diverge on graded alignments and are incompatible on canted alignments (§10.5.5).

32. The `IfcSectionedSolidHorizontal` specification incorrectly states that the profile X axis aligns with `RefDirection`; this contradicts `IfcSectionedSurface` and would produce degenerate geometry if implemented as written (§10.5.6).

33. Guide curves are geometrically referenced through the surface or solid (itself a rooted entity) by way of the `Tag` mechanism, but the bSI Validation Service does not trace that path and flags them as unassociated (IFC105); at least three techniques resolve this in practice — placeholder `IfcAlignment`, placeholder `IfcAnnotation`, and sibling representation — but none is prescribed by the spec (§10.5.7).

34. When guide curves carry an independent `BasisCurve` whose length or position is mismatched to the directrix and cross-section endpoints, the spec does not define which geometry governs (§10.6.1.6, §10.6.2.6).

---

## Chapter 11 — Precision and Tolerance

35. No implementation agreement exists for how `Pset_Tolerance` and `Pset_Uncertainty` properties should be used; recommended properties carry no normative weight (§11.0).

36. The spec is silent on how implementations should respond when a computed segment endpoint does not match the stored start point of the next segment, even when a `CONTSAMEGRADIENT` or `CONTSAMEGRADIENTSAMECURVATURE` transition is declared (§11.1).
