# Section 7 - Linear Placement

Many elements in the built environment for infrastructure works are
located relative to an alignment. The IFC class `IfcLinearPlacement`
accomplishes this type of object placement.

Generally alignments are place in the project coordinate system so they are relative to (0,0). To indicate that a linear placement is relative to the alignment, the `PlacementRelTo` attribute is omitted indicating that the placement is relative to the start of the basis curve of the alignment.

The `IfcLinearPlacement.RelativePlacement` attribute places an object.
RelativePlacement is an `IfcAxis2PlacementLinear`.

`IfcAxis2PlacementLinear.Location` is an `IfcPoint`, but is constrained to
be an `IfcPointByDistanceExpression` by a where rule. This means that the
placement location is measured along the basis curve. For a 3D alignment
curve such as `IfcGradientCurve` or `IfcSegmentedReferenceCurve`, the basis
curve is `IfcCompositeCurve` representing the projection of the 3D curve
onto a 2D horizontal plane.

## General

`IfcAxis2PlacementLinear` has optional `Axis` and `RefDirection` attributes.
When omitted, `RefDirection` is the tangent to the 3D curve at Location.

Unfortunately, `Axis` is not clearly defined in the IFC schema
documentation (See [Default value for `IfcAxis2PlacementLinear.Axis` is
not defined · Issue #125 ·
buildingSMART/IFC4.x-IF](https://github.com/buildingSMART/IFC4.x-IF/issues/125)).

The most logical default `Axis` is "perpendicular" to the `RefDirection` in
the general direction of global Z-axis. This can be computed as follows:

1.  From the horizontal projection of the 3D curve, compute tangent
    vector.

2.  Compute Y from cross product of this tangent vector and (0,0,1)

3.  Axis = cross product of Y and RefDirection.

## Linear Placement along IfcOffsetCurveByDistances

Linear placement along an `IfcOffsetCurveByDistances` is not precise. `IfcOffsetCurveByDistances` is an interpoloated curve defined by offsets from a basis curve. The offset values are linearly  interpolated forming a segmented curve. The length of the offset curve is approximate and depends on the frequency of the interpoloated points along the curve. For this reason, `IfcAxis2PlacementLinear.Location.DistanceAlong` cannot be precisely determined.