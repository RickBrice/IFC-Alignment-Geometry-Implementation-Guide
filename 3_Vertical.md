# Section 3 - Vertical Alignment

## General

The parameter is distance along the alignment.

$L =$ Horizontal Length

$g_{s} =$ Start Gradient

$g_{e} =$ End Gradient

## Placement Matrix

Vertical alignment is evaluated in a "distance along, elevation" plane.
This is a 2D space. The "y" value is really an elevation, so we want
that value in the "z" position of the placement matrix. The slope of the
curve (RefDirection) is in the "distance along, elevation" plane. The
normal to the curve slope, in the general up direction, is the Axis
direction. Since we are in a 2D plane, the Y direction is (0,1,0,0). The
general positioning matrix for a point on the `IfcGradientCurve` is

$$M_{v} = \begin{bmatrix}
dx & 0 & - dy & d \\
0 & 1 & 0 & 0 \\
dy & 0 & dx & y \\
0 & 0 & 0 & 1
\end{bmatrix}$$

Matrix multiply horizontal and vertical to get placement in 3D. Note
however that $M_{h}$ has the X-Y plane coordinate. The "X" coordinate in
$M_{v}$ represents the "distance along" the horizontal alignment. If
this value is multiplied with (X,Y) in $M_{h}$, incorrect coordinates
will result. To remedy, revise $M_{v}$ by setting the $d$ value to 0.0
as follows

$${M'}_{v} = \begin{bmatrix}
dx & 0 & - dy & 0 \\
0 & 1 & 0 & 0 \\
dy & 0 & dx & y \\
0 & 0 & 0 & 1
\end{bmatrix}$$

The 3D position is computed from

$$M = M_{h}{M'}_{v}$$

Column 1 = RefDirection = Tangent to 3D curve, in the direction of the
curve

Column 2 = Y = RefDirection X Axis

Column 3 = Axis = "Up" direction that is orthogonal to RefDirection

Column 4 = Location = Point on 3D curve

Y = RefDirection CrossProduct (0,0,1)

Axis = Y CrossProduct RefDirection

## Constant Gradient

### Parent Curve Parametric Equations

$$x(s) = p_{x} + s$$

$$y(s) = p_{y} + s(dy/dx)$$

Note that these equations are different from the equations for
horizontal.

### Semantic Definition to Geometry Mapping

Mapping of the semantic definition of the linear segment to the
geometric definition is described with the following example.

Consider a vertical gradient at an uphill slope of 0.5 starting at point
(0,10). The horizontal projection of the segment length is 100.

~~~
#44 = IFCALIGNMENTVERTICALSEGMENT($, $, 0., 100., 10., 0.5, 0., $, .CONSTANTGRADIENT.);
~~~

Define the direction of the `IfcLine` so it matches the vertical segment

$$dx = \cos\left( \tan^{- 1}{0.5} \right) = 0.894427191$$

$$dy = \sin\left( \tan^{- 1}{0.5} \right) = 0.44713595$$

Define the `IfcLine` as passing through point (0,0)

~~~
#80 = IFCLINE(#81, #82);
#81 = IFCCARTESIANPOINT((0., 0.));
#82 = IFCVECTOR(#83, 1.);
#83 = IFCDIRECTION((0.894427190999916, 0.447213595499958));
~~~

Place the curve segment at (0,10) with a tangent direction
(0.894427190999916, 0.447213595499958).

~~~
#77 = IFCAXIS2PLACEMENT2D(#78, #79);
#78 = IFCCARTESIANPOINT((0., 10.));
#79 = IFCDIRECTION((0.894427190999916, 0.447213595499958));
~~~

`IfcCurveSegment.SegmentLength` is the length measured along the trimmed
curve. For a horizontal length of 100, the length along the curve is
100/0.894427190999916 = 111.803398874989

The curve segment is defined as

~~~
#71 = IFCCURVESEGMENT(.CONTINUOUS., #77, IFCLENGTHMEASURE(0.), IFCLENGTHMEASURE(111.803398874989), #80);
~~~

## Circular Arc

Vertical circular arcs are tricky. For vertical, the "distance along" is
a horizontal dimension. The parent curve equations need a distance along
the curve. The following procedure is used to convert the horizontal
distance, uh, to the arc length, u.

![](images/image10.emf)

The center point (Cx,Cy) is computed from (Sx,Sy) and the curve tangent
(tx,ty) at the start point.

Cx = Sx -- sign(length)\*ty\*R

Cy = Sy + sign(length)\*tx\*R

From the Dx-Dy-R triangle, $R^{2} = Dx^{2} + Dy^{2}$

Substitute $Dx = uh - (Cx - Sx)$ and $Dy = (Cy - y)$

$$R^{2} = (uh + Sx - Cx)^{2} + (Cy - y)^{2}$$

Solve for y

$$y = Cy - \sqrt{R^{2} - (uh + Sx - Cx)^{2}}$$

$uh = x - S_{x}$

$$y = Cy - \sqrt{R^{2} - (x - Cx)^{2}}$$

Compute the chord distance as the distance between the start point and
the point on the arc, c

$$c = \sqrt{(x - Sx)^{2} + (y - Sy)^{2}}$$

The chord distance is also $c = 2R\sin\frac{\mathrm{\Delta}}{2}$

Solve for $\mathrm{\Delta}$

$$\mathrm{\Delta} = 2\sin^{- 1}\frac{c}{2R}$$

Compute arc length, u

$$u = R\mathrm{\Delta}$$

The parent curve function can now be evaluated at u.

This calculation can be simplified because the point on the curve (x,y)
is computed. This is the point we want. The tangent direction at that
point is easily computed from the start tangent and the angle ∆.

:warning: **[Finish this]** :warning:

## Clothoid

:warning: **[Finish this]** :warning:

Start angle = atan(startGradient)

End angle = atan(endGradient)

Start radius = start radius of curvature

End radius = end radius of curvature

Set equal to horizontal length, adjust curve length until computed value
is equal to the specified horizontal length. Numerically solve ![](images/image11.png)

## Parabolic Arc

:warning: **[Finish this] -- need to show how to compute curve length given
horizontal length like for parabolic vertical curves** :warning:

A = start height

B = start gradient

C = (end gradient -- start gradient)/(2\*horizontal length)

Parent curve is `IfcPolynomialCurve`

Position = `IfcAxis2Placement2D.Location`=0,0,RefDirection=1,0

CoefficientsX = (0,1)

CoefficientsY=(A,B,C)

:warning: **[THERE COULD BE A PROBLEM WITH THE Y-COEFFICIENTS. THE ARE SUPPOSED TO
BE REAL VALUES]** :warning:

Compute segment curve length from $s = \int_{}^{}\sqrt{y^{'2} + 1}dx$

![](images/image12.png)

`IfcCurveSegment`

.Placement = `IfcAxis2Placement2D.Location`=(start distance along, start
height).RefDirection=`IfcDirection(1,0)`

.SegmentStart=0.0,

SegmentLength = s
