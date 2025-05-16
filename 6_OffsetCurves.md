# Section 6 - Offset Curves

Offset curves are very common in infrastructure geometry. Some examples
are:

- Edge of pavement

- Bridge girder centerlines

- Lane striping

`IfcOffsetCurveByDistance` defines the geometry of offset curves. It has
two attributes:

- BasisCurve : The curve from which offsets are measured

- OffsetValues: Defines the offsets along the curve

A single offset value indicates a constant offset over the entire length
of the curve.

If the offsets do not span the full length of the curve, the first and
last offset are implicitly continued to the head and tail of the basis
curve, respectively.

The `IfcOffsetCurveByDistance.OffsetValues` are of type
`IfcPointByDistanceExpression`. `IfcOffsetCurveByDistance.BasisCurve` and
`IfcPointByDistanceExpression.BasisCurve` must reference the same curve.
