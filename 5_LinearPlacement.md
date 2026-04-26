# Section 5 - Linear Placement

outline: 
* describe the concept of object placement in ifc.
* introduct the idea of linear placement for horizontal construction projects. describe locating a bridge poer on an alignment using 2D like fron traditional plans and then a drain inlet in 3d with station, offset and elevation. add a figure to illustrate.
* discuss how linear placement is accomplished with ifc. this will include distance along diretrix with explaination of stationing which is covered in a different section, lateral and vertical offset, longitudinal offset for otherwise unreachable point (include a figure to illustrate), and the placement coordinate system with discussion of uncertaintly frim the spec on default axis and refdirection.
* discuss linear placement along ifcoffsetcurvebydistances
* review the iso 19148 on linear placement to see if there is other important concepts to discuss. one could be milepost system compared to stationing. see https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/Pset_LinearReferencingMethod.htm.

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

The most logical default `Axis` is "perpendicular" to the `RefDirection` in the general direction of global Z-axis. However, the most common interpetation is that `Axis` is up (0,0,1). 

When `Axis` and `RefDirection` are not provided, the local coordinate system can be computed as follows:

1. Set Axis = Z = (0,0,1)
2. Compute the tangent vector to the 3D curve. This is the RefDirection.
3. Y = cross product of Z and RefDirection.
4. X = cross product of Y and Z.

X, Y, Z are orthoginal axes.

## Linear Placement along IfcOffsetCurveByDistances

Linear placement along an `IfcOffsetCurveByDistances` is not precise. `IfcOffsetCurveByDistances` is an interpoloated curve defined by offsets from a basis curve. The offset values are linearly interpolated forming a segmented curve. The length of the offset curve is approximate and depends on the frequency of the interpoloated points along the curve. For this reason, `IfcAxis2PlacementLinear.Location.DistanceAlong` cannot be precisely determined.
