# Section 7 - IfcReferent and Stationing

The class `IfcReferen`t defines a position at a particular offset along an
alignment curve. Stationing (also known as chainage) is a good example.

As an example, the Point of Curvature (PC) of a horizontal curve can be
located with an `IfcReferent`.

`IfcReferent.ObjectPlacement` = `IfcLinearPlacement`

`IfcLinearPlacement.Axis2PlacementLinear.Location` =
`IfcPointByDistanceExpression`

`IfcPointByDistanceExpression.DistanceAlong` =(distance from start of
alignment to the PC)

`IfcPointByDistanceExpression.BasisCurve` = `IfcCompositeCurve`
(representing horizontal alignment)

The `IfcReferent` can have a representation, so it has a visual presence in a
model viewer.
