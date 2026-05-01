outline:
* describe cant in terms of it being a deviation to railroad alignment vertical in curves. it provides for track banking
* need figure the show cross slope and coordinate system 3D and 2-2D elevation and section.
* need figure that shows centerline and railhead deviation
* reference british standard (BS EN 13803:2017 Railway applications - Track - Track alignment design parameters - Track gauges 1 435 mm and wider, Table C.1 "C:\Users\BriceR\OneDrive - Washington State Department of Transportation\BIM for Bridges\Rail Spec\bs-en-13803-2017.pdf") and describe the equivalent functional form of equations used for horizontal. The form of the horizontal transition spirals equations is the same form as the cant equation.
* Equivalance of functional form - state that the derivative of $\theta(t)$ equation, which is the curvature $\kappa(t)$, for horizontal has the same form as the $\frac{D(t)}{L^2}$ equation for cant.
* Need to add a general discussion about the spiral coefficients. This is the text used in some sections - it doesn't need to be repeated everywhere. "The polynomial coefficients must have units of length. The basic form of the coefficient of the $i^{th}$ term is $A_{i} = \frac{L^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{\left| a_{i} \right|}}\frac{a_{i}}{\left| a_{i} \right|}$"
* horizontal and cant always use the same curve type, though technically ifc would permit mixing them
* provide a bit more discussion in the examples. reference the example files
* need to discuss cross slope, Axis vector, and their orientation and relation to one another. Axis is normal to cross slope line. $\phi(s) = \phi_s + \left(\frac{\phi_e - \phi_s}{D_e - D_s}\right)\bigl(D(s) - D_s\bigr)$. Should this equation use $\Delta D$?
* state up front that the railhead distance for all examples is 1.5 m, so we don't have to keep restating this


# Section 4.0 - Cant Alignment

Cant (also called superelevation) is the transverse inclination of a railway track cross-section: the elevation difference between the two railheads when one rail is raised above the other. By tilting the track into a curve, cant directs a component of gravitational force inward, partially offsetting the centrifugal acceleration experienced by vehicles negotiating the curve. The result is improved ride quality, reduced wheel–rail lateral forces, and the ability to operate at higher speeds through curves without exceeding comfort or safety limits.

Cant is measured as a length — the height difference between railheads — rather than as an angle. The conversion between the two depends on track gauge. `IfcAlignmentCant.RailHeadDistance` supplies the centre-to-centre distance between railheads, which is the lever arm for this conversion.

## 4.1 General
An `IfcSegmentedReferenceCurve` describes the cross slope of superelevated rail lines as a track banks through curves. When the point of rotation is about one of the railheads, the alignment elevation must deviate to accomodate the cross slope. 

An `IfcSegmentedReferenceCurve` also describes this deviation in elevation. As a subtype of `IfcCompositeCurve`, an `IfcSegmentedReferenceCurve` consists of an end to start collection of `IfcCurveSegment`. An `IfcSegmentedReferenceCurve` also has a `BasisCurve` which is typically an `IfcGradientCurve`.

The `IfcCurveSegment.ParentCurve` defines the change in cross
slope between rail heads over the length of the segment. When the
`IfcCurveSegment.Placement.Location` differs from the
`IfcCurveSegment.Placement.Location` of the next segment, the
`IfcCurveSegment.ParentCurve` also defines variation in the deviating elevation. If the
`IfcCurveSegment.Placement.Location` is the same as for the start of the
next segment, the deviating elevation along the length of the segment is
constant.

Table 4.1-1 maps each `IfcAlignmentCant.PredefinedType` to its corresponding parent curve type.

  Business Logic (`IfcAlignmentCant.PredefinedType`) | Geometric Representation (`IfcCurveSegment.ParentCurve`)
  -----------------------------------------|-----------------------------------
  CONSTANTCANT                             |`IfcLine`
  LINEARTRANSITION                         |`IfcClothoid`
  HELMERTCURVE                             |`IfcSecondOrderPolynomialSpiral`
  BLOSSCURVE                               |`IfcThirdOrderPolynomialSpiral`
  COSINECURVE                              |`IfcCosineSpiral`
  SINECURVE                                |`IfcSineSpiral`
  VIENNESEBEND                             |`IfcSeventhOrderPolynomialSpiral`

  *Table 4.1-1 — Mapping of business logic to geometric representation for cant alignment*


The transition functions used to shape cant variation have the same functional form as functions used for horizontal transition curves: clothoid (linear cant), Helmert, Bloss, cosine, sine, and Viennese bend. In practice, the cant transition type always matches the horizontal transition type, though IFC does not enforce this constraint.

As an example, the radius of curvature for a Helmert curve is a second order polynomial of the form


$$\theta(t) = \frac{t^{3}}{3A_{2}^{3}} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}t^{2} + \frac{t}{A_{0}}$$

$$\kappa(t) = \frac{\theta(t)}{dt} = \frac{1}{A_{2}^{3}}t^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}t + \frac{1}{A_{0}}$$

The cant deviating elevation is of the form

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

The deviating elevation has the same functional form as the radius of curvature of the horizontal alignment segment. 

In IFC, the semantic cant profile is encoded in `IfcAlignmentCant` and its child `IfcAlignmentCantSegment` entities. The geometric representation is an `IfcSegmentedReferenceCurve`, which evaluates the cant at every point along the alignment and, in conjunction with the horizontal alignment `IfcCompositeCurve` and the vertical alignment `IfcGradientCurve`, produces the full 3D track centerline geometry.

[todo: add a figure to illustrate the cross slope and centerline elevation deviation] 

Each `IfcCurveSegment` in an `IfcSegmentedReferenceCurve` is evaluated in a two-dimensional coordinate system whose axes are *distance along the horizontal alignment* $d$ and *deviating elevation* $D$. The deviating elevation is the vertical offset applied to the track centerline, away from the gradient curve, to produce the correct cross-slope angle at every point along the segment.

The `StartCantLeft` $D_{sl}$, `EndCantLeft` $D_{el}$, `StartCantRight` $D_{sr}$, and `EndCantRight` $D_{el}$ attributes of `IfcAlignmentCantSegment` determine $D_s$ and $D_e$ as the averages of their respective left and right values:

$$D_s = \frac{D_{sl} + D_{sr}}{2}, \quad D_e = \frac{D_{el} + D_{er}}{2}$$

The cross-slope angle $\phi$ at a given point is not obtained directly from the parent curve equation; instead it is interpolated between the start and end cross-slope angles encoded in the `Axis` vectors of the `IfcCurveSegment.Placement`, using the deviating elevation as the interpolation parameter:

$$\phi(s) = \phi_s + \left(\frac{\phi_e - \phi_s}{\Delta D}\right)\bigl(D(s) - D_s\bigr)$$

where $\phi_s$ and $\phi_e$ are the cross-slope angles at the start and end of the segment and $D_s$ and $D_e$ are the corresponding deviating elevations. $\Delta D = D_e - D_s$, and $D(s)$ is the deviation elevation at $s$. The `Axis` vector at any point is $(0,\ \cos\phi(s),\ \sin\phi(s))$. The `Axis` vector is perpendicular to a line connecting the railheads in an upwards direction. The cross-slope angle $\phi$ is the angle from the transverse $y$ axis to the `Axis` vector. In sections without cant, `Axis` is (0,0,1) and $\phi = \frac{\pi}{2}$.

Together, the distance along, the deviating elevation $D(s)$, and the cross-slope angle $\phi(s)$ fully specify a 3D placement frame for the track centerline at each arc-length $s$. Section 4.2 describes an algorithm for constructing that frame and composing it with the horizontal and vertical matrices to produce a 3D position.

## 4.2 Curve Segment Evaluation Algorithm

Cant segments are evaluated in a two-dimensional "distance along, deviating elevation" coordinate system in which $x(s) = d$ is the distance measured along the horizontal `IfcCompositeCurve` and $y(s) = D(s)$ is the deviating elevation: the vertical offset applied to the track centerline to accommodate the cross slope. Unlike horizontal and vertical segments, each cant point also carries a cross slope angle $\phi$, making the local frame inherently three-dimensional.

**Steps 1—4** follow the identical procedure describe in Section 2.2 for horizontal segments, substituting distance along for the horizontal $x$-coordinate and deviating elevation for the horizontal y-coordinate. Let $s_0 = $ `IfcAlignmentCantSegment.StartDistAlong`.

**Step 1 — Evaluate the parent curve at the trim start**

Compute the deviating elevation $z_0 = D_0 = D(s_0)$ and the slope angle $\theta_0 = \tan^{-1}(D'(s_0))$. $d_0 = x(s_0)$ is the distance along the parent curve at the trim start.

**Step 2 — Form the normalization matrix $M_N$**

$M_N$ simultaneously translates the trim-start point to the origin and rotates so that the tangent at $s_0$ aligns with the positive $x$-direction.

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -d_0\cos\theta_0 - z_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -d_0\sin\theta_0 - z_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$M_{CSP}$ is constructed from `IfcCurveSegment.Placement`: $(d_p, D_p)$ is the `Location` (distance along, deviating elevation), the `RefDirection` gives slope angle $\theta_p$, and the `Axis` gives cross slope angle $\phi_p$.

$$\mathbf{RefDir}_p = (\cos\theta_p,\ \sin\theta_p,\ 0),\quad \mathbf{Axis}_p = (0,\ \cos\phi_p,\ \sin\phi_p)$$
$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p,\quad \mathbf{X}_p = \mathbf{Axis}_p \times \mathbf{Y}_p$$

The placement in matrix form is

$$M_{CSP} = \begin{bmatrix} 
X_p.x & Y_p.x & Axis_p.x & d_p \\
X_p.y & Y_p.y & Axis_p.y & 0 \\
X_p.z & Y_p.z & Axis_p.z & D_p \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 — Evaluate and map each point**

For the point at a distance along the horizontal alignment $s$, compute $D(s)$ and $\theta(s) = \tan^{-1}(D'(s))$. Interpolate the cross slope angle between the segment start and end values:

$$\phi(s) = \phi_s + \left(\frac{\phi_e - \phi_s}{\Delta D}\right)(D(s) - D_s)$$

Form the local frame:

$$\mathbf{X} = (\cos\theta(s),\ \sin\theta(s),\ 0),\quad \mathbf{Z} = (0,\ \cos\phi,\ \sin\phi)$$
$$\mathbf{Y} = \mathbf{Z} \times \mathbf{X},\quad \mathbf{Axis} = \mathbf{X} \times \mathbf{Y}$$

$$M_{PC} = \begin{bmatrix}
X.x & Y.x & Axis.x & d \\
X.y & Y.y & Axis.y & 0 \\
X.z & Y.z & Axis.z & D(s) \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

where $d = x(s)$ is the distance along the horizontal alignment at arc-length $s$.

Apply the normalization and placement in sequence:

$$M_c = M_{CSP}\ M_N\ M_{PC}$$

Column 4 of $M_c$ is $(d,\ 0,\ D)$ — the distance along and deviating elevation. Column 3 (Axis) is the cross-slope direction at that point. Step 5 is performed immediately for this point before moving to the next arc-length $s$.

**Step 5 — Combine with horizontal and vertical to produce the 3D placement matrix**

The cant result must be combined with the horizontal matrix $M_h$ (evaluated at distance $s$ along the `IfcCompositeCurve`) and the vertical matrix $M_v$ (evaluated at the same $s$). All three coordinate systems share the distance-along axis, so the positional components of $M_v$ and $M_c$ must be extracted before multiplication and added back afterward to avoid incorrectly rotating the position offsets.

Construct $M'_v$ as described in Section 3.2.

Construct $M'_c$ by zeroing the distance-along component in column 4 of $M_c$:

$${M'}_c = \begin{bmatrix} 
X.x & Y.x & Axis.x & 0 \\ 
X.y & Y.y & Axis.y & 0 \\ 
X.z & Y.z & Axis.z & D \\ 
0 & 0 & 0 & 1 
\end{bmatrix}$$

Extract position vectors from each modified matrix (setting row 4 to zero), then zero column 4 before multiplying:

$$P_v = M'_v \text{ column 4, row 4 set to 0} = \begin{bmatrix} 0 \\ 0 \\ z \\ 0 \end{bmatrix}, \qquad P_c = M'_c \text{ column 4, row 4 set to 0} = \begin{bmatrix} 0 \\ 0 \\ D \\ 0 \end{bmatrix}$$

$$M''_v = M'_v \text{ with column 4 set to } (0,0,0,1)^T, \qquad M''_c = M'_c \text{ with column 4 set to } (0,0,0,1)^T$$

Multiply the three orientation matrices, then add back both position offsets:

$$M' = M_h \cdot M''_v \cdot M''_c$$

$$M_{3Dcant} = M' + 
\begin{bmatrix} 
0 & 0 & 0 & P_{v.x} \\
 0 & 0 & 0 & P_{v.y} \\ 
 0 & 0 & 0 & P_{v.z} \\ 
 0 & 0 & 0 & 0 
 \end{bmatrix} 
 + 
 \begin{bmatrix} 
 0 & 0 & 0 & P_{c.x} \\
  0 & 0 & 0 & P_{c.y} \\
   0 & 0 & 0 & P_{c.z} \\ 
   0 & 0 & 0 & 0 
   \end{bmatrix}$$

Column 4 of the final matrix $M_{3Dcant}$ is the full 3D position of the track centerline. Column 3 is the cross-slope direction, encoding the railhead superelevation at that point.


## 4.3 Constant Cant

Cant has a constant deviating elevation and cross-slope angle in rail segments between curves or in the circular portion of curves where the tracks are banked at a constant rate.

The parent curve is `IfcLine`. The slope-intercept form of a line is $y = mx + b$, where $m$ is the slope and $b$ is the $y$-intercept. The derivative is $y' = m$, and the second derivative is $y''= 0$.

In the context of cant, $D(s) = y'(x)$, so the deviating elevation is a constant value, $m$, and the rate of change of the deviating elevation $D'(s) = y''(x) = 0$.

### 4.3.3 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$D(s) = D_s = D_e$$

$$\frac{d}{ds}D(s) = 0.0$$

### 4.3.2 Semanic Definition to Geometry Mapping

Consider 100 m long segment of a railway that is turning towards the left. The right rail is raised 0.16 m through the circular portion of the curve. The sementic definition is

~~~
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 1.6E-1, 1.6E-1, .CONSTANTCANT.);
~~~

$D_s = \frac{0.0\ m + 0.16\ m}{2} = 0.08\ m \quad D_e = \frac{0.0\ m + 0.16\ m}{2} = 0.08\ m$

$\Delta D = D_e - D_s = 0.08\ m - 0.08\ m = 0.0\ m$

The parent curve has a constant elevation at $0.08\ m$ and a slope of $0.0$.

Define the parent curve as an `IfcLine` passing through (0,0.08) in the direction (1,0).

~~~
#123 = IFCLINE(#124, #125);
#124 = IFCCARTESIANPOINT((0., 0.08));
#125 = IFCVECTOR(#126, 1.);
#126 = IFCDIRECTION((1., 0.));
~~~

The `IfcCurveSegment` trims a segment from the parent curve. The curve segment placement must capture the cross-slope rotation between the rail heads. For this reason the placement is an `IfcAxis2Placement3D` (instead of `IfcAxis2Placement2D` used for horizontal and vertical representations).

The cross-slope angle is $\phi = tan^{-1}\left(\frac{\Delta D}{D_{rh}}\right)$, where $D_{rh}$ is the rail head distance, $1.5\ m$.

$\phi = tan^{-1}\left(\frac{0.08}{1.5}\right) = 0.05328285$

$dz_y = sin\phi = sin(0.05328285) = 0.0532576$

$dz_z = cos\phi = cos(0.05328285) = 0.9985808$

~~~
#113 = IFCCURVESEGMENT(.CONTINUOUS., #119, IFCLENGTHMEASURE(0.), IFCLENGTHMEASURE(100.), #123);
#119 = IFCAXIS2PLACEMENT3D(#120, #121, #122);
#120 = IFCCARTESIANPOINT((0., 0.08, 0.));
#121 = IFCDIRECTION((0.,  0.0532576, 0.9985808));
#122 = IFCDIRECTION((1., 0., 0.));
~~~

### 4.3.2 Compute Point on Curve

Compute the placement matrix for a point $s = 50\ m$ from the start of the curve segment.

**Step 1 - Evaluate the parent curve at the trim start**

$s_0 = 0, D(0) = 0.08\ m, D'(0) = 0.$

$\phi(0) = tan^{-1}\left(\frac{0.9985808}{0.0532576}\right) = 1.517513518$

**Step 2 - Form the normalization matrix $M_N$**

$$\mathbf{X}_0 = (1,\ 0,\ 0),\quad \mathbf{Z}_0 = (0,\ 0.0532576,\ 0.9985808)$$
$$\mathbf{Y}_0 = \mathbf{Z}_0 \times \mathbf{X}_0,\quad \mathbf{Axis}_0 = \mathbf{X}_0 \times \mathbf{Y}_0$$

$$\mathbf{Y}_0 = (0,\ 0.9985808,\ -0.0532576)$$

$$\mathbf{Axis}_0 = (0,\ 0.0532576,\ 0.9985808)$$

$$M_N = \begin{bmatrix}
1 & 0 & 0 & 0 \\
 0 & 0.9985808 & -0.0532576 & 0 \\ 
 0 & 0.0532576 & 0.9985808 & -0.08 \\
  0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 3 - Form the curve segment placement matrix $M_{CSP}$**

$$\mathbf{RefDir}_p = (1,\ 0,\ 0),\quad \mathbf{Axis}_p = (0,\ 0.0532576,\ 0.9985808)$$
$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ 0.0532576,\ 0.9985808),\quad \mathbf{X}_p = \mathbf{Axis}_p \times \mathbf{Y}_p = (1,\ 0,\ 0)$$

$$M_{CSP} = \begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.9985808 & 0.0532576 & 0 \\
0 & 0.0532576 & 0.9985808 & 0.08 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 - Evaluate and map each point**

$$M_{PC} = \begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 0.9985808 & 0.0532576 & 0 \\
0 & 0.0532576 & 0.9985808 & 0.08 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

$$M_c = M_{CSP}\, M_N\, M_{PC}$$

$$M_c =
\begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.9985808 & 0.0532576 & 0 \\
0 & 0.0532576 & 0.9985808 & 0.08 \\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
 0 & 0.9985808 & -0.0532576 & 0 \\ 
 0 & 0.0532576 & 0.9985808 & -0.08 \\
  0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 0.9985808 & 0.0532576 & 0 \\
0 & 0.0532576 & 0.9985808 & 0.08 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

$$M_c = \begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 0.9985808 & 0.0532576 & 0 \\
0 & 0.0532576 & 0.9985808 & 0.08 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

## 4.4 Linear Transition

A linear transition in cant is represented with an `IfcClothoid`.

### 4.4.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s\ $$

$$\frac{d}{ds}D(s) = L^{2}\frac{A_{1}}{\left| A_{1}^{3} \right|}$$

$$a_{0} = D_{s},\ A_{0} = \frac{L^{2/1}}{\sqrt[1]a_{0}}\frac{a_0}{\left|a_0\right|},\ A_{0} = \frac{L^{2}}{a_{0}}$$

$$a_1 = \Delta D,\ A_1 = \frac{L^{\frac{3}{2}}}{\sqrt{\left| a_{1} \right|}}\frac{a_{1}}{\left| a_{1} \right|}$$

$A_1$ is the clothoid constant.

### 4.4.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a clothoid transition curve towards the left. The track banks at a constant rate resulting in a linearly deviating elevation between the rail heads. The rail head separation is 1.5 m and the cant is 160 mm.

The semantic representation of the cant alignment is

~~~
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 0.16, 0., .LINEARTRANSITION.);
~~~

Compute the parent curve parameters.

$D_{sl} = 0\ m\quad D_{el} = 0\ m$

$D_{sr} = 0.16\ m\quad D_{er} = 0\ m$

$D_s = \frac{(0.16 + 0\ m)}{2} = 0.08\ m$

$D_e = \frac{(0 + 0)}{2} = 0\ m$

$\Delta D = D_e - D_s = 0.0 - 0.08 = -0.08\ m$

$a_0 = D_s = 0.08\ m,\ A_0 = \frac{(100\ m)^2}{0.08\ m} = 125000\ m$

$a_{1} = \Delta D = -0.08\ m \quad A_{1} = \frac{{(100\ m)}^{\frac{3}{2}}}{\sqrt{|-0.08\ m|}}\frac{-0.08\ m}{|-0.08\ m|} = -3535.533906\ m$

The clothoid parent curve is

~~~
#95=IFCCARTESIANPOINT((0.,0.));
#96=IFCDIRECTION((1.,0.));
#97=IFCAXIS2PLACEMENT2D(#95,#96);
#98=IFCCLOTHOID(#97,-3535.53390593274);
~~~

The cant segment begins with a deviating elevation of $D_s = 0.08\ m$.
$y = d = 0.08$

The slope of the cant curve is $\frac{\Delta D}{L} = \frac{-0.08}{100} = -0.0008$.

$\theta = tan^{-1}(-0.0008) = -0.0007999998$

$dx_x = cos(-0.0007999998) = 0.9999996800$

$dy_x = sin(-0.0007999998) = -0.0007999997$

The cross-slope at the start of the segment is

$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.16 - 0.0}\right) = 1.464531464$

The cross slope orientation is

$dy_z = cos(\phi_s) = cos(1.464531464) = 0.106064981$

$dz_z = sin(\phi_s) = sin(1.464531464) = 0.994359201$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.106064981,0.994359201));
#102=IFCDIRECTION((0.9999996800,-0.0007999997,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.4.3 Compute Point on Curve

Compute the cant placement matrix for a point 50 m from the start of the curve segment.

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve 

$s_0 = 0,\ x(s_0) = 0, \ y(s_0) = 0,\ dx_0 = 1,\ dy_0 = 0,\ \theta_0 = 0$

**Step 2 — Form the normalization matrix $M_N$**

Since $x(s_0) = 0, \ y(s_0) = 0,\ \theta_0 = 0, M_N = I$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir}_p = (0.9999996800,-0.0007999997,0.),\ \mathbf{Axis}_p = (0.,0.106064981,0.994359201)$

$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0.0007954871, 0.9943588828, -0.1060649471)$

$$M_{CSP} = \begin{bmatrix} 
0.9999996800 & 0.0007954871 & 0 & 0 \\
-0.0007999997 & 0.9943588828 & 0.106064981 & 0.08 \\
0 & -0.1060649471 & 0.994359201 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

The $\mathbf{\text{Axis}}$ vector is perpendicular to the railhead cross slope line.

$\mathbf{\text{Axis}} = (0.0,\ 0.106064981,\ 0.994359201)$

$\phi_p = tan^{-1}\left(\frac{0.994359201}{0.106064981}\right) = 1.464531464$

With $y$ to the left and $z$ upwards, the vector is nearly vertical, pointing slightly to the left. This is consistent with a curve to the left and the right railhead being superelevated.

**Step 4 — Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$

$D(50\ m) = (100\ m)^{2}\left( \frac{1}{125000\ m} + \frac{(-3535.533906\ m)}{\left| (-3535.533906\ m)^{3} \right|}(50\ m) \right) = 0.04\ m$

$M_{PC} = \begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 1 & 0 & -0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$

$M_c = M_{CSP}M_N M_{PC}$

$M_c = 
\begin{bmatrix}
0.999999680000 & 0.0007988711 & 0.0000424859 & 0 \\
-0.000800000085 & 0.9985884845 & 0.053107402 & 0.08 \\
0 & -0.053107419 & 0.9985882289 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix} I \end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 50 \\
0 & 1 & 0 & -0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
$

$M_c = \begin{bmatrix}
0.9999996836000798 & 0.0007955209455802008 & 0.0 & 50.0 \\
-0.0007909999255054242 & 0.9985884897861665 & 0.05310743567896648 & 0.04 \\
0.0 & -0.05310740211832019 & 0.9985888044014736 & 0.0 \\
0.0 & 0.0 & 0.0 & 1.0
\end{bmatrix}$

$\mathbf{\text{Axis}} = (0.0,\ 0.05310743567896648,\ 0.9985888044014736)$

$\phi(50\ m) = tan^{-1}\left(\frac{0.9985888044014736}{0.05310743567896648}\right) = 1.517663895$

The $\mathbf{\text{Axis}}$ vector is closer to vertical half way through the cant segment. At the end of the cant segment, $\mathbf{\text{Axis}}$ will be $\frac{\pi}{2}$.

As a quick check, the $\mathbf{\text{Axis}}$ direction vector half way through the cant segment should be the average value. $\frac{1.464531464+\frac{\pi}{2}}{2} = 1.517663895$

## 4.5 Helmert Curve

Like the Helmert transition spiral, the Helmert cant sementic definition maps to two `IfcCurveSegment` instances for the geometric representation. The parent curve is `IfcSecondOrderPolynomialSpiral`.

### 4.5.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{2s}{A_{2}^{3}} + \frac{A_{1}}{\left| A_{1}^{3} \right|} \right)$$

The polynomial coefficietions carry a second subscript to indicate first half $1$, and second half $2$. For example, $A_{21}$ is coefficient $A_2$ for the first half and $A_{32}$ is coefficient $A_3$ for the second half. **[todo: add this description to 2_Horizonta.md]**

In the first half of the cant transition

Constant Term:

 $a_{01} = 4D_{s}$,
$A_{01} = \frac{L^{2}}{\left| a_{o1} \right|}\frac{a_{01}}{\left| a_{o1} \right|}$

Linear Term: 

$a_{11} = 0$,
$A_{11} = \frac{L^{\frac{3}{2}}}{\sqrt{\left| a_{11} \right|}}\frac{a_{11}}{\left| a_{11} \right|} = 0$

Quadratic Term:

$a_{21} = 8f$,
$A_{21} = \frac{L^{4\text{/}3}}{\sqrt[3]{\left| a_{21} \right|}}\frac{a_{21}}{\left| a_{21} \right|}$

In the second half

Constant Term: 

$a_{02} = -4f + 4D_{s}$,
$A_{02} = \frac{L^{2}}{\left| a_{02} \right|}\frac{a_{01}}{\left| a_{02} \right|}$

Linear Term: 

$a_{12} = 16f$,
$A_{12} = \frac{L^{\frac{3}{2}}}{\sqrt{\left| a_{12} \right|}}\frac{a_{12}}{\left| a_{12} \right|}$

Quadratic Term: 

$a_{22} = -8f$,
$A_{22} = \frac{L^{\frac{4}{3}}}{\sqrt[3]{\left| a_{22} \right|}}\frac{a_{22}}{\left| a_{22} \right|}$


### 4.5.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a Helmert transition curve towards the left. The start cant is $0.08\ m$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.HELMERTCURVE.);
~~~

Compute the parent curve parameters

$$L = 100\ m$$

$$D_{sl} = 0\ m,\ D_{el} = 0\ m$$

$$D_{sr} = 0.16\ m,\ D_{er} = 0\ m$$

$$D_{s} = \frac{0 + 0.16\ m}{2} = 0.08\ m$$

$$D_{e} = \frac{0 + 0}{2} = 0.\ m$$

$$\Delta D = 0.0 - 0.08 = -0.08\ m$$

$$f = \Delta D = -0.08\ m$$

First half:

$$a_{01} = 4D_{s} = 4(0.08\ m) = 0.32\ m$$

$$A_{01} = \frac{L^{2}}{\left| a_{o1} \right|}\frac{a_{01}}{\left| a_{o1} \right|} = \frac{(100\ m)^{2}}{|0.32\ m|}\frac{0.32\ m}{|0.32\ m|} = 31250\ m$$

$$a_{11} = 0,\ A_{11} = 0$$

$$a_{21} = 8f = 8(-0.08\ m) = -0.64\ m$$

$$A_{21} = \frac{L^{4\text{/}3}}{\sqrt[3]{\left| a_{21} \right|}}\frac{a_{21}}{\left| a_{21} \right|} = \frac{(100\ m)^\frac{4}{3}}{\sqrt[3]{| - 0.64\ m|}}\frac{-0.64\ m}{|-0.64\ m|} = -538.6086725\ m$$

The first half parent curve `IfcSecondOrderPolynomialSpiral` is
~~~
#104=IFCCARTESIANPOINT((0.,0.));
#105=IFCDIRECTION((1.,0.));
#106=IFCAXIS2PLACEMENT2D(#104,#105);
#107=IFCSECONDORDERPOLYNOMIALSPIRAL(#106,-538.60867250797071,$,31250.);
~~~

Determine the first half placement and trimming.

Note that the length of the first half curve is $L_1 =50\ m$, half the length of the full Helmert transition. **[Need to do a better job explaining why L/2 when A is computed on full L]**

The deviation elevation at the start of the first half transition is

$D(0\ m) = (50\ m)^{2}\left( \frac{1}{31250\ m} + \frac{1}{(-538.6086725\ m)^{3}}(0\ m)^{2} \right) = 0.08\ m$

The slope at $0\ m$ is $0.0$. $dx_x = 1.0,\ dx_y = 0.0$

The cross slope is 

$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.16 - 0.0}\right) = 1.464531464$

$dy_z = cos(\phi_s) = cos(1.464531464) = 0.106064981$

$dz_z = sin(\phi_s) = sin(1.464531464) = 0.994359201$

~~~
#108=IFCCARTESIANPOINT((0.,0.08,0.));
#109=IFCDIRECTION((0.,0.10606498139220574,0.99435920055192883));
#110=IFCDIRECTION((1.,0.,0.));
#111=IFCAXIS2PLACEMENT3D(#108,#109,#110);
#112=IFCCURVESEGMENT(.CONTINUOUS.,#111,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(50.),#107);
~~~

Second half:

$$a_{02} = -4f + 4D_{s} = -4(-0.08\ m) + 4(0.08)\ m = 0.64\ m$$

$$A_{02} = \frac{L^{2}}{\left| a_{02} \right|}\frac{a_{01}}{\left| a_{02} \right|} = \frac{(100\ m)^{2}}{|0.64\ m|}\frac{0.64\ m}{|0.64\ m|} = 15625\ m$$

$$a_{12} = 16f = 16(-0.08\ m) = -1.28\ m$$
$$A_{12} = \frac{L^{\frac{3}{2}}}{\sqrt{\left| a_{12} \right|}}\frac{a_{12}}{\left| a_{12} \right|} = \frac{(100\ m)^{\frac{3}{2}}}{\sqrt{|-1.28\ m|}}\frac{-1.28\ m}{|-1.28\ m|} = -883.8834765\ m$$

$$a_{22} = -8f = -8(-0.08\ m) = 0.64\ m$$

$$A_{22} = \frac{L^{\frac{4}{3}}}{\sqrt[3]{\left| a_{22} \right|}}\frac{a_{22}}{\left| a_{22} \right|} = \frac{(100\ m)^{\frac{4}{3}}}{\sqrt[3]{|0.64\ m|}}\frac{0.64\ m}{|0.64\ m|} = 538.6086725\ m$$

The second half parent curve `IfcSecondOrderPolynomialSpiral` is
~~~
#113=IFCCARTESIANPOINT((0.,0.));
#114=IFCDIRECTION((1.,0.));
#115=IFCAXIS2PLACEMENT2D(#113,#114);
#116=IFCSECONDORDERPOLYNOMIALSPIRAL(#115,538.60867250797071,-883.8834764831845,15625.);
~~~

Determine the second half placement and trimming.

**[todo: consider adding a figure that plots both parent curves. discuss that they both start at 0,0 and don't align at the mid-point. could either adjust origin of second half, or just trim and place - it's far easier to trim and place so we get the placement information from the end of the first half curve]**

The starting elevation of the second half is the end elevation of the first half

$D(50\ m) = (50\ m)^{2}\left( \frac{1}{31250\ m} + \frac{1}{(-538.6086725\ m)^{3}}(50\ m)^{2} \right) = 0.04\ m$

The slope at $50\ m$ is $\frac{dD'}{ds} = L_1^2\left(\frac{2s}{A_2^3} + \frac{A_1}{\left| A_1^3 \right|}\right) = (50\ m)^2\left(\frac{2\cdot 50\ m}{(-538.6086725\ m)^3} + \frac{31250\ m}{\left|(31250\ m)^3 \right|} \right) = -0.00159744$
. 

$dx_x = \frac{1}{\sqrt{(-0.00159744)^2 + 1}} = 0.999998724
,\ dx_y = \frac{-0.00159744}{\sqrt{(-0.00159744)^2 + 1}} = -0.001597438$

The cross slope at the end of the first half is 

$\phi(50\ m) = 1.464531464 + \left(\frac{\frac{\pi}{2} - 1.464531464}{0.08\ m}\right)(0.04\ m - 0.08\ m) = 1.517663895$

$dy_z = cos(\phi_s) = cos(1.517663895) = 0.053107436$

$dz_z = sin(\phi_s) = sin(1.517663895) = 0.998588804$

The trimming begins at $50\ m$ and progresses for a length of $50\ m$ for the second half segment.
~~~
#117=IFCCARTESIANPOINT((50.,0.04,0.));
#118=IFCDIRECTION((0.,0.053257642916150753,0.99858080467782662));
#119=IFCDIRECTION((0.9999987200024576,-0.0015999979520039342,0.));
#120=IFCAXIS2PLACEMENT3D(#117,#118,#119);
#121=IFCCURVESEGMENT(.CONTINUOUS.,#120,IFCLENGTHMEASURE(50.),IFCLENGTHMEASURE(50.),#116);
~~~

### 4.5.3 Compute Point on Curve

Compute the cant placement matrix for a point 75 m from the start of the curve segment. 

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve

$s_0 = 0,\ x_0 = 0,\ y(s_0) = 0,\ dx_0 = 1,\ dy_0 = 0,\ \theta_0 = 0$

**Step 2 — Form the normalization matrix $M_N$**

Since $x_0 = 0,\ y(s_0) = 0,\ \theta_0 = 0, M_N = I$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir_p} = (0.9999987200024576,-0.0015999979520039342,0.),\ \mathbf{Axis_p} = (0.,0.053257642916150753,0.99858080467782662)$

$\mathbf{Y_p} = \mathbf{Axis_p} \times \mathbf{RefDir_p} = (0.001597727253, 0.998579530, -0.0532575749)$

$$M_{CSP} = \begin{bmatrix}
0.999998720 & 0.001597727253 & 0 & 50.0 \\
-0.001599997953 & 0.998579530 & 0.0532576429 & 0.04 \\
 0 & -0.0532575749 & 0.998580805 & 0 \\
 0 & 0 & 0 & 1
 \end{bmatrix}$$

**Step 4 — Evaluate and map each point**
 
A point $75\ m$ from the start of the segment is in the second half of the helmert curve. Evaluate the second half parent curve at $s = 75\ m - 50\ m = 25\ m$

$D(25\ m) = (100\ m)^2\left(\frac{1}{(538.6086725\ m)^3}(25\ m)^2 + \frac{-883.8834765}{\left| (-883.8834765\ m)^3 \right|}(25\ m) + \frac{1}{15625\ m} \right) = 0.36\ m$

$M_{PC} = \begin{bmatrix} 
1 & 0 & 0 & 25 \\
0 & 1 & 0 & 0.36 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$

$M_c = M_{CSP}M_N M_{PC}$

$M_c = 
\begin{bmatrix}
0.999998720 & 0.001597727253 & 0 & 50.0 \\
-0.001599997953 & 0.998579530 & 0.0532576429 & 0.04 \\
 0 & -0.0532575749 & 0.998580805 & 0 \\
 0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix} I \end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 25 \\
0 & 1 & 0 & 0.36 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$

$M_c = \begin{bmatrix}
0.999999684 & 0.000799928774 & 0 & 75.0 \\
-0.000795461553 & 0.999910964 & 0.0133204468 & 0.01 \\
0 & -0.0133203149 & 0.999911281 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$

$\mathbf{Axis} = (0.0,\ 0.0133204468,\ 0.999911281)$

$\phi(75\ m) = tan^{-1}\left(\frac{0.999911281}{0.0133204468}\right) = 1.557475486$

The $\mathbf{Axis}$ vector is closer to vertical 75% way through the cant segment. At the end of the cant segment, $\mathbf{\text{Axis}}$ will be $\frac{\pi}{2}$.

## 4.6 Bloss Curve

### 4.6.1 Parent Curve Parametric Equations

### 4.6.2 Semantic Definition to Geometry Mapping

### 4.6.3 Compute Point on Curve

**Step 1 — Evaluate the parent curve at the trim start**

**Step 2 — Form the normalization matrix $M_N$**

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

**Step 4 — Evaluate and map each point**

$$\frac{D(s)}{L^{2}} = \frac{A_{3}}{\left| A_{3}^{5} \right|}s^{3} + \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{3A_{3}}{\left| A_{3}^{5} \right|}s^{2} + \frac{2}{A_{2}^{3}}s + \frac{A_{1}}{2\left| A_{1}^{3} \right|} \right)$$

$$D_{1} = \frac{D_{sl} + D_{sr}}{2},\ D_{2} = \frac{D_{el} + D_{er}}{2},\ \mathrm{\Delta}D = D_{2} - D_{1}$$

$$f = \mathrm{\Delta}D$$

The polynomial coefficients must have units of length. The basic form of
the coefficient of the $i^{th}$ term is

$$A_{i} = \frac{L^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{\left| a_{i} \right|}}\frac{a_{i}}{\left| a_{i} \right|}$$

Perform a dimensional analysis with $l$ representing term with length
units. We see that the resulting coefficient $A_{i}$ has units of length.

$$\frac{l^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{|l|}}\frac{l}{|l|} = \frac{l^{\frac{i + 2}{i + 1}}}{l^{\frac{1}{i + 1}}} = l^{\frac{i + 2}{i + 1}}l^{\frac{- 1}{(i + 1)}} = l^{\frac{i + 1}{i + 1}} = l$$

Constant Term

$$a_{0} = D_{1},\ A_{0} = \frac{L^{2}}{\left| a_{0} \right|}\frac{a_{0}}{\left| a_{0} \right|}$$

Linear Term

$$a_{1} = 0,\ A_{1} = \frac{L^{\frac{3}{2}}}{\sqrt{\left| a_{1} \right|}}\frac{a_{1}}{\left| a_{1} \right|}$$

Quadratic Term

$$a_{2} = 3f,\ A_{2} = \frac{L^{\frac{4}{3}}}{\sqrt[3]{\left| a_{2} \right|}}\frac{a_{2}}{\left| a_{2} \right|}$$

Cubic Term

$$a_{3} = - 2f,\ A_{3} = \frac{L^{\frac{5}{4}}}{\sqrt[4]{\left| a_{3} \right|}}\ \frac{a_{3}}{\left| a_{3} \right|}$$

Example

GENERATED\_\_CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc

~~~
#61=IFCALIGNMENTCANT('1FNFyDAJeHwv87wDZHIYI7',$,$,$,$,$,$,1.5);
#62=IFCALIGNMENTSEGMENT('1FNFyHAJeHwuDtwDZHIYI3',#3,$,$,$,$,$,#64);
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.,0.16,.BLOSSCURVE.);
#92=IFCCARTESIANPOINT((0.,0.));
#93=IFCDIRECTION((1.,0.));
#94=IFCAXIS2PLACEMENT2D(#92,#93);
#95=IFCCURVESEGMENT(.DISCONTINUOUS.,#94,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#91);
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCTHIRDORDERPOLYNOMIALSPIRAL(#98,-500.,746.900791092861,$,$);
#100=IFCCARTESIANPOINT((0.,0.,0.));
#101=IFCDIRECTION((0.,0.,1.));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

$$D_{1} = \frac{0 + 0}{2} = 0m,\ D_{2} = \frac{0 + 0.16}{2} = 0.08m,\ \mathrm{\Delta}D = 0.08 - 0 = 0.08m$$

$$f = \mathrm{\Delta}D = 0.08m$$

Constant Term
$$a_{0} = 0m,\ A_{0} = \frac{L^{2}}{\left| a_{0} \right|}\frac{a_{0}}{\left| a_{0} \right|} = \ 0m$$

Linear Term
$A_{1} = 0m$

Quadratic Term

$a_{2} = 3f = 3(0.08m) = 0.24m,\ A_{2} = \frac{(100m)^{\frac{4}{3}}}{\sqrt[3]{|0.24m|}}\left( \frac{0.24m}{|0.24m|} \right) = 746.9007911m$

Cubic Term

$a_{3} = -2f = -2(0.08m) = -0.16m,\ A_{3} = \frac{{(100m)}^{\frac{5}{4}}}{\sqrt[4]{|-0.16m|}}\left( \frac{-0.16m}{| -0.16m|} \right) = -500m$

Evaluate at start end of the segment

$$D(0m) = \frac{A_{3}L^{2}}{\left| A_{3}^{5} \right|}0^{3} + \frac{L^{2}}{A_{2}^{3}}0^{2} = 0.0m$$

$$D(50m) = \frac{-500m}{\left| ( -500m)^{5} \right|}(100m)^{2}(50m)^{3} + \frac{(100m)^{2}}{(746.9007811m)^{3}}(50m)^{2} = 0.04m$$

$$D(100m) = \frac{-500m}{\left| ( -500m)^{5} \right|}(100m)^{2}(100m)^{3} + \frac{(100m)^{2}}{(746.9007811m)^{3}}(100m)^{2} = 0.08m$$

Placement

$$\left( 0.0,\frac{L^{2}}{A_{0}},\ 0.0 \right) = (0.0,\ 0.0,\ 0.0)$$

## 4.7 Cosine Curve

### 4.7.1 Parent Curve Parametric Equations

### 4.7.2 Semantic Definition to Geometry Mapping

### 4.7.3 Compute Point on Curve

**Step 1 — Evaluate the parent curve at the trim start**

**Step 2 — Form the normalization matrix $M_N$**

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

**Step 4 — Evaluate and map each point**

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{1}{A_{1}}\cos\left( \pi\frac{s}{L} \right)$$

$$\frac{d}{ds}D(s) = L^{2}\left( -\frac{\pi}{L}\sin\left( \pi\frac{s}{L} \right) \right)$$

Constant term,
$A_{0} = \frac{L^{2}}{D_{1} + \frac{1}{2}\mathrm{\Delta}D}$

Cosine term, $A_{1} = \frac{L^{2}}{-\frac{1}{2}\mathrm{\Delta}D}$

Example

GENERATED\_\_CantAlignment_CosineCurve_100.0_1000_300_1_Meter.ifc

~~~
#61 = IFCALIGNMENTCANT(1FNFyDAJeHwv87wDZHIYI7, $, $, $, $, #134, $, 1.5);
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 0., 1.6E-1, .COSINECURVE.);
#112 = IFCSEGMENTEDREFERENCECURVE((#113), .F., #89, #130);
#113 = IFCCURVESEGMENT(.CONTINUOUS., #123, IFCLENGTHMEASURE(0.), IFCLENGTHMEASURE(100.), #127);
#123 = IFCAXIS2PLACEMENT3D(#124, #125, #126);
#124 = IFCCARTESIANPOINT((0., 0., 0.));
#125 = IFCDIRECTION((0., -0., 1.));
#126 = IFCDIRECTION((1., 0., 0.));
#127 = IFCCOSINESPIRAL(#128, -2500., 2500.);
#128 = IFCAXIS2PLACEMENT2D(#129, $);
#129 = IFCCARTESIANPOINT((0., 0.));
#130 = IFCAXIS2PLACEMENT3D(#131, #132, #133);
#131 = IFCCARTESIANPOINT((100., 8.E-2, 0.));
#132 = IFCDIRECTION((-0., 1.06064981392206E-1, 9.94359200551929E-1));
~~~

$$D_{1} = \frac{0 + 0}{2} = 0m,\ D_{2} = \frac{0 + 0.16}{2} = 0.08m,\ \mathrm{\Delta}D = 0.08 - 0 = 0.08m$$

$$A_{0} = \frac{({100m)}^{2}}{0 + \frac{1}{2}0.08m} = 250000\ m$$

$$A_{1} = \frac{{(100m)}^{2}}{- \frac{1}{2}0.08m} = -250000\ m$$

$$D(s) = \frac{{(100m)}^{2}}{250000m} + (\frac{({100m)}^{2}}{-250000m})\cos\left( \pi\frac{s}{100} \right)$$

Evaluate

$$D(0m) = \frac{{(100m)}^{2}}{250000m} - \frac{{(100m)}^{2}}{250000m}\cos(0) = 0\ m$$

$$D(50m) = \frac{({100m)}^{2}}{250000m} - \frac{(100m)^{2}}{250000m}\cos\left( \pi\frac{50m}{100m} \right) = 0.04\ m$$

$$D(100m) = \frac{({100m)}^{2}}{250000m} - \frac{(100m)^{2}}{250000m}\cos\left( \pi\frac{100m}{100m} \right) = 0.08\ m$$

## 4.8 Sine Curve

### 4.8.1 Parent Curve Parametric Equations

### 4.8.2 Semantic Definition to Geometry Mapping

### 4.8.3 Compute Point on Curve

**Step 1 — Evaluate the parent curve at the trim start**

**Step 2 — Form the normalization matrix $M_N$**

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

**Step 4 — Evaluate and map each point**

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{A_{1}}{\left| A_{1} \right|}\left( \frac{1}{A_{1}} \right)^{2}s + \frac{1}{A_{2}}\sin\left( 2\pi\frac{s}{L} \right)$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{A_{1}}{\left| A_{1} \right|}\left( \frac{1}{A_{1}} \right)^{2} + \frac{2\pi}{LA_{2}}\cos\left( 2\pi\frac{s}{L} \right) \right)$$

Constant term: $A_{0} = \frac{L^{2}}{D_{1}}\ $

Linear term: $A_{1} = \frac{L^{\frac{3}{2}}}{\sqrt{\mathrm{\Delta}D}}$

Sine term: $A_{2} = \frac{L^{2}}{- \frac{1}{2\pi}\mathrm{\Delta}D}$

Example

GENERATED\_\_CantAlignment_SineCurve_100.0_300_1000_1_Meter.ifc

~~~
#61 = IFCALIGNMENTCANT(1FNFyDAJeHwv87wDZHIYI7, $, $, $, $, #134, $, 1.5);
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 1.6E-1, 0., .SINECURVE.);
#112 = IFCSEGMENTEDREFERENCECURVE((#113), .F., #89, #130);
#113 = IFCCURVESEGMENT(.CONTINUOUS., #123, IFCLENGTHMEASURE(0.), IFCLENGTHMEASURE(100.), #127);
#123 = IFCAXIS2PLACEMENT3D(#124, #125, #126);
#124 = IFCCARTESIANPOINT((0., 8.E-2, 0.));
#125 = IFCDIRECTION((-0., 1.06064981392206E-1, 9.94359200551929E-1));
#126 = IFCDIRECTION((1., 0., 0.));
#127 = IFCSINESPIRAL(#128, 7853.98163397448, -353.553390593274, 1250.);
#128 = IFCAXIS2PLACEMENT2D(#129, $);
#129 = IFCCARTESIANPOINT((0., 0.));
#130 = IFCAXIS2PLACEMENT3D(#131, #132, #133);
#131 = IFCCARTESIANPOINT((100., 0., 0.));
#132 = IFCDIRECTION((0., -0., 1.));
#133 = IFCDIRECTION((1., 0., 0.));
~~~

$$D_{1} = \frac{0m + 0.16m}{2} = 0.08m,\ D_{2} = \frac{0 + 0}{2} = 0m,\ \mathrm{\Delta}D = 0 - 0.08 = - 0.08m$$

Constant term:
$A_{0} = \frac{L^{2}}{D_{1}} = \frac{(100m)^{2}}{0.08m} = 125000m$

Linear term:
$A_{1} = \frac{L^{\frac{3}{2}}}{\sqrt{\mathrm{\Delta}D}} = \frac{(100m)^{\frac{3}{2}}}{\sqrt{| -0.08m|}}\frac{-0.08m}{| -0.08m|} = - 3535.533906m$

Sine term:
$A_{2} = \frac{L^{2}}{-\frac{1}{2\pi}\mathrm{\Delta}D} = \frac{(100m)^{2}}{-\frac{1}{2\pi}( -0.08m)} = 78539.81634m$

$$D(0m) = \frac{(100m)^{2}}{125000m} + \left( \frac{-3535.533906m}{| -3535.533906m|} \right)\left( \frac{1}{-3535.533906m} \right)^{2}(0m)(100m)^{2} + \frac{(100m)^{2}}{78539.81634m}\sin\left( 2\pi\frac{0m}{100m} \right) = 0.08m$$

$$D(50m) = \frac{(100m)^{2}}{125000m} + \left( \frac{- 3535.533906m}{| - 3535.533906m|} \right)\left( \frac{1}{-3535.533906m} \right)^{2}(50m)(100m)^{2} + \frac{(100m)^{2}}{78539.81634m}\sin\left( 2\pi\frac{50m}{100m} \right) = 0.04m$$

$$D(100m) = \frac{(100m)^{2}}{125000m} + \left( \frac{-3535.533906m}{| -3535.533906m|} \right)\left( \frac{1}{-3535.533906m} \right)^{2}(100m)(100m)^{2} + \frac{(100m)^{2}}{78539.81634m}\sin\left( 2\pi\frac{100m}{100m} \right) = 0.0m$$

## 4.9 Viennese Bend

### 4.9.1 Parent Curve Parametric Equations

### 4.9.2 Semantic Definition to Geometry Mapping

### 4.9.3 Compute Point on Curve

**Step 1 — Evaluate the parent curve at the trim start**

**Step 2 — Form the normalization matrix $M_N$**

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

**Step 4 — Evaluate and map each point**

Parent Curve: `IfcSeventhOrderPolynomialSpiral`

$$\frac{D(s)}{L^{2}} = \frac{A_7}{|A_7^9|}s^7 + \frac{1}{A_6^7}s^6 + \frac{A_5}{|A_5^7|}s^5 + \frac{1}{A_4^5}s^4 + \frac{A_{3}}{\left| A_{3}^{5} \right|}s^{3} + \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{7A_7}{|A_7^9|}s^6 + \frac{6}{A_6^7}s^5 + \frac{5A_5}{|A_5^7|}s^4 + \frac{4}{A_4^5}s^3 + \frac{3A_{3}}{\left| A_{3}^{5} \right|}s^{2} + \frac{2}{A_{2}^{3}}s + \frac{A_{1}}{2\left| A_{1}^{3} \right|} \right)$$

$$D_{1} = \frac{D_{sl} + D_{sr}}{2},\ D_{2} = \frac{D_{el} + D_{er}}{2},\ \mathrm{\Delta}D = D_{2} - D_{1}$$

$$f = \mathrm{\Delta}D$$

The polynomial coefficients must have units of length. The basic form of
the coefficient of the $i^{th}$ term is

$$A_{i} = \frac{L^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{\left| a_{i} \right|}}\frac{a_{i}}{\left| a_{i} \right|}$$

Perform a dimensional analysis with $l$ representing term with length
units. We see that the resulting coefficient $A_{i}$ has units of length.

$$\frac{l^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{|l|}}\frac{l}{|l|} = \frac{l^{\frac{i + 2}{i + 1}}}{l^{\frac{1}{i + 1}}} = l^{\frac{i + 2}{i + 1}}l^{\frac{- 1}{(i + 1)}} = l^{\frac{i + 1}{i + 1}} = l$$

Constant Term

$$a_{0} = D_{1}, A_{0} = \frac{L^{2}}{\left| a_{0} \right|}\frac{a_{0}}{\left| a_{0} \right|}$$

Linear Term

$$a_{1} = 0, A_{1} = \frac{L^{\frac{3}{2}}}{\sqrt{\left| a_{1} \right|}}\frac{a_{1}}{\left| a_{1} \right|}$$

Quadratic Term

$$a_{2} = 0, A_{2} = \frac{L^{\frac{4}{3}}}{\sqrt[3]{\left| a_{2} \right|}}\frac{a_{2}}{\left| a_{2} \right|}$$

Cubic Term

$$a_{3} = 0, A_{3} = \frac{L^{\frac{5}{4}}}{\sqrt[4]{\left| a_{3} \right|}}\ \frac{a_{3}}{\left| a_{3} \right|}$$

Quartic Term

$$a_{4} = 35f, A_{4} = \frac{L^{\frac{6}{5}}}{\sqrt[5]{\left| a_{4} \right|}}\ \frac{a_{4}}{\left| a_{4} \right|}$$

Quintic Term

$$a_{5} = -84f, A_{5} = \frac{L^{\frac{7}{6}}}{\sqrt[6]{\left| a_{5} \right|}}\ \frac{a_{5}}{\left| a_{5} \right|}$$

Sextic Term

$$a_{6} = 70f, A_{6} = \frac{L^{\frac{8}{7}}}{\sqrt[7]{\left| a_{6} \right|}}\ \frac{a_{6}}{\left| a_{6} \right|}$$

Septic Term

$$a_{7} = -20f, A_{7} = \frac{L^{\frac{9}{8}}}{\sqrt[8]{\left| a_{7} \right|}}\ \frac{a_{7}}{\left| a_{7} \right|}$$

### 4.9.4 Example
[GENERATED__CantAlignment_VienneseBend_100.0_300_1000_1_Meter.ifc](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/blob/master/alignment_testset/IFC-WithGeneratedGeometry/GENERATED__CantAlignment_VienneseBend_100.0_300_1000_1_Meter.ifc)

~~~
#61=IFCALIGNMENTCANT('1FNFyDAJeHwv87wDZHIYI7',$,$,$,$,$,$,1.5);
#62=IFCALIGNMENTSEGMENT('1FNFyHAJeHwuDtwDZHIYI3',#3,$,$,$,$,$,#64);
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.1,0.03,.VIENNESEBEND.);

#79=IFCSEGMENTEDREFERENCECURVE((#104),.F.,#78,$);
#99=IFCSEVENTHORDERPOLYNOMIALSPIRAL(#98,185.935683676356,-169.870955956539,180.001218460868,-241.197489008512,$,$,$,200000.);
#100=IFCCARTESIANPOINT((0.,0.05,0.));
#101=IFCDIRECTION((0.,0.0665190105237739,0.997785157856609));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

$$D_{sl} = 0.0$$
$$D_{el} = 0.0$$
$$D_{sr} = 0.1$$
$$D_{er} = 0.03$$

$$D_{1} = \frac{0 + 0.1}{2} = 0.05m, D_{2} = \frac{0 + 0.03}{2} = 0.015m,\ \mathrm{\Delta}D = 0.015 - 0.05 = -0.035m$$

$$f = \mathrm{\Delta}D = -0.035m$$

Constant Term
$$a_{0} = 0.05m, A_{0} = \frac{100m^{2}}{\left| 0.05 \right|}\frac{0.05}{\left| 0.05 \right|} = 20000m$$

Linear Term
$$a_{1} = 0, A_{1} = 0m$$

Quadratic Term

$$a_{2} = 0, A_{2} = 0m$$

Cubic Term

$$a_{3} = 0, A_{3} = 0m$$

Quartic Term

$$a_{4} = 35(-0.035m) = -1.225m, A_{4} = \frac{100m^{\frac{6}{5}}}{\sqrt[5]{\left| -1.225m \right|}}\ \frac{-1.225m}{\left| -1.225m \right|} = -241.1974890085123m$$

Quintic Term

$$a_{5} = -84(-0.035m)=2.94m, A_{5} = \frac{100m^{\frac{7}{6}}}{\sqrt[6]{\left| 2.94m \right|}}\ \frac{2.94m}{\left| 2.94m \right|} = 180.0012184608678m$$

Sextic Term

$$a_{6} = 70(-0.035m)=-2.45m, A_{6} = \frac{100m^{\frac{8}{7}}}{\sqrt[7]{\left| -2.45m \right|}}\ \frac{-2.45m}{\left|-2.45m\right|} = -169.87095595653895m$$

Septic Term

$$a_{7} = -20(-0.035m) = 0.7m, A_{7} = \frac{100m^{\frac{9}{8}}}{\sqrt[8]{\left| 0.7m \right|}}\ \frac{0.7m}{\left| 0.7m \right|} = 185.93568367635672m$$

Evaluate at start, middle, and end of the segment.

$Cant(u) = D(u) - D(0) + Cant(0)$

$Cant(0)$ = `IfcCurveSegment.Placement.Location.Coordinates[2]` = $0.05m$


$$D(0m) = (100m)^2 \left(\frac{185.93568367635672m}{|(185.93568367635672m)^9|}(0m)^7 + \frac{1}{(-169.87095595653895m)^7}(0m)^6 + \frac{180.0012184608678m}{|(180.0012184608678m)^7|}(0m)^5 + \frac{1}{(-241.1974890085123m)^5}(0m)^4  + \frac{1}{20000m}\right) = 0.5m$$

$$Cant(0m) = 0.5m - 0.5m + 0.05m = 0.05m$$

$$D(50m) = (100m)^2 \left(\frac{185.93568367635672m}{|(185.93568367635672m)^9|}(50m)^7 + \frac{1}{(-169.87095595653895m)^7}(50m)^6 + \frac{180.0012184608678m}{|(180.0012184608678m)^7|}(50m)^5 + \frac{1}{(-241.1974890085123m)^5}(50m)^4  + \frac{1}{20000m}\right) = 0.4825m$$

$$Cant(50m) = 0.4825m - 0.5m + 0.05m = 0.0325m$$


$$D(100m) = (100m)^2 \left(\frac{185.93568367635672m}{|(185.93568367635672m)^9|}(100m)^7 + \frac{1}{(-169.87095595653895m)^7}(100m)^6 + \frac{180.0012184608678m}{|(180.0012184608678m)^7|}(100m)^5 + \frac{1}{(-241.1974890085123m)^5}(100m)^4  + \frac{1}{20000m}\right) = 0.465m$$

$$Cant(100m) = 0.465m - 0.5m + 0.05m = 0.015m$$

Placement

$$\left( 0.0,\frac{L^{2}}{A_{0}},\ 0.0 \right) = (0.0, 0.05, 0.0)$$

## 4.10 Combined 3D

[do a full cant example]

## 4.11 Deviation from EnrichIfc4x3 Reference Implementation

The cant calculations in this section deviate from the ones performed by the EnrichIfc4x3
reference implementation. The calculations in the reference implementation, published at
[IFC-Rail-Unit-Test-Reference-Code/EnrichIFC4x3/EnrichIFC4x3/business2geometry
at master · bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code
(github.com)](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/tree/master/EnrichIFC4x3/EnrichIFC4x3/business2geometry), yield coefficients for sine, cosine, and polynomial spirals that are not in units of length. The IFC specification is clear that the coefficients have
units of length and are represented by `IfcLengthMeasure`.

The error in the EnrichIfc4x3 reference implementation is illustrated by way of an example. Consider the Bloss Curve example [GENERATED__CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/blob/master/alignment_testset/IFC-WithGeneratedGeometry/GENERATED__CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc). 

The semantic definition of the cant transition segment is 
~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.,0.16,.BLOSSCURVE.);
~~~

The EnrichIfc4x3 reference implementation maps the semantic definition to the geometric representation as follows:

$D_s = \frac{0 + 0}{2} = 0\ m,\ D_e = \frac{0 + 0.16}{2} = 0.08\ m,\ \Delta D = 0.08-0 = 0.08\ m,\ f = \Delta D = 0.08\ m$

Quadratic Term:

$a_{2} = 3f = 3(0.08m) = 0.24\ m$

$A_{2} = \frac{(100\ m)}{\sqrt[3]{|0.24\ m|}}\left( \frac{0.24\ m}{|0.24\ m|} \right) = 160.917897\ m^{2/3}$


Cubic Term:

 $a_{3} = -2f = -0.016m$
 
 $A_{3} = \frac{100\ m}{\sqrt[4]{|-0.16\ m|}}\frac{-0.16\ m}{|-0.16\ m|} = -158.113883\ m^{3/4}$

Notice that the polynomial coefficents do not have whole length units (e.g. the units aren't $m$).

 The mapped geometric representation is
 ~~~
#127 = IFCTHIRDORDERPOLYNOMIALSPIRAL(#128, -158.113883008419, 160.914897434272, $, $);
 ~~~

Recalling from Bloss Curve example above, 

Quadratic Term

$A_{2} = \frac{(100m)^{\frac{4}{3}}}{\sqrt[3]{|0.24m|}}\left( \frac{0.24m}{|0.24m|} \right) = 746.9007911\ m$

Cubic Term

$A_{3} = \frac{{(100\ m)}^{\frac{5}{4}}}{\sqrt[4]{|-0.16\ m|}}\left( \frac{-0.16\ m}{| -0.16\ m|} \right) = -500\ m$

The polynomial coefficients have units of length as required by IFC.

The resulting geometric representation is
~~~
#127=IFCTHIRDORDERPOLYNOMIALSPIRAL(#98,-500.,746.900791092861,$,$);
~~~

Table 4.10-1 compares the third order polynomal terms.

| Polynomial Term | EnrichIfc4x3 | This Guide |
|---|---|---|
| Constant | $0.0$ (unitless) | $0\ m$|
| Linear | $0\ m^{1/2}$ | $0\ m$|
| Quadratic | $160.91789\ m^{2/3}$| $746.90078\ m$|
| Cubic | $-158.113883\ m^{3/4}$| $-500\ m$|

*Table 4.10-1 — Comparison of polynomial coefficients*

The EnrichIfc4x3 reference implementation computes the correct value for the deviating elevation. This is because there is a compensating error in the implementation. The deviating elevation is computed as

$D(s) = L\left( \frac{A_3}{|A_3^5|}s^3 + \frac{1}{A_2^3}s^2\right)$

Evaluated at $s = 50\ m$

$D(50\ m) = (100\ m)\left( \frac{-158.113883\ m^{3/4}}{|(-158.113883\ m^{3/4})^5|}(100\ m)^3 + \frac{1}{(160.914897434272\ m^{2/3})^3}(100\ m)^2\right) = (100\ m)(-0.0002+0.0006) = 0.04\ m$

The deviating elevation as computed in this guide is

$D(s)= L^2\left( \frac{A_3}{|A_3^5|}s^3 + \frac{1}{A_2^3}s^2\right)$

Notice that the first term is $L^2$, not $L$ as in the reference implementation.

$D(50\ m) = (100\ m)^2\left( \frac{-500\ m}{|(-500\ m)^5|}(100\ m)^3 + \frac{1}{(746.90079\ m)^3}(100\ m)^2\right) = (100\ m)^2(-0.000002\ 1/m + 0.000006\ 1/m) = 0.04\ m$

Both approaches give the same result, however, a serious problem emerges if the EnrichIfc4x3 semantic to geometry mapping is mixed with the deviating elevation equation from this guide and visa-versa. Table 4.10-2 compares the results for all the combinations of the sematic to geometry mapping and deviation elevation computations for the Bloss curve evaluated at $s=50\ m$. The deviating elevation can be incorrect by a factor of 100 or 1/100. 

| Mapping | $D(s)$ Equation | $D(50\ m)$ |
|---|---|---|
| EnrichIfc4x3 | EnrichIfc4x3 | $0.04\ m$ |
| This Guide | This Guide | $0.04\ m$ |
| EnrichIfc4x3 | This Guide | $4.0\ m$ |
| This Guide | EnrichIfc4x3 | $0.0004\ m$ |

*Table 4.10-2 — Comparison of deviation elevation results*
