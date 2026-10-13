# Revision Log

| Date | Description | By |
|------|-------------|-----|
| 30 Jun 2026 | Chapter 8 revised and expanded: reorganized offset/unreachable-points content into §8.2.1, added §8.2.2 (Stationing and DistanceAlong) and §8.3.3 (Linear Placement Example), and updated/added several figures. | R. Brice |
| 6 Jul 2026 | Chapter 8 cleanup following the 30 Jun restructuring: removed an unused figure, fixed stale cross-references, and regenerated Figure 8.2.1-1. | R. Brice |
| 7 Jul 2026 | Chapter 8 §8.2/§8.3 rewritten to separate `IfcAxis2PlacementLinear`'s Location and Orientation roles, anchored on `BasisCurve`'s tangent; fixed Figure 8.1.2-2 units, and added a §12.3.4 vertical-offset test case. | R. Brice |
| 8 Jul 2026 | Chapter 9 §9.5.2 example reworked with a non-zero starting station to clarify Station vs. `DistanceAlong`; Figure 9.5.2-1 extended with `IfcAlignment`, a second `IfcRelPositions`, and a starting-station referent; §9.6 checklist updated. | R. Brice |
| 9 Jul 2026 | Chapter 9 updated to cover the Product Span Positioning concept. | R. Brice |
| 10 Jul 2026 | §9.5 rewritten per ISO 19148 §6.2.12.1. | R. Brice |
| 13 Jul 2026 | §9.5.3 simplified: `IfcAnnotation` removed from the intersection-referent correlation pattern. | R. Brice |
| 15 Jul 2026 | §10.5.4 expanded to cover cross-section/string-line redundancy. | R. Brice |
| 17 Jul 2026 | Chapter 10 expanded to cover an additional guide-curve rooting and tag scoping technique, with examples and figures updated to match. | R. Brice |
| 31 Jul 2026 | Chapter 10 §10.5 restructured around bSI-InfraRoom/IFC-Specification#118 (the guide-curve mechanism's origin issue) | R. Brice |
| 1 Aug 2026 | Added §9.3.4 (Key-Point Referents) and §9.5.2 (IfcRelInterfersElements) | R. Brice |
| 5 Aug 2026 | §9.3.4 corrected: key-point referents nest to `IfcAlignment` (Concept Template 4.1.4.4.3 Object Nesting) | R. Brice |
| 13 Oct 2026 | Helmert test data corrected. The `HELMERTCURVE` test cases (horizontal and cant, all unit variants) and the BPaimio–Kupittaa real-world alignment were generated with an IfcOpenShell defect. The second half of each Helmert curve was placed using the heading at the x coordinate the integration had reached, θ(x), instead of the heading at arc length s, θ(s). Every Helmert curve therefore had a heading kink at its midpoint and ended away from the curve its design parameters describe. The geometry IFC, semantic terminator segments, reference CSVs and plots have been regenerated. Implementations validated against the old Helmert reference data will now differ from it by up to about 2.2 cm (0.071 ft) in position and 4.35 × 10⁻⁴ rad in direction at the end of the curve (100 m transition from R 300 m to R 1000 m). The difference is zero over the first half of the curve and grows over the second half. An implementation that matched the old data reproduced the defect; one that follows §2.7 now matches. The real-world 3D reference CSVs are now sampled at every metre instead of at 100 equal intervals. The §2.7.2/§2.7.3 worked example's parent-curve position, normalization matrix and raw-spiral integrals were also corrected; these were arithmetic errors unrelated to the defect. | R. Brice |

