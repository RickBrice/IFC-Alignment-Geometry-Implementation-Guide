# Section 7 - Offset Curves

## 7.0 Introduction

Offset curves are very common in infrastructure geometry. Some examples are:

* Edge of pavement
* Bridge girder centerlines
* Lane striping
* Utility centerline

`IfcOffsetCurveByDistances` defines the geometry of offset curves. It has
three attributes:

* `BasisCurve`: The curve from which offsets are measured
* `OffsetValues`: Defines the offsets along the curve
* `Tag` (optional): An identifier for the curve, used to correlate offset curve points with positions in a variable cross-section (see Section 9)

A single offset value indicates a constant offset over the entire length of the curve.

If the offsets do not span the full length of the curve, the first and last offset are implicitly continued to the head and tail of the basis curve, respectively.

The `IfcOffsetCurveByDistances.OffsetValues` are of type `IfcPointByDistanceExpression`. `IfcOffsetCurveByDistances.BasisCurve` and `IfcPointByDistanceExpression.BasisCurve` must reference the same curve.

The `IfcOffsetCurveByDistances` geometry is derived by interpolating the `OffsetValues`.

![](images/OffsetCurves.png)

*Figure 7.0-1 Offset curves*

Figure 7.0-1 shows two offset curves that share a single basis curve. Offset curve 1 has different offset values defined at the start and the end of the basis curve. The start offset is 10 ft and the end offset is 20 ft. The basis curve is 100 ft long. The point on Offset curve 1 that corresponds to the mid-point of the basis curve is determined by evaluating the basis curve at 50 ft, then applying the linearly interpolated offset of 15 ft.

Offset curve 2 has several offsets. Linear interpolation is used to determine the offset from the basis curve to the offset curve between each pair of consecutive offset points.

Example model:
[IfcOffsetCurveByDistances.ifc](examples/IfcOffsetCurveByDistances.ifc)

## 7.1 Offset Sign Convention

Positive offset values place the offset curve to the left of the basis curve, measured perpendicular to the curve's direction of travel at each chainage position. Negative values place it to the right. This matches the curvature sign convention used throughout this guide — positive means left, negative means right.

Offset values can change sign along the curve, meaning the offset curve can cross from one side of the basis curve to the other. Practical infrastructure uses for sign-crossing offsets are rare, but the representation allows it.

## 7.2 Offset Curves and IfcAlignment

In IFC4x3, `IfcOffsetCurveByDistances` is a resource-layer geometric entity and cannot exist independently in a model. Validation rule IFC105 requires that every resource entity be reachable from a rooted entity. In practice this means the offset curve must be assigned as the shape representation of an `IfcAlignment` (or another product), and that alignment must be aggregated into the project. Without this, the IFC validation service will report an IFC105 violation.

The consequence is that offset curves in IFC4x3 models are represented as alignments. This is natural: an offset alignment has its own object identity, can carry properties, can support linear placement of objects, and participates in the project's spatial breakdown just like the basis alignment.

The example file [`IfcOffsetCurveByDistances.ifc`](examples/IfcOffsetCurveByDistances.ifc) demonstrates this structure. The basis alignment "E-Line" and its two offsets, "Offset1" and "Offset2," are all `IfcAlignment` instances aggregated under the project. Each offset alignment's `Representation` references an `IfcShapeRepresentation` whose item is the corresponding `IfcOffsetCurveByDistances`.

## 7.3 Stationing on Offset Alignments

The IFC validation service warns when an `IfcAlignment` has no stationing referent — a `Pset_Stationing` property set attached via an `IfcReferent`. For many offset alignments this warning is valid and should be resolved: a ramp, a lane edge used for striping construction, or any offset alignment along which objects are linearly placed benefits from defined stationing.

For offset alignments that are purely geometric — a drainage channel modeled for clash detection, a clearance envelope, a construction limit line — independent stationing may not be meaningful. In those cases the warning is acceptable to leave. An alternative is to assign a stationing referent that mirrors the basis alignment's stationing, so that chainage values on the offset alignment correspond directly to chainage on the basis. This is often the least confusing option when the two alignments are used together in quantity takeoff or reporting.

## 7.4 Accuracy of Offset Curves

`IfcOffsetCurveByDistances` is an exact representation for two curve types and an approximation for everything else.

**Lines and circular arcs.** The geometric parallel of a line is another line; the geometric parallel of a circular arc of radius $R$ at offset $d$ is another circular arc of radius $R + d$ (left offset) or $R - d$ (right offset). For alignments composed entirely of tangents and circular arcs, a constant `IfcOffsetCurveByDistances` with a single `IfcPointByDistanceExpression` reproduces the true parallel exactly.

**Transition curves.** The six transition curve types — Clothoid, Bloss, Cosine, Sine, Helmert, and VienneseBend — do not have closed-form geometric parallels. The true parallel of a Clothoid spiral, for example, is not a Clothoid. `IfcOffsetCurveByDistances` handles this by defining the offset through linearly interpolated lateral distances rather than a parallel curve formula. The resulting geometry is a piecewise-linear approximation of the true offset. Accuracy improves by adding more `IfcPointByDistanceExpression` values at shorter chainage intervals, densifying the approximation.

For most infrastructure applications the linear interpolation error is small relative to construction tolerances. For applications requiring tighter accuracy — such as rail superelevation ramps or precision survey control — the approximation should be evaluated against the required tolerance and the offset point spacing adjusted accordingly.

### 7.4.1 Approximate Distance Along and Its Effect on IfcLinearPlacement

A related but distinct accuracy issue arises when `IfcOffsetCurveByDistances` is used as the `BasisCurve` in `IfcPointByDistanceExpression` for `IfcLinearPlacement`. The problem is not just that the shape of the offset curve is approximate — it is that **distance along** the offset curve is also approximate, and two independent implementations may compute different arc lengths for the same curve definition.

The arc length of `IfcOffsetCurveByDistances` at any given chainage is obtained by numerically integrating the offset curve geometry between the sample points. Because the IFC specification does not prescribe the interpolation method (see §6.7), different software may produce different intermediate curve shapes from identical `OffsetValues`, and therefore different arc lengths. Even if the interpolation method is agreed upon, the arc length integral has no closed form for a general offset from a spiral, so implementations must use numerical quadrature with finite precision.

The consequence is that a `DistanceAlong` value specified against an `IfcOffsetCurveByDistances` does not map to a unique, reproducible point across implementations. This is in direct contrast to `DistanceAlong` measured along an `IfcCompositeCurve` or `IfcGradientCurve`, where arc length is determined exactly by the curve equations.

For precise linear placement, the recommended practice (discussed fully in §6.5) is to reference the **parent alignment** as the `BasisCurve` in `IfcPointByDistanceExpression` and use `OffsetLateral` to account for the transverse distance — rather than placing objects directly along the offset curve. This avoids the arc-length approximation entirely and keeps placement reproducible across software implementations.

## 7.5 Arc Length of an Offset Curve

The arc length of an offset curve differs from the basis curve length. For a constant offset $d$ from a circular arc of radius $R$ and arc length $L$:

$$L_{\text{offset}} = L \cdot \frac{R + d}{R}$$

A positive (left) offset increases arc length; a negative (right) offset inside the curve decreases it. For a left offset of 10 ft from a 1000-ft radius arc of length 200 ft:

$$L_{\text{offset}} = 200 \cdot \frac{1010}{1000} = 202 \text{ ft}$$

For varying offsets or non-circular basis curves there is no simple closed-form expression. `IfcOffsetCurveByDistances` does not expose an arc length attribute. When linear placement of objects relative to an offset alignment is needed, the recommended practice (see §6.5) is to use the parent alignment as the `BasisCurve` in `IfcPointByDistanceExpression` rather than the offset curve itself, so the arc length of the offset curve is rarely needed in practice.

## 7.6 Example Model Walkthrough

The file [`IfcOffsetCurveByDistances.ifc`](examples/IfcOffsetCurveByDistances.ifc) contains a basis alignment and two offset alignments using feet as the length unit. The relevant IFC excerpts are shown below.

**Basis curve.** The composite curve `#20` consists of a 200-foot circular arc (radius 1000 ft) starting at the origin heading east, followed by a zero-length line tangent. The arc subtends an angle of $200/1000 = 0.2$ radians, ending at approximately $(198.7, 19.9)$ ft. The basis alignment "E-Line" has stationing from 100+00 to 102+00.

**Offset1** — left side, linearly varying:

```
#88=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),10.,$,$,#20);
#89=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(200.),20.,$,$,#20);
#94=IFCOFFSETCURVEBYDISTANCES(#20,(#88,#89),$); /* Tag omitted */
```

The offset begins at +10 ft at chainage 0 and increases linearly to +20 ft at chainage 200. The midpoint of the basis curve (chainage 100) has an interpolated offset of +15 ft. This produces a left-side offset curve that diverges from the basis alignment.

**Offset2** — right side, multi-point:

```
#102=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(0.),-10.,$,$,#20);
#103=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(50.),-40.,$,$,#20);
#104=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(100.),-20.,$,$,#20);
#105=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(150.),-30.,$,$,#20);
#106=IFCPOINTBYDISTANCEEXPRESSION(IFCLENGTHMEASURE(200.),-20.,$,$,#20);
#111=IFCOFFSETCURVEBYDISTANCES(#20,(#102,#103,#104,#105,#106),$); /* Tag omitted */
```

The right-side offset widens quickly from −10 ft to −40 ft over the first 50 feet, then narrows to −20 ft at mid-curve, widens again to −30 ft, and finishes at −20 ft. The piecewise-linear profile of the offset distance is visible in the geometry of the resulting curve.

Both offset curves share the same basis curve `#20`. Each `IfcPointByDistanceExpression` also references `#20` directly, satisfying the requirement that the `BasisCurve` in `IfcOffsetCurveByDistances` and in its `OffsetValues` be the same curve object.

## 7.7 Interpolation of Offset Values

The IFC specification does not prescribe how offset values are to be interpolated between `IfcPointByDistanceExpression` entries. Several methods are possible:

* **Linear interpolation of offset values** — the lateral offset distance is interpolated linearly between consecutive offset points, and the interpolated distance is applied perpendicular to the basis curve at each chainage. This keeps the offset curve anchored to the basis curve geometry.
* **Linear interpolation between 3D points** — the 3D positions of consecutive offset points are computed and connected by straight line segments. This produces a true piecewise-linear curve in space, but one that drifts away from the basis curve between offset points.
* **Spline interpolation** — cubic spline, B-spline, Bézier, or NURBS methods applied to either the offset values or the 3D positions, producing smoother curves but with greater implementation complexity.

Different interpolation methods produce materially different geometry from the same `IfcOffsetCurveByDistances` data. Without a formal implementation agreement, two compliant applications may render the same model differently.

The recommended best practice is **linear interpolation of offset values**: interpolate the lateral distance at each chainage position, then apply that distance perpendicular to the basis curve. This method is the most natural given the structure of `IfcOffsetCurveByDistances`, produces predictable geometry, and is the least ambiguous for interchange.

## 7.8 The Tag Attribute

The `Tag` attribute of `IfcOffsetCurveByDistances` is an optional label that assigns an identifier to the offset curve. Its primary purpose is to correlate an offset curve with a named point in a variable cross-section definition.

`IfcSectionedSurface` and `IfcSectionedSolidHorizontal` define geometry by sweeping a series of cross-sections along a basis curve. Each cross-section can contain named control points — edge-of-pavement, top-of-rail, daylight line, and so on. The `Tag` on an `IfcOffsetCurveByDistances` matches one of those named points, allowing the surface or solid geometry to be driven by the offset curve's lateral positions rather than by fixed cross-section ordinates. This is the mechanism by which variable-width surfaces and solids are defined in IFC4x3.

The full treatment of `IfcSectionedSurface` and `IfcSectionedSolidHorizontal`, including how `Tag` values are resolved against cross-section geometry, is covered in Section 9.
