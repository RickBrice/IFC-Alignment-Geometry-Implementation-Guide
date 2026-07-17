# Future Work

Content gaps and topics to research and expand as understanding of IFC continues to develop. Unlike `IFC_Spec_Issues_Summary.md` — which tracks gaps and errors in the IFC specification itself — this list tracks gaps in the *guide's own coverage*: topics not yet explained, examples not yet built, or areas needing deeper research before they can be written up.

- [ ] Update the discussion of IFC specification gaps in `IFC_Spec_Issues_Summary.md` as they get resolved by buildingSMART or by further research.

- [ ] Research and add examples covering grade-separated and at-grade intersections. `IfcRelInterferesElements` appears to be relevant — it carries interference types such as `Crosses`, `PassesThrough`, `PassesOver`, and `PassesUnder` (exact values to verify during research). This relationship is part of the Alignment-based View (AbV) MVD, so it's worth discussing. (Chapter 9 already covers `INTERSECTION` referents at §9.5; this would extend that discussion.)

- [ ] Provide a better explanation of the other referent types (`MARKER`, `MILEPOST`, etc.) and how they are modeled. (Chapter 9, §9.1.)

- [ ] Provide a better explanation of linear reference systems. One example worth covering: a milepost system where mileage resets to zero when a highway crosses into a new state — e.g., an interstate bridge crossing a river, where the mileage reference changes at the midpoint but stationing is likely continuous through the entire project alignment. (Chapter 8 §8.6 covers ISO 19148 linear referencing generally; Chapter 9 covers stationing.)

- [ ] Continue to improve and clarify string-line-based geometry for sectioned surfaces and solids. Right now there are more open questions than answers. (Chapter 10, §10.5 — see also `IFC_Spec_Issues_Summary.md` #25–34.)

- [ ] Add a discussion of MVDs and the Alignment-based View (AbV) in particular, including why some entities are included and others excluded.

- [ ] Expand the LandXML appendix (Appendix A).

- [ ] Provide a worked example of the dual-carriageway and 7-line (double-track) alignment problem. (Chapter 7, §7.5 documents this as an unsupported use case; see also `IFC_Spec_Issues_Summary.md` #17.)

- [ ] Analyze, break down, and provide examples for the [§8.9.3.28 `IfcCurveSegment`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcCurveSegment.htm) statement that when an `IfcCurveSegment` is placed via `IfcAxis2PlacementLinear`, the positioning curve (`Placement.Location.BasisCurve`) does not necessarily correspond with the segment's own `ParentCurve`. Not currently discussed anywhere in the guide — Chapter 2's only citation of §8.9.3.28 is for an unrelated point (Informal Proposition 1, arc-length parameterization), and `ParentCurve` does not appear in Chapter 8 at all.

- [ ] Investigate whether it's a genuine discrepancy that `IfcSectionedSolidHorizontal.CrossSectionPositions.Location` (an `IfcPointByDistanceExpression`) is governed by the `NoLongitudinalOffsets` formal proposition (forbidding longitudinal offsets only), while `IfcSectionedSurface.CrossSectionPositions.Location` — also an `IfcPointByDistanceExpression` — is governed by `NoOffsets` (forbidding longitudinal, lateral, *and* vertical offsets). Why are the two formal propositions different? (Chapter 10 currently only states the solid's restriction, at §10.4, and never mentions the surface's — see also `IFC_Spec_Issues_Summary.md`.)
