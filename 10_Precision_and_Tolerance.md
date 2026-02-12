# Section 10 - Precision and Tolerance

`IfcCurveSegment.Transition` defines the intended transition from the end
of one segment to the start of the next. The options are:

CONTINUOUS: The segments joint but no condition on their tangents is
implied

CONTSAMEGRADIENT: The segments join and their tangent vectors or tangent
planes are parallel and have the same direction at the joint; equality
of derivative is not required

CONSTSAMEGRADIENTSAMECURVATURE: For a curve, the segments join, their
tangent vectors are parallel and in the same direction and their
curvatures are equal at the joint: equality of derivatives is not
required. For a surface this implies that the principle curvatures are
the same and the principle directions are coincident along the common
boundary.

DISCONTINUOUS: The segments do not join. This is permitted only at the
boundary of the curve or surface to indicate that it is not closed.

For a variety of reasons, adjacent segment start and end points might
not exactly line up in position, gradient, or curvature.

While not officially determined yet, `Pset_Tolerance` is used to indicate
the acceptable tolerance under which the calculated end point of a
preceding segment would be considered geometrically continuous with the
provided start point of the following segment. Similarly,
Pset_Uncertainty is used to indicate the uncertainty inherent in
historical information gleaned from plan sets and other historic
sources. As a fallback if `Pset_Tolerance` is not provided, tolerances can
be taken from `IfcGeometricRepresentationContext.Precision`.
