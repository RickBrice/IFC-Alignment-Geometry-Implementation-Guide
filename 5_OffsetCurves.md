# Chapter 5 — Offset Curves

## 5.0 Introduction

Offset curves are very common in infrastructure geometry. Some examples are:

* Edge of pavement
* Bridge girder centerlines
* Lane striping
* Utility centerline

`IfcOffsetCurveByDistances` defines the geometry of offset curves. It has
three attributes:

* `BasisCurve`: The curve from which offsets are measured
* `OffsetValues`: Defines the offsets along the curve
* `Tag` (optional): An identifier for the curve, used to correlate offset curve points with positions in a variable cross-section (see [Chapter 10](10_Sectioned_Surfaces_and_Solids.md))

A single offset value indicates a constant offset over the entire length of the curve.

If the offsets do not span the full length of the curve, the first and last offset are implicitly continued to the head and tail of the basis curve, respectively.

The `IfcOffsetCurveByDistances.OffsetValues` are of type `IfcPointByDistanceExpression`. The `IfcOffsetCurveByDistances.BasisCurve` and `IfcPointByDistanceExpression.BasisCurve` should logically reference the same curve since the offset value is defining an offset from `IfcOffsetCurveByDistances.BasisCurve`. However, this is not an explicitly stated requirement in the IFC specifications nor is it enforced by the bSI Validation Service [8].

The `IfcOffsetCurveByDistances` geometry is derived by interpolating the `OffsetValues`.

![Figure 5.0-1 — 3D Blender viewport showing a BasisCurve (orange/yellow curved alignment) flanked by two IfcOffsetCurveByDistances instances rendered in orange: OffsetCurve1 above and OffsetCurve2 below, illustrating positive and negative lateral offsets from the reference alignment.](images/Figure_5.0-1_Offset_Curves.png)

*Figure 5.0-1 Offset curves*

Figure 5.0-1 shows two offset curves that share a single basis curve. Offset curve 1 has different offset values defined at the start and the end of the basis curve. The start offset is 10 ft and the end offset is 20 ft. The basis curve is 100 ft long. The point on Offset curve 1 that corresponds to the mid-point of the basis curve is determined by evaluating the basis curve at 50 ft, then applying the linearly interpolated offset of 15 ft.

Offset curve 2 has several offsets. Linear interpolation is used to determine the offset from the basis curve to the offset curve between each pair of consecutive offset points.

The following IFC STEP excerpt illustrates how these two offset curves are encoded. The basis curve `#20` is a circular arc.

**Offset1** — left side, linearly varying:

```
#88=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),10.,$,$,#20);
#89=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(200.),20.,$,$,#20);
#94=IFCOFFSETCURVEBYDISTANCES(#20,(#88,#89),$); /* Tag omitted */
```

The offset begins at +10 at distance 0 and increases linearly to +20 at distance 200 along the basis curve. At the midpoint of the basis curve (distance 100) the interpolated offset is +15.

**Offset2** — right side, multi-point:

```
#102=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),-10.,$,$,#20);
#103=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(50.),-40.,$,$,#20);
#104=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(100.),-20.,$,$,#20);
#105=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(150.),-30.,$,$,#20);
#106=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(200.),-20.,$,$,#20);
#111=IFCOFFSETCURVEBYDISTANCES(#20,(#102,#103,#104,#105,#106),$); /* Tag omitted */
```

The right-side offset widens quickly from −10 to −40 over the first 50 distance units along the basis curve, then narrows to −20 at mid-curve, widens again to −30, and finishes at −20. Positive lateral offsets place the offset curve to the left of the basis curve and negative offsets to the right, measured perpendicular to the curve looking in the direction of increasing distance.

Both offset curves share the same basis curve `#20`. Each `IfcPointByDistanceExpression` also references `#20` directly — the logical choice, since each offset value defines a lateral distance from that curve. The case where these two basis curve references differ is explored in §5.5.3.

The STEP excerpt above is drawn from the example models [`IfcOffsetCurveByDistances_2D.ifc`](examples/IfcOffsetCurveByDistances_2D.ifc) and [`IfcOffsetCurveByDistances_3D.ifc`](examples/IfcOffsetCurveByDistances_3D.ifc), which are discussed further in §5.5.

## 5.1 Offset Curves and IfcAlignment

In IFC4x3, `IfcOffsetCurveByDistances` is a resource-layer geometric entity and cannot exist independently in a model. Validation rule [IFC105](https://buildingsmart.github.io/ifc-gherkin-rules/branches/main/features/IFC105_Resource-entities-need-to-be-referenced-by-rooted-entity.html) [5] requires that every resource entity be reachable from a rooted entity. In practice this means the offset curve must be assigned as the shape representation of an `IfcAlignment` (or another product), and that alignment must be aggregated into the project. Without this, the IFC validation service will report an IFC105 violation.

The consequence is that offset curves in IFC4x3 models are represented as alignments. This is natural: an offset alignment has its own object identity, can carry properties, can support linear placement of objects, and participates in the project's spatial breakdown just like the basis alignment.

The example file [`IfcOffsetCurveByDistances_2D.ifc`](examples/IfcOffsetCurveByDistances_2D.ifc) demonstrates this structure. The basis alignment "E-Line" and its two offsets, "Offset1" and "Offset2," are all `IfcAlignment` instances aggregated under the project. Each offset alignment's `Representation` references an `IfcShapeRepresentation` whose item is the corresponding `IfcOffsetCurveByDistances`.

When `IfcOffsetCurveByDistances` is used as a guide curve for `IfcSectionedSurface` or `IfcSectionedSolidHorizontal`, the same requirement applies with an additional complication. The guide curve is geometrically referenced by the surface or solid through the tag mechanism, and the surface or solid is itself a rooted entity — so the chain of references back to a rooted entity exists. The validation service does not trace this path, however, and still flags guide curves that are not directly assigned as a representation of a rooted entity. See [§10.5](10_Sectioned_Surfaces_and_Solids.md#validation-service-ifcoffsetcurvebydistances-must-be-referenced-by-a-rooted-entity) for the practical consequence.

## 5.2 Accuracy of Offset Curves

`IfcOffsetCurveByDistances` produces an exact geometric parallel only for lines and circular arcs with a constant offset. Even with a constant offset, transition curves have no closed-form geometric parallel — the true parallel of a Clothoid spiral, for example, is not a Clothoid. The resulting geometry is always a piecewise-linear approximation of the true offset, regardless of whether the offset is constant or varying. Accuracy improves by adding more `IfcPointByDistanceExpression` values at shorter intervals, densifying the approximation.

For most infrastructure applications, the linear interpolation error is small relative to construction tolerances. For applications requiring tighter accuracy — such as rail superelevation ramps or precision survey control — the approximation should be evaluated against the required tolerance and the offset point spacing adjusted accordingly.

A further consequence of the approximation is that **distance along** the offset curve is also approximate. When `IfcOffsetCurveByDistances` is used as the `BasisCurve` in `IfcPointByDistanceExpression` for `IfcLinearPlacement`, two independent implementations may compute different arc lengths for the same curve definition.

The arc length of `IfcOffsetCurveByDistances` at any given location is obtained by numerically integrating the offset curve geometry between the sample points. Because the IFC specification does not prescribe the interpolation method (see §5.3), different software may produce different intermediate curve shapes from identical `OffsetValues`, and therefore different arc lengths. Even if the interpolation method is agreed upon, the arc length integral has no closed form for a general offset from a spiral, so implementations must use numerical quadrature with finite precision or approximate series expansion solutions.

The consequence is that a `DistanceAlong` value specified against an `IfcOffsetCurveByDistances` does not map to a unique, reproducible point across implementations. This is in direct contrast to `DistanceAlong` measured along an `IfcCompositeCurve` or `IfcGradientCurve`, where arc length is determined exactly by the curve equations.

For precise linear placement, the recommended practice (discussed fully in [§8.6](8_LinearPlacement.md#86-linear-placement-along-ifcoffsetcurvebydistances)) is to reference the **parent alignment** as the `BasisCurve` in `IfcPointByDistanceExpression` and use `OffsetLateral` to account for the transverse distance — rather than placing objects directly along the offset curve. This avoids the arc-length approximation entirely and keeps placement reproducible across software implementations.

## 5.3 Interpolation of Offset Values

The IFC specification does not prescribe how offset values are to be interpolated between `IfcPointByDistanceExpression` entries. Several methods are possible:

* **Linear interpolation of offset values** — the lateral offset distance is interpolated linearly between consecutive offset points, and the interpolated distance is applied perpendicular to the basis curve at each chainage. This keeps the offset curve anchored to the basis curve geometry.
* **Linear interpolation between 3D points** — the 3D positions of consecutive offset points are computed and connected by straight line segments. This produces a true piecewise-linear curve in space, but one that drifts away from the basis curve between offset points.
* **Spline interpolation** — cubic spline, B-spline, Bézier, or NURBS methods applied to either the offset values or the 3D positions, producing smoother curves but with greater implementation complexity.

Different interpolation methods produce materially different geometry from the same `IfcOffsetCurveByDistances` data. This is illustrated in Figure 5.3-1 which overlays a spline interpolation onto the linear interpolation from Figure 5.0-1. Without a formal implementation agreement, two compliant applications may render the same model differently.

![Figure 5.3-1 — 3D Blender viewport showing a BasisCurve (orange/yellow) alongside an offset curve computed via spline interpolation (dashed white/teal), overlaid on the linear interpolation from Figure 5.0-1. The spline produces a smoother offset path between the discrete control points.](images/Figure_5.3-1_Spline_Interplotation.png)

*Figure 5.3-1 - Comparison of linear and spline interpolation*

The recommended best practice is **linear interpolation of offset values**: interpolate the lateral distance at each chainage position, then apply that distance perpendicular to the basis curve. This method is the most natural given the structure of `IfcOffsetCurveByDistances`, produces predictable geometry, and is the least ambiguous for interchange.

## 5.4 The Tag Attribute

The `Tag` attribute of `IfcOffsetCurveByDistances` is an optional label that assigns an identifier to the offset curve. Its primary purpose is to correlate an offset curve with a named point in a variable cross-section definition.

`IfcSectionedSurface` and `IfcSectionedSolidHorizontal` define geometry by sweeping a series of cross-sections along a basis curve. Each cross-section can contain named control points — edge-of-pavement, top-of-rail, daylight line, and so on. The `Tag` on an `IfcOffsetCurveByDistances` matches one of those named points, allowing the surface or solid geometry to be driven by the offset curve's lateral positions rather than by fixed cross-section ordinates. This is the mechanism by which variable-width surfaces and solids are defined in IFC4x3.

The full treatment of `IfcSectionedSurface` and `IfcSectionedSolidHorizontal`, including how `Tag` values are resolved against cross-section geometry, is covered in [Chapter 10](10_Sectioned_Surfaces_and_Solids.md).

## 5.5 Example Models

Three example models illustrate `IfcOffsetCurveByDistances` in progressively more demanding configurations. The 2D and 3D variants share the same geometry and offset profiles; the difference is whether the basis curve is an `IfcCompositeCurve` (horizontal only) or an `IfcGradientCurve` (3D). The split-basis variant tests a configuration the IFC specification does not prohibit but leaves geometrically ambiguous.

### 5.5.1 Two-Dimensional Basis Curve

The file [`IfcOffsetCurveByDistances_2D.ifc`](examples/IfcOffsetCurveByDistances_2D.ifc) contains a basis alignment and two offset alignments. The basis curve is an `IfcCompositeCurve` — a horizontal-only curve with no elevation component.

**Validation.** Both offset alignments in this model fail the validation rule `IfcShapeRepresentation.CorrectItemsForType`. The `IfcShapeRepresentation` for each offset alignment uses `RepresentationType = "Curve3D"`, which requires its items to be 3D curves. The `IfcOffsetCurveByDistances` entities here are 2D because their `BasisCurve` is an `IfcCompositeCurve` — a planar horizontal curve with no elevation component. The `IfcAlignment` specification permits `IfcOffsetCurveByDistances` to represent either a 2D or 3D alignment curve, but the validation service's `CorrectItemsForType` rule does not account for this — it requires `Curve3D` items to be 3D regardless. This is a gap in the validation service, not a conflict in the specification. It is anticipated that the next version of the buildingSMART Validation Service will not flag this as an error.

### 5.5.2 Three-Dimensional Basis Curve

The file [`IfcOffsetCurveByDistances_3D.ifc`](examples/IfcOffsetCurveByDistances_3D.ifc) extends the 2D example by adding a flat vertical alignment to the basis alignment, making its basis curve an `IfcGradientCurve`. The two offset alignments are constructed to demonstrate how basis curve choice affects dimensionality and validation outcome.

**Offset1** references the `IfcGradientCurve` as the `BasisCurve` in both the `IfcOffsetCurveByDistances` and all `IfcPointByDistanceExpression` offset values. Because `IfcGradientCurve` is a 3D curve, the resulting offset curve is 3D. Offset1 satisfies `IfcShapeRepresentation.CorrectItemsForType`.

**Offset2** references `IfcGradientCurve.BaseCurve` — the underlying `IfcCompositeCurve` — as the `BasisCurve` for its offset values. `IfcCompositeCurve` is a 2D horizontal curve, so the resulting offset curve is 2D regardless of whether the parent alignment has a vertical component. Offset2 fails `IfcShapeRepresentation.CorrectItemsForType` for the same reason as the 2D example. It is anticipated that the next version of the buildingSMART Validation Serivce will not flag this as an error.

The key finding is that the dimensionality of an `IfcOffsetCurveByDistances` is determined by which curve object is referenced as its `BasisCurve` — not by the dimensionality of the alignment that owns it. Referencing an `IfcGradientCurve` produces a 3D offset curve; referencing its constituent `IfcCompositeCurve` produces a 2D one.

### 5.5.3 Split Basis Curves

The file [`IfcOffsetCurveByDistances_split_basis.ifc`](examples/IfcOffsetCurveByDistances_split_basis.ifc) demonstrates the edge case described in §5.0 where `IfcOffsetCurveByDistances.BasisCurve` and `IfcPointByDistanceExpression.BasisCurve` reference different curves. The model contains two basis alignments — a circular arc and a straight line — each with a flat vertical profile and an `IfcGradientCurve` basis curve.

The single offset alignment has its `IfcOffsetCurveByDistances.BasisCurve` set to the circular arc's `IfcGradientCurve`, while its `IfcPointByDistanceExpression` offset values reference the straight line's `IfcGradientCurve`. Because the two curves have different shapes, the parameterization of the offset values is inconsistent with the curve to which they are applied.

The IFC specification does not prohibit this configuration, and the model passes all validation service checks. This is itself a gap: the split-basis configuration is semantically ambiguous and should be flagged as either an error or a best-practices violation. A future validation rule requiring that `IfcOffsetCurveByDistances.BasisCurve` and the `BasisCurve` of all its `OffsetValues` reference the same curve object would close this gap without breaking any legitimate use case.
