# IFC Specification Issues — Part 2

*IFC Alignment Geometry Implementation Guide, Part 2 — Advanced Topics: Placement, Referencing, and Derived Geometry*

This summary lists gaps, ambiguities, and errors in the IFC4x3 specification identified while preparing Chapters 6–12 of this guide. Each item cites the section of the guide where it is discussed. Items are numbered independently in each part of the guide.

---

## Chapter 6 — Offset Curves

1. The spec does not require `IfcOffsetCurveByDistances.BasisCurve` and the `BasisCurve` of its `OffsetValues` to reference the same curve object; this "split-basis" configuration is semantically ambiguous but passes all validation service checks (§6.1, §6.5.3).

2. Because no interpolation method is mandated, distance along an offset curve is approximate and not reproducible across implementations (§6.2).

3. No interpolation method is prescribed between consecutive `IfcPointByDistanceExpression` entries; multiple valid methods exist, and different implementations may render the same model differently from identical data (§6.3).

---

## Chapter 7 — Approximate Alignment Geometry

4. No concept templates exist showing how `IfcPolyline` or `IfcIndexedPolyCurve` provide a geometric representation of `IfcAlignment` (the same gap applies to `IfcOffsetCurveByDistances`) (§7.2).

5. The `IfcPolyline` WHERE rule WR1 prohibits coincident vertices, making it structurally incompatible with the zero-length segments required by a complete semantic alignment layout; the two representations are mutually exclusive in IFC4x3 (§7.2).

---

## Chapter 8 — Alignments Reusing Horizontal Layout

6. No concept template exists for geometric representation when reusing horizontal layout; four questions remain open: representation ownership, horizontal curve ownership, whether geometry must be all-or-nothing, and whether mixed representation types are permitted (§8.2).

7. Double-track and dual-carriageway configurations are common in practice but cannot be fully represented; no concept template supports these use cases (§8.5).

---

## Chapter 9 — Linear Placement

8. The default value of the `Axis` attribute in `IfcAxis2PlacementLinear` when omitted is not unambiguously defined; two conflicting interpretations exist in practice and the issue is tracked as open in the buildingSMART community (§9.3.2).

9. Distance along `IfcOffsetCurveByDistances` is only approximate; two implementations using different sampling densities may compute different positions for the same `DistanceAlong` value (§9.5.1).

---

## Chapter 10 — Referents and Stationing

10. At a station-equation overlap, a single station value maps to two geometrically valid `DistanceAlong` positions; the schema provides no way to disambiguate them, and implementations must apply a project-specific convention (§10.2.6).

11. The ordering of `IfcReferent` instances within `IfcRelNests.RelatedObjects` (by increasing `DistanceAlong`) is required only by the IFC concept template, not by a schema `WHERE` rule; a model with an unsorted list still validates (§10.3.1).

12. Whether layout sub-objects and referents should share a single `IfcRelNests` relationship or use separate ones is not resolved; two patterns exist in practice (§10.3.2). Where they do share one nest, the `RelatedObjects` order between a whole-alignment layout sub-object and a referent located partway along it (e.g. a `SUPERELEVATIONEVENT`, a `POSITION` referent at a vertical curve's low point, or an `INTERSECTION` referent inside a segment) is left undefined — the layout sub-objects have no single `DistanceAlong` to sort by, and the schema supplies no convention (§10.3.2).

13. The schema does not restrict `IfcReferent.ObjectPlacement` to `IfcLinearPlacement`; `IfcLocalPlacement` and `IfcGridPlacement` are schema-valid alternatives but carry no `DistanceAlong` value, leaving no reliable basis for ordering referents or performing station-to-distance conversions (§10.3.3).

14. Concept Template 4.1.4.4.3 (Object Nesting) is the only schema mechanism that establishes alignment stationing (`STATION` referents, §10.3.1) or key-point referents (§10.3.4), yet the template itself is not tagged as part of the Alignment-based View (AbV); a conformance check applied strictly by MVD tag could flag conforming stationing/key-point-referent models as out of scope even though no alternative AbV-tagged mechanism exists (§10.3.4).

15. `IfcConnectionGeometry` is tagged as part of the Alignment-based View (AbV), but none of its five concrete subtypes — including `IfcConnectionPointGeometry` and `IfcConnectionPointEccentricity`, the only types usable as `IfcRelInterferesElements.InterferenceGeometry` — carry that tag themselves; the same tag-propagation gap as item 14, here affecting intersection-crossing geometry rather than referent nesting (§10.5.2).

16. `IfcRelInterferesElements.InterferenceType` is typed as free-text `IfcIdentifier` rather than a restricted enumeration; the schema documentation's example values (`Crosses`, `PassesOver`, `PassesUnder`, `PassesThrough`, `Along`, `Clash`) carry no normative weight, so two implementations recording the same physical relationship may choose different vocabularies and neither is non-conforming (§10.5.2).

---

## Chapter 11 — Sectioned Surfaces and Solids

17. Although required for the geometry to be unambiguous, the spec does not explicitly state that an `IfcOpenCrossProfileDef` segment's `Slope` and `Width` must be zero at a breakline's start/end distance along the directrix (§11.3.1).

18. It is unclear whether all tagged cross-section vertices independently participate in guide-curve matching, or whether an unmatched vertex falls back to linear interpolation between authored sections rather than being treated as a modeling error (§11.3.2, §11.5.4).

19. The spec does not state whether a guide curve's `BasisCurve` must match the surface/solid `Directrix`, nor does it explain how a guide curve — referenced only through the surface or solid by the string-valued `Tag` mechanism — satisfies the `IFC105` rootedness rule the bSI Validation Service enforces, which does not trace that reference and flags guide curves as unassociated. Design history behind the guide curve mechanism (§11.5.1) shows the working group's actual intent: host guide curves in a sibling `IfcShapeRepresentation` of the product they belong to. This construction resolves both concerns simultaneously and has been validated against the bSI Validation Service (§11.5.2, §11.6.1.4, §11.6.2.5) — but it is recoverable only from that design history, not from the spec's normative text, and the case of multiple sectioned surfaces/solids sharing one `IfcProductDefinitionShape` remains genuinely undetermined.

20. When a cross-section vertex and a guide curve with a matching tag occupy different positions at the same cross-section, the spec provides no machine-enforced consistency check — though the mechanism's own proposer confirms the intent was that the two coincide, with consistency an authoring responsibility rather than a precedence question for consuming applications (§11.5.1, §11.5.3).

21. IFC provides no forward reference (attribute, inverse relationship, or STEP entity identifier) from a tagged vertex to the guide curve controlling it; under the intended sibling-representation construction a consuming application need only compare tags among the guide curves in that same `IfcProductDefinitionShape`, but even within that narrowed scope the match is by string-equal `Tag` rather than a typed reference (§11.5.2).

22. Figure 8.8.3.35.C in the IFC specification incorrectly depicts sectioned solids extending to the directrix head and tail, contradicting the accompanying specification text (§11.5.5).

23. The default `Axis` direction in `IfcAxis2PlacementLinear` for cross-section positions is undefined (the same ambiguity as §9.3.2); interpretations diverge on graded alignments and are incompatible on canted alignments (§11.5.6).

24. The `IfcSectionedSolidHorizontal` specification incorrectly states that the profile X axis aligns with `RefDirection`; this contradicts `IfcSectionedSurface` and would produce degenerate geometry if implemented as written (§11.5.7).

---

## Chapter 12 — Precision and Tolerance

25. No implementation agreement exists for how `Pset_Tolerance` and `Pset_Uncertainty` properties should be used; recommended properties carry no normative weight (§12.0).

26. The spec is silent on how implementations should respond when a computed segment endpoint does not match the stored start point of the next segment, even when a `CONTSAMEGRADIENT` or `CONTSAMEGRADIENTSAMECURVATURE` transition is declared (§12.1).
