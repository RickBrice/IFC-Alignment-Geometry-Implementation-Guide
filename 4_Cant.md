outline:
* need figure the show cross slope and coordinate system 3D and 2-2D elevation and section.
* need figure that shows centerline and railhead deviation
* provide a bit more discussion in the examples. reference the example files
* need to discuss cross slope, Axis vector, and their orientation and relation to one another. Axis is normal to cross slope line. $\phi(s) = \phi_s + \left(\frac{\phi_e - \phi_s}{D_e - D_s}\right)\bigl(D(s) - D_s\bigr)$. Should this equation use $\Delta D$?


# Section 4.0 - Cant Alignment

Cant (also called superelevation) is the transverse inclination of a railway track cross-section: the elevation difference between the two railheads when one rail is raised above the other. By tilting the track into a curve, cant directs a component of gravitational force inward, partially offsetting the centrifugal acceleration experienced by vehicles negotiating the curve. The result is improved ride quality, reduced wheel–rail lateral forces, and the ability to operate at higher speeds through curves without exceeding comfort or safety limits.

Cant is measured as a length — the height difference between railheads — rather than as an angle. The conversion between the two depends on track gauge. `IfcAlignmentCant.RailHeadDistance` supplies the centre-to-centre distance between railheads, which is the lever arm for this conversion.

## 4.1 General

An `IfcSegmentedReferenceCurve` describes the cross slope of superelevated rail lines as a track banks through curves. When the point of rotation is about one of the railheads, the alignment elevation must deviate to accomodate the cross slope. 

An `IfcSegmentedReferenceCurve` also describes this deviation in elevation. As a subtype of `IfcCompositeCurve`, an `IfcSegmentedReferenceCurve` consists of an end to start collection of `IfcCurveSegment`. An `IfcSegmentedReferenceCurve` also has a `BasisCurve` which is typically an `IfcGradientCurve`.

The `IfcCurveSegment.ParentCurve` defines the deviating elevation over the length of the segment. When the segment start elevation differs from the
segment start elevation of the next segment, the `IfcCurveSegment.ParentCurve` also defines variation in the deviating elevation. If the
segment start elevation is the same as for the start of the next segment, the deviating elevation along the length of the segment is
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


The transition functions used to shape cant variation have the same functional form as functions used for horizontal transition curves: line, clothoid (linear cant), Helmert, Bloss, cosine, sine, and Viennese bend. In practice, the cant transition type always matches the horizontal transition type, though IFC does not enforce this constraint.

As an example, the horizontal tangent direction, $\theta(t)$, and the radius of curvature, $\kappa(t)$, for a Helmert curve is a second order polynomial of the form


$$\theta(t) = \frac{t^{3}}{3A_{2}^{3}} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}t^{2} + \frac{t}{A_{0}}$$

$$\kappa(t) = \frac{\theta(t)}{dt} = \frac{1}{A_{2}^{3}}t^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}t + \frac{1}{A_{0}}$$

The cant deviating elevation for a Helmert transition is of the same form as the curvature

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

The deviating elevation has the same functional form as the radius of curvature of the horizontal alignment segment. 

In IFC, the semantic cant profile is encoded in `IfcAlignmentCant` and its child `IfcAlignmentCantSegment` entities. The geometric representation is an `IfcSegmentedReferenceCurve`, which evaluates the cant at every point along the alignment and, in conjunction with the horizontal alignment `IfcCompositeCurve` and the vertical alignment `IfcGradientCurve`, produces the full 3D track centerline geometry.

[todo: add a figure to illustrate the cross slope and centerline elevation deviation] 

Each `IfcCurveSegment` in an `IfcSegmentedReferenceCurve` is evaluated in a two-dimensional coordinate system whose axes are *distance along the horizontal alignment* $s$ and *deviating elevation* $D$. The deviating elevation is the vertical offset applied to the track centerline, away from the gradient curve, to produce the correct cross-slope angle at every point along the segment.

The `StartCantLeft` $D_{sl}$, `EndCantLeft` $D_{el}$, `StartCantRight` $D_{sr}$, and `EndCantRight` $D_{el}$ attributes of `IfcAlignmentCantSegment` determine $D_s$ and $D_e$ as the averages of their respective left and right values:

$$D_s = \frac{D_{sl} + D_{sr}}{2}, \quad D_e = \frac{D_{el} + D_{er}}{2} \quad \Delta D = D_e - D_s$$

The cross-slope angle $\phi$ at a given point is not obtained directly from the parent curve equation; instead it is interpolated between the start and end cross-slope angles encoded in the `Axis` vector of the `IfcCurveSegment.Placement`, using the deviating elevation as the interpolation parameter:

$$\phi(s) = \phi_s + \left(\frac{\phi_e - \phi_s}{\Delta D}\right)\bigl(D(s) - D_s\bigr)$$

$$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}} \right)$$

where $\phi_s$ and $\phi_e$ are the cross-slope angles at the start and end of the segment and $D(s)$ is the deviation elevation at $s$. The `Axis` vector at any point is $(0,\ \cos\phi(s),\ \sin\phi(s))$. The `Axis` vector is perpendicular to a line connecting the railheads in an upwards direction. The cross-slope angle $\phi$ is the angle from the transverse $y$ axis to the `Axis` vector. In sections without cant, `Axis` is (0,0,1) and $\phi = \frac{\pi}{2}$.

Together, the distance along, the deviating elevation $D(s)$, and the cross-slope angle $\phi(s)$ fully specify a 3D placement frame for the track centerline at each arc-length $s$. Section 4.2 describes an algorithm for constructing that frame and composing it with the horizontal and vertical matrices to produce a 3D position.

All examples use a railhead distance $D_{rh} = 1.5\ m$.

## 4.2 Curve Segment Evaluation Algorithm

Cant segments are evaluated in a two-dimensional "distance along, deviating elevation" $(s,D(s))$ coordinate system in which $d$ is the distance measured along the horizontal `IfcCompositeCurve` and $D(s)$ is the deviating elevation: the vertical offset applied to the track centerline to accommodate the cross slope. Unlike horizontal and vertical segments, each cant point also carries a cross slope angle $\phi(s)$, making the local frame inherently three-dimensional.

**Steps 1—4** follow the identical procedure describe in Section 2.2 for horizontal segments, substituting distance along for the horizontal $x$-coordinate and deviating elevation for the horizontal y-coordinate. Let $s_0 = $ `IfcAlignmentCantSegment.StartDistAlong`.

**Step 1 — Evaluate the parent curve at the trim start**

Compute the deviating elevation $D_0 = D(s_0)$ and the slope angle $\theta_0 = \tan^{-1}(D'(s_0))$.

**Step 2 — Form the normalization matrix $M_N$**

$M_N$ simultaneously translates the trim-start point to the origin and rotates so that the tangent at $s_0$ aligns with the positive $x$-direction.

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$M_{CSP}$ is constructed from `IfcCurveSegment.Placement`: $(s_p, D_p)$ is the `Location` (distance along, deviating elevation), the `RefDirection` gives slope angle $\theta_p$, and the `Axis` gives cross slope angle $\phi_p$.

$$\mathbf{RefDir}_p = (\cos\theta_p,\ \sin\theta_p,\ 0),\quad \mathbf{Axis}_p = \mathbf{Z}_p = (0,\ \cos\phi_p,\ \sin\phi_p)$$
$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p,\quad \mathbf{X}_p = \mathbf{Axis}_p \times \mathbf{Y}_p$$

The placement in matrix form is

$$M_{CSP} = \begin{bmatrix} 
X_p.x & Y_p.x & Z_p.x & s_p \\
X_p.y & Y_p.y & Z_p.y & 0 \\
X_p.z & Y_p.z & Z_p.z & D_p \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 — Evaluate and map each point**

For the point at a distance along the horizontal alignment $s$, compute $D(s)$ and $\theta(s) = \tan^{-1}(D'(s))$. Interpolate the cross slope angle between the segment start and end values:

$$\phi(s) = \phi_s + \left(\frac{\phi_e - \phi_s}{\Delta D}\right)(D(s) - D_s)$$

Form the local frame:

$$\mathbf{X} = (\cos\theta(s),\ \sin\theta(s),\ 0),\quad \mathbf{Z} = (0,\ \cos\phi,\ \sin\phi)$$
$$\mathbf{Y} = \mathbf{Z} \times \mathbf{X}$$

$$M_{PC} = \begin{bmatrix}
X.x & Y.x & Z.x & s \\
X.y & Y.y & Z.y & 0 \\
X.z & Y.z & Z.z & D(s) \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$$M_c = M_{CSP}\ M_N\ M_{PC}$$

Step 5 is performed immediately for this point before moving to the next arc-length $s$.

**Step 5 — Combine with horizontal and vertical to produce the 3D placement matrix**

The cant result must be combined with the horizontal matrix $M_h$ (evaluated at distance $s$ along the `IfcCompositeCurve`) and the vertical matrix $M_v$ (evaluated at the same $s$). All three coordinate systems share the distance-along axis, so the positional components of $M_v$ and $M_c$ must be extracted before multiplication and added back afterward to avoid incorrectly rotating the position offsets.

Construct $M'_v$ as described in Section 3.2.

Construct $M'_c$ by zeroing the distance-along component in column 4 of $M_c$:

$${M'}_c = \begin{bmatrix} 
X.x & Y.x & Z.x & 0 \\ 
X.y & Y.y & Z.y & 0 \\ 
X.z & Y.z & Z.z & D \\ 
0 & 0 & 0 & 1 
\end{bmatrix}$$

Extract position vectors from each modified matrix, $M'_v,\ M'_c$, (setting row 4 to zero), then zero column 4 before multiplying:

$$P_v = M'_v \text{ column 4, row 4 set to 0} = \begin{bmatrix} 0 \\ 0 \\ z \\ 0 \end{bmatrix}, \qquad P_c = M'_c \text{ column 4, row 4 set to 0} = \begin{bmatrix} 0 \\ 0 \\ D \\ 0 \end{bmatrix}$$

$$M''_v = M'_v \text{ with column 4 set to } (0,0,0,1)^T, \qquad M''_c = M'_c \text{ with column 4 set to } (0,0,0,1)^T$$

<span style="background-color: yellow;color: black">[todo: show the full $M''_v$ and $M''_c$ matrices]</span>

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

### 4.3.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$D(s) = D_s = D_e$$

$$\frac{d}{ds}D(s) = 0.0$$

### 4.3.2 Semanic Definition to Geometry Mapping

Consider 100 m long segment of a railway that is turning towards the left. The right rail is raised 0.16 m through the circular portion of the curve. The sementic definition is

~~~
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 0.16, 0.16, .CONSTANTCANT.);
~~~

$D_s = \frac{0.0\ m + 0.16\ m}{2} = 0.08\ m \quad D_e = \frac{0.0\ m + 0.16\ m}{2} = 0.08\ m$

$\Delta D = D_e - D_s = 0.08\ m - 0.08\ m = 0.0\ m$

The parent curve has a constant deviating elevation at $0.08\ m$ and a slope of $0.0$.

Define the parent curve as an `IfcLine` passing through (0,0.08) in the direction (1,0).

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCVECTOR(#97,1.);
#99=IFCLINE(#96,#98);
~~~

The `IfcCurveSegment` trims a segment from the parent curve. The curve segment placement must capture the cross-slope rotation between the rail heads. For this reason the placement is an `IfcAxis2Placement3D` (instead of `IfcAxis2Placement2D` used for horizontal and vertical representations).

The cross-slope angle is $\phi = tan{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}} \right)$.

$\phi = tan^{-1}\left(\frac{1.5}{0.16-0.0}\right) = 1.4645314$

$dz_y = cos\phi = 0.10606498$

$dz_z = sin\phi = 0.99435920$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10606498139220574,0.99435920055192883));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.3.2 Compute Point on Curve

<span style="background-color: yellow;color: black">
[todo - look at this example carefully, the cant terms are in the Z position - should they be in the Y position?]
</span>

Compute the placement matrix for a point $s = 50\ m$ from the start of the curve segment.

**Step 1 - Evaluate the parent curve at the trim start**

$s_0 = 0, D(0) = D_0 = 0.08\ m, D'(0) = \theta_0 = 0.$

**Step 2 - Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
1 & 0 & 0 & 0 \\
 0 & 1 & 0 & -0.08 \\ 
 0 & 0 & 1 & 0 \\
 0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 3 - Form the curve segment placement matrix $M_{CSP}$**

$$\mathbf{RefDir}_p = (1,\ 0,\ 0),\quad \mathbf{Axis}_p = (0,\ 0.10606498,\ 0.99435920)$$
$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ -0.10606498,\ 0.99435920),\quad \mathbf{X}_p = \mathbf{Axis}_p \times \mathbf{Y}_p = (1,\ 0,\ 0)$$

$$M_{CSP} = \begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.99435920 & 0.10606498 & 0.08 \\
0 & -0.10606498 & 0.99435920 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 - Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$.

$D(50\ m) = 50\ m$

$D'(50\ m) = 0$

$$M_{PC} = \begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 1 & 0 & 0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$$M_c = M_{CSP}\, M_N\, M_{PC}$$

$$M_c =
\begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.99435920 & 0.10606498 & 0.08 \\
0 & -0.10606498 & 0.99435920 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
 0 & 1 & 0 & -0.08 \\ 
 0 & 0 & 1 & 0 \\
 0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 1 & 0 & 0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

$$M_c = \begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 0.99435920 & 0.10606498 & 0.08 \\
0 & -0.10606498 & 0.99435920 & 0 \\
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

Consider an alignment segment that has a clothoid transition curve towards the left. The track banks at a constantly increasing rate resulting in a linear deviation in the right rail elevation relative to the left rail. The right rail raises 160 mm over the 100 m segment length.

The semantic representation of the cant alignment is

~~~
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 0.16, 0., .LINEARTRANSITION.);
~~~

Compute the parent curve parameters.

$D_{sl} = 0\ m\quad D_{el} = 0\ m$

$D_{sr} = 0.16\ m\quad D_{er} = 0\ m$

$D_s = \frac{(0.16 + 0)}{2} = 0.08\ m$

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

The cant segment begins with a deviating elevation of

$$D(0\ m) = (100\ m)^2\left(\frac{1}{125000} + \frac{-3535.533906}{|-3535.533906|^3}(0\ m)\right) = 0.08\ m$$

The slope at the start of the segment is

$$D'(0\ m) = (100\ m)^{2}\frac{-3535.533906}{\left| -3535.533906^{3} \right|} = -0.0008$$

$$\theta_0 = tan^{-1}(-0.0008) = -0.00079999$$

$dx_x = cos(\theta_0) = 0.999999680$

$dy_x = sin(\theta_0) = -0.000799999744$

The cross-slope at the start of the segment is

$\phi(0) = \phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.16 - 0.0}\right) = 1.464531464$

$dy_z = cos(\phi_s) = cos(1.464531464) = 0.106064981$

$dz_z = sin(\phi_s) = sin(1.464531464) = 0.994359201$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.106064981,0.994359201));
#102=IFCDIRECTION((0.999999680,-0.000799999744,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.4.3 Compute Point on Curve

Compute the cant placement matrix for a point 50 m from the start of the curve segment.

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve 

$s_0 = 0$

$D(0\ m) = (100\ m)^{2}\left( \frac{1}{125000\ m} + \frac{(-3535.533906\ m)}{\left| (-3535.533906\ m)^{3} \right|}(0\ m) \right) = 0.08\ m$

$D'(0) = -0.0008,\ \theta_0 = -0.00079999$


**Step 2 — Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

$$M_N = \begin{bmatrix}
0.999999680 & -0.000799999744 & 0 & 0 \\
0.000799999744 & 0.999999680 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir}_p = (0.9999996800,-0.000799999744,0.),\ \mathbf{Axis}_p = (0.,0.106064981,0.994359201)$

$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0.0007954871, 0.9943588828, -0.1060649471)$

$$M_{CSP} = \begin{bmatrix} 
0.9999996800 & 0.0007954871 & 0 & 0 \\
-0.000799999744 & 0.9943588828 & 0.106064981 & 0.08 \\
0 & -0.1060649471 & 0.994359201 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

The $\mathbf{Axis}$ vector is perpendicular to the railhead cross slope line.

$\mathbf{Axis} = (0.0,\ 0.106064981,\ 0.994359201)$

$\phi_p = tan^{-1}\left(\frac{0.994359201}{0.106064981}\right) = 1.464531464$

With the cross section $y$-axis to the left and $z$-axis upwards, the vector is nearly vertical, pointing slightly to the left. This is consistent with a curve to the left and the right rail being superelevated.

**Step 4 — Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$

$D(50\ m) = (100\ m)^{2}\left( \frac{1}{125000\ m} + \frac{(-3535.533906\ m)}{\left| (-3535.533906\ m)^{3} \right|}(50\ m) \right) = 0.04\ m$

$$M_{PC} = \begin{bmatrix} 
1 & 0 & 0 & 50 \\
0 & 1 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$M_c = M_{CSP}M_N M_{PC}$

$$M_c = 
\begin{bmatrix}
0.999999680000 & 0.0007988711 & 0.0000424859 & 0 \\
-0.000800000085 & 0.9985884845 & 0.053107402 & 0.08 \\
0 & -0.053107419 & 0.9985882289 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 50 \\
0 & 1 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
$$

$$M_c = \begin{bmatrix}
0.9999996836000798 & 0.0007955209455802008 & 0.0 & 50.0 \\
-0.0007909999255054242 & 0.9985884897861665 & 0.05310743567896648 & 0.04 \\
0.0 & -0.05310740211832019 & 0.9985888044014736 & 0.0 \\
0.0 & 0.0 & 0.0 & 1.0
\end{bmatrix}$$

$\mathbf{Axis} = (0.0,\ 0.05310743567896648,\ 0.9985888044014736)$

$\phi(50\ m) = tan^{-1}\left(\frac{0.9985888044014736}{0.05310743567896648}\right) = 1.517663895$

The $\mathbf{Axis}$ vector is closer to vertical half way through the cant segment. At the end of the cant segment, $\phi$ will be $\frac{\pi}{2}$ (This is left for an excersie for the reader - repeat Step 5 with $s=100\ m$ to verify ).

As a quick check, the $\mathbf{\text{Axis}}$ direction vector half way through the cant segment should be the average value. $\frac{1.464531464+\frac{\pi}{2}}{2} = 1.517663895 = \phi(50\ m)$

## 4.5 Helmert Curve

Like the Helmert transition spiral, the Helmert cant sementic definition maps to two `IfcCurveSegment` instances for the geometric representation. The parent curve is `IfcSecondOrderPolynomialSpiral`.

### 4.5.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{2s}{A_{2}^{3}} + \frac{A_{1}}{\left| A_{1}^{3} \right|} \right)$$

The polynomial coefficietions carry a second subscript to indicate first half $1$, and second half $2$. For example, $A_{21}$ is coefficient $A_2$ for the first half and $A_{02}$ is coefficient $A_0$ for the second half. 
<span style="background-color: yellow;color: black">
[todo: add this description to 2_Horizonta.md]
</span>

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

Consider an alignment segment that has a Helmert transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

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

Note that the length of the first half curve is $L_1 =50\ m$, half the length of the full Helmert transition.

<span style="background-color: yellow;color: black">
[todo - Need to do a better job explaining why L/2 when A is computed on full L. There is a plot of the two parent curves planned, perhaps this will help explain the situation.]
</span>

The deviation elevation at the start of the first half transition is

$$D(0\ m) = (50\ m)^{2}\left( \frac{1}{31250\ m} + \frac{1}{(-538.6086725\ m)^{3}}(0\ m)^{2} \right) = 0.08\ m$$

$$D'(0\ m) = (50\ m)^{2}\left( \frac{2(0\ m)}{(-538.6086725\ m)^{3}}\right) = 0$$

$\theta = 0,\ dx_x = 1, dy_x = 0$

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

<span style="background-color: yellow;color: black">
[todo: consider adding a figure that plots both parent curves. discuss that they both start at 0,0 and don't align at the mid-point. could either adjust origin of second half, or just trim and place - it's far easier to trim and place so we get the placement information from the end of the first half curve - this may be more appropreate in the horizontal section, or maybe graph in both]
</span>

The starting elevation of the second half is the end elevation of the first half. Use the first half parent curve to determine the start of the second half curve.

$$D(50\ m) = (50\ m)^{2}\left( \frac{1}{31250\ m} + \frac{1}{(-538.6086725\ m)^{3}}(50\ m)^{2} \right) = 0.04\ m$$

$$D'(50\ m) = (50\ m)^2\left(\frac{2\cdot 50\ m}{(-538.6086725\ m)^3}\right) = -0.0016$$

$dx_x = \frac{1}{\sqrt{(-0.0016)^2 + 1}} = 0.999998724,\ dy_x = \frac{-0.0016}{\sqrt{(-0.0016)^2 + 1}} = -0.00159999795$

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

From the parent curve 

$s_0 = 50\ m$

$D(50\ m) = (100\ m)^2\left(\frac{1}{(538.6086725\ m)^3}(50\ m)^2 + \frac{-883.8834765}{\left| (-883.8834765\ m)^3 \right|}(50\ m) + \frac{1}{15625\ m} \right) = 0.16\ m$

$D'(50\ m) = (100\ m)^{2}\left( \frac{2(50\ m)}{(538.6086725\ m)^{3}} + \frac{-883.8834765\ m}{\left| (-883.8834765\ m)^{3} \right|} \right) = -0.0064$

$\theta_0 = tan^{-1}(-0.0064) = -0.006399913$

$cos \theta_0 = cos(\theta_0) = 0.999979521$

$sin \theta_0 = sin(\theta_0) = -0.006399869$

**Step 2 — Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

$-(50\ m)(0.999979521) - (0.16\ m)(-0.006399869) = -49.99795207$

$-(50\ m)(-0.006399869) - (0.16\ m)(0.999979521) = 0.159996727$

$$M_N = \begin{bmatrix}
0.999979521 & -0.006399869 & 0 & -49.99795207 \\
0.006399869 & 0.999979521 & 0 & 0.159996727 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

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
 
A point $75\ m$ from the start of the segment is in the second half of the helmert curve. Evaluate the second half parent curve at $s = 75\ m$

$$D(75\ m) = (100\ m)^2\left(\frac{1}{(538.6086725\ m)^3}(75\ m)^2 + \frac{-883.8834765\ m}{\left| (-883.8834765\ m)^3 \right|}(75\ m) + \frac{1}{15625\ m} \right) = 0.04\ m$$

$$D'(75\ m) = (100\ m)^{2}\left( \frac{2(75\ m)}{(538.6086725\ m)^{3}} + \frac{-883.8834765\ m}{\left| (-883.8834765\ m)^{3} \right|} \right) = -0.032$$

$\theta = tan^{-1}(-0.0032) = -0.00319998908$

$dx_x = cos(\theta) = 0.99999488004$

$dx_y = sin(\theta) = -0.00319998362$


$$M_{PC} = \begin{bmatrix} 
0.99999488004 & 0.00319998362 & 0 & 75 \\
-0.00319998362 & 0.99999488004 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$M_c = M_{CSP}M_N M_{PC}$

$$M_c = 
\begin{bmatrix}
0.999998720 & 0.001597727253 & 0 & 50.0 \\
-0.001599997953 & 0.998579530 & 0.0532576429 & 0.04 \\
 0 & -0.0532575749 & 0.998580805 & 0 \\
 0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
0.999979521 & -0.006399869 & 0 & -49.99795207 \\
0.006399869 & 0.999979521 & 0 & 0.159996727 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
0.99999488004 & 0.00319998362 & 0 & 75 \\
-0.00319998362 & 0.99999488004 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

<span style="background-color: pink;color: black">
[todo - verify matrix multiplication - final result is correct from IfcOpenShell - transformation matrix looks wacky]
</span>

$$M_c = \begin{bmatrix}
0.999999684 & 0.000799928774 & 0 & 75.0 \\
-0.000795461553 & 0.999910964 & 0.0133204468 & 0.01 \\
0 & -0.0133203149 & 0.999911281 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

## 4.6 Bloss Curve

A Bloss transition in cant is represented with an `IfcThirdOrderPolynomialSpiral`.

### 4.6.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{A_{3}}{\left| A_{3}^{5} \right|}s^{3} + \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{3A_{3}}{\left| A_{3}^{5} \right|}s^{2} + \frac{2}{A_{2}^{3}}s + \frac{A_{1}}{2\left| A_{1}^{3} \right|} \right)$$

Constant Term

$a_{0} = D_s,\ A_{0} = \frac{L^{\frac{2}{1}}}{\sqrt[0]{|a_0|}}\frac{a_0}{|a_0|} = \frac{L^{2}}{\left| a_{0} \right|}\frac{a_{0}}{\left| a_{0} \right|}$

Linear Term

$a_1 = 0,\ A_{1}$

Quadratic Term

$a_{2} = 3f,\ A_{2} = \frac{L^{\frac{4}{3}}}{\sqrt[3]{|a_2|}}\frac{a_2}{|a_2|}$

Cubic Term

$a_{3} = -2f\ A_{3} = \frac{{L}^{\frac{5}{4}}}{\sqrt[4]{|a_3|}}\frac{a_3}{|a_3|}$

### 4.6.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a Bloss transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.BLOSSCURVE.);
~~~

Compute the parent curve parameters

$D_{s} = \frac{0 + 0.16}{2} = 0.08\ m,\ D_{e} = \frac{0 + 0\ m}{2} = 0.\ m,\ \Delta D = 0.0 - 0.16 = -0.08\ m$

$f = \Delta D = -0.08m$

Constant Term

$a_{0} = -0.08\ m,\ A_{0} = \frac{(100\ m)^{2}}{\left|-0.08\ m \right|}\frac{-0.08\ m}{\left| -0.08\ m \right|} = 125000\ m$

Linear Term

$A_{1} = 0\ m$

Quadratic Term

$a_{2} = 3(-0.08\ m) = -0.24\ m,\ A_{2} = \frac{(100\ m)^{\frac{4}{3}}}{\sqrt[3]{|-0.24\ m|}}\left( \frac{-0.24\ m}{|-0.24\ m|} \right) = -746.9007911\ m$

Cubic Term

$a_{3} = -2f = -2(-0.08\ m) = 0.16\ m,\ A_{3} = \frac{{(100\ m)}^{\frac{5}{4}}}{\sqrt[4]{|0.16\ m|}}\left( \frac{0.16\ m}{| 0.16\ m|} \right) = 500\ m$

The parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCTHIRDORDERPOLYNOMIALSPIRAL(#98,500.00000000000006,-746.90079109286057,$,125000.);
~~~


$$D_0 = D(0\ m) = (100\ m)^2\left( \frac{500\ m}{\left| (500\ m)^{5} \right|}(0\ m)^{3} + \frac{1}{(-746.9007911\ m)^{3}}(0\ m)^{2} + \frac{1}{125000\ m} \right) = 0.08\ m$$

$$D'(0) = 0,\ \theta_0 = 0$$

$dx_x = cos(\theta_0) = 1$

$dy_x = sin(\theta_0) = 0$

The cross-slope at the start of the segment is

$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.16 - 0.0}\right) = 1.464531464$

The cross slope orientation is

$dy_z = cos(\phi_s) = cos(1.464531464) = 0.106064981$

$dz_z = sin(\phi_s) = sin(1.464531464) = 0.994359201$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10606498139220574,0.99435920055192883));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.6.3 Compute Point on Curve

Compute the cant placement matrix for a point 50 m from the start of the curve segment.

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve 

$s_0 = 0,\ D(0\ m) = 0.08\ m, \ D'(0) = 0,\ \theta_0 = 0$

**Step 2 — Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

$$M_N = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir}_p = (1,0,0.),\ \mathbf{Axis}_p = (0.,0.106064981,0.994359201)$

$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0, 0.9943592, -0.10606498)$

$$M_{CSP} = \begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.9943592 & 0.106064981 & 0.08 \\
0 & -0.10606498 & 0.9943592 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

The $\mathbf{\text{Axis}}$ vector is perpendicular to the railhead cross slope line.

$\mathbf{\text{Axis}} = (0.0,\ 0.106064981,\ 0.9943592)$

$\phi_p = tan^{-1}\left(\frac{0.9943592}{0.106064981}\right) = 1.464531464$

With $y$ to the left and $z$ upwards, the vector is nearly vertical, pointing slightly to the left. This is consistent with a curve to the left and the right railhead being superelevated.

**Step 4 — Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$

$$D(50\ m) = (100\ m)^2\left( \frac{500\ m}{\left| (500\ m)^{5} \right|}(50\ m)^{3} + \frac{1}{(-746.9007911\ m)^{3}}(50\ m)^{2} + \frac{1}{125000\ m} \right) = 0.04\ m$$

$$D'(50\ m) = (100\ m)^{2}\left( \frac{500\ m}{\left| (500\ m)^{5} \right|}(50\ m)^{2} + \frac{2}{(-746.9007911\ m)^{3}}(50\ m) + \frac{125000\ m}{2\left| (125000\ m)^{3} \right|} \right) = -0.002$$

$\theta = tan^{-1}(-0.002) = -0.0019997$

$dx_x = cos(\theta) = 0.9999980$

$dy_x = sin(\theta) = -0.0019997$


$$M_{PC} = \begin{bmatrix} 
0.9999980 & 0.0019997 & 0 & 50 \\
-0.0019997 & 0.9999980 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$M_c = M_{CSP}M_N M_{PC}$

$$M_c = 
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0.9943592 & 0.106064981 & 0.08 \\
0 & -0.10606498 & 0.9943592 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
0.9999980 & 0.0019997 & 0 & 50 \\
-0.0019997 & 0.9999980 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

$$M_c = \begin{bmatrix}
0.999999280 & 0.00119830570 & 0.0 & 50.0 \\
-0.00119999914 & 0.998588085 & 0.0531073592 & 0.04 \\
0 & 0 & 0.9985888041 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$


## 4.7 Cosine Curve

A Cosine transition in cant is represented with an `IfcCosineSpiral`.

### 4.7.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{1}{A_{1}}\cos\left( \pi\frac{s}{L} \right)$

$\frac{d}{ds}D(s) = L^{2}\left( -\frac{\pi}{A_1 L}\sin\left( \pi\frac{s}{L} \right) \right)$

$f = \Delta D$

Constant term,

$a_0 = D_s + \frac{f}{2}$

$A_0 = L^{2}\frac{1}{a_0}\frac{a_0}{|a_0|}$

Cosine term, 

$a_1 = -\frac{1}{2} f$

$A_1 = L^{2}\frac{1}{a_1}\frac{a_1}{|a_1|}$

### 4.7.2 Semantic Definition to Geometry Mapping

Consider and alignment segment that has a Cosine transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.COSINECURVE.);
~~~

Compute the parent curve parameters

$D_{s} = \frac{0 + 0.16}{2} = 0.08\ m,\ D_{e} = \frac{0 + 0\ m}{2} = 0.\ m,\ \Delta D = 0.0\ m - 0.08\ m = -0.08\ m$

$a_0 = 0.08\ m + \frac{-0.08\ m}{2} = 0.04$

$A_0 = (100\ m)^{2} \frac{1}{0.04\ m}\frac{0.04\ m}{|0.04\ m|} = 250000\ m$

$a_1 = -\frac{1}{2}(-0.08\ m) = -0.04\ m$

$A_1 = (100\ m)^2\frac{1}{-0.04\ m}\frac{-0.04\ m}{|-0.04\ m|} = 250000\ m$

The parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCCOSINESPIRAL(#98,250000.,250000.);
~~~

$$D(0\ m) = (100\ m)^{2}\left( \frac{1}{250000\ m} + \frac{1}{250000\ m}\cos\left( \pi\frac{0\ m}{100\ m} \right) \right) = 0.08\ m$$

$$ D'(0\ m) = (100\ m)^{2}\left( -\frac{\pi}{(250000\ m)(100\ m)}\sin\left( \pi\frac{0\ m}{100\ m} \right) \right) = 0$$

$\theta_0 = 0,\ dx_x = 1,\ dy_x = 0$

The cross-slope at the start of the segment is

$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.16 - 0.0}\right) = 1.464531464$

The cross slope orientation is

$dy_z = cos(\phi_s) = cos(1.464531464) = 0.106064981$

$dz_z = sin(\phi_s) = sin(1.464531464) = 0.994359201$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10606498139220574,0.99435920055192883));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.7.3 Compute Point on Curve

Compute the cant placement matrix for a point 50 m from the start of the curve segment.

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve 

$s_0 = 0$

$D(0\ m) = 0.08\ m$

$D'(0\ m) = 0$

$\theta_0 = 0$

**Step 2 — Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

$$M_N = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir}_p = (1,0,0.),\ \mathbf{Axis}_p = (0.,0.106064981,0.994359201)$

$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0, 0.9943592, -0.10606498)$

$$M_{CSP} = \begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.9943592 & 0.106064981 & 0.08 \\
0 & -0.10606498 & 0.9943592 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 — Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$

$$D(50\ m) = (100\ m)^{2}\left( \frac{1}{250000\ m} + \frac{1}{250000\ m}\cos\left( \pi\frac{50\ m}{100\ m} \right) \right) = 0.04\ m$$

$$D'(50\ m) = (100\ m)^{2}\left( -\frac{\pi}{(250000\ m)(100\ m)}\sin\left( \pi\frac{50\ m}{100\ m} \right) \right) = -0.00125664$$

$\theta = tan^{-1}(-0.00125664) = -0.001256636$

$dx_x = cos(\theta) = 0.99999921$

$dx_y = sin(\theta) = -0.001256636$

$$M_{PC} = \begin{bmatrix} 
0.99999921 & 0.001256636 & 0 & 50 \\
-0.001256636 & 0.99999921 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$M_c = M_{CSP}M_N M_{PC}$

$$M_c = 
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0.9943592 & 0.106064981 & 0.08 \\
0 & -0.10606498 & 0.9943592 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
0.99999921 & 0.001256636 & 0 & 50 \\
-0.001256636 & 0.99999921 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

$$M_c = \begin{bmatrix}
1 & 0 & 0 & 50 \\
0 & 0.9985888041 & 0.0531074357 & 0.04 \\
0 & -0.05310743572 & 0.998588804 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$


<span style="background-color: yellow;color: black">
[todo - check the matrix multiplication]
</span>

## 4.8 Sine Curve

A Sine transition in cant is represented with an `IfcSineSpiral`

### 4.8.1 Parent Curve Parametric Equations

The deviation elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{A_{1}}{\left| A_{1} \right|}\left( \frac{1}{A_{1}} \right)^{2}s + \frac{1}{A_{2}}\sin\left( 2\pi\frac{s}{L} \right)$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{A_{1}}{\left| A_{1} \right|}\left( \frac{1}{A_{1}} \right)^{2} + \frac{2\pi}{LA_{2}}\cos\left( 2\pi\frac{s}{L} \right) \right)$$

Constant term: 
$$a_0 = D_s$$
$$A_0 = L^2\frac{1}{a_0}\frac{a_0}{|a_0|} $$

Linear term: 

$$a_1 = f$$
$$A_1 = L^{\frac{3}{2}}\frac{1}{\sqrt{|a_1|}}\frac{a_1}{|a_1|} $$

Sine term: 
$$a_2 = -\frac{1}{2\pi} f$$
$$A_2 = L^2\frac{1}{a_2}\frac{a_2}{|a_2|} $$

### 4.8.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a Sine transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.SINECURVE.);
~~~

Compute the paraent curve parameters

$D_{s} = \frac{0 + 0.16}{2} = 0.08\ m,\ D_{e} = \frac{0 + 0\ m}{2} = 0.\ m,\ \Delta D = 0.0\ m - 0.08\ m = -0.08\ m$

Constant term:
$a_0 = 0.08\ m$

$A_0 = (100\ m)^2\frac{1}{0.08\ m}\frac{0.08\ m}{|0.08\ m|} = 125000\ m$

Linear term:
$a_1 = -0.08\ m$

$A_1 = (100\ m)^{\frac{3}{2}} \frac{1}{\sqrt{| -0.08\ m|}}\frac{-0.08\ m}{| -0.08\ m|} = -3535.533906\ m$

Sine term:
$a_2 = -\frac{1}{2\pi} (0.08\ m) = -0.0127324\ m$

$A_2 = (100\ m)^2\frac{1}{-0.0127324\ m}\frac{-0.0127324\ m}{|-0.0127324\ m|} = 785398.1634\ m$

The parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCSINESPIRAL(#98,785398.16339744814,-3535.533905932738,125000.);
~~~

$$D(0\ m) = (100\ m)^{2}\left(\frac{1}{125000\ m} + \left( \frac{-3535.533906\ m}{| -3535.533906\ m|} \right)\left( \frac{1}{-3535.533906\ m} \right)^{2}(0\ m) + \frac{1}{785398.1634\ m}\sin\left( 2\pi\frac{0\ m}{100\ m} \right) \right) = 0.08\ m$$

$$D'(0\ m) = (100\ m)^{2}\left( \frac{-3535.533906}{\left| -3535.533906 \right|}\left( \frac{1}{-3535.533906} \right)^{2} + \frac{2\pi}{(100\ m)(785398.1634\ m)}\cos\left( 2\pi\frac{0\ m}{100\ m} \right) \right) = 0.$$

$\theta_0 = 0$

$dx_x = cos(\theta_0) = 1$

$dx_y = sin(\theta_0) = 0$

The cross-slope at the start of the segment is

$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr} - D_{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.16 - 0.0}\right) = 1.464531464$

The cross slope orientation is

$dy_z = cos(\phi_s) = cos(1.464531464) = 0.106064981$

$dz_z = sin(\phi_s) = sin(1.464531464) = 0.994359201$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10606498139220574,0.99435920055192883));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.8.3 Compute Point on Curve

Compute the cant placement matrix for a point 50 m from the start of the curve segment.

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve 

$$D(0\ m) = \frac{(100\ m)^{2}}{125000\ m} + \left( \frac{-3535.533906\ m}{| -3535.533906\ m|} \right)\left( \frac{1}{-3535.533906\ m} \right)^{2}(0\ m)(100\ m)^{2} + \frac{(100\ m)^{2}}{78539.81634\ m}\sin\left( 2\pi\frac{0\ m}{100\ m} \right) = 0.08\ m$$

$$D'(0\ m) = (100\ m)^{2}\left( \frac{-3535.533906}{\left| -3535.533906 \right|}\left( \frac{1}{-3535.533906} \right)^{2} + \frac{2\pi}{(100\ m)(78539.81634\ m)}\cos\left( 2\pi\frac{0\ m}{100\ m} \right) \right) = 0$$

$\theta_0 = 0$

**Step 2 — Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

$$M_N = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir}_p = (1,0,0.),\ \mathbf{Axis}_p = (0.,0.106064981,0.994359201)$

$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0, 0.9943592, -0.10606498)$

$$M_{CSP} = \begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.9943592 & 0.106064981 & 0.08 \\
0 & -0.10606498 & 0.9943592 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 — Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$

$D(50\ m) = \frac{(100\ m)^{2}}{125000\ m} + \left( \frac{-3535.533906\ m}{| -3535.533906\ m|} \right)\left( \frac{1}{-3535.533906\ m} \right)^{2}(50\ m)(100\ m)^{2} + \frac{(100\ m)^{2}}{785398.1634\ m}\sin\left( 2\pi\frac{50\ m}{100\ m} \right) = 0.04\ m$

$$D'(50\ m) = (100\ m)^{2}\left( \frac{-3535.533906}{\left| -3535.533906 \right|}\left( \frac{1}{-3535.533906} \right)^{2} + \frac{2\pi}{(100\ m)(785398.1634\ m)}\cos\left( 2\pi\frac{50\ m}{100\ m} \right) \right) = -0.0016$$

$$M_{PC} = \begin{bmatrix} 
0.99999872 & 0.001599998 & 0 & 50 \\
-0.001599998 & 0.99999872 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$M_c = M_{CSP}M_N M_{PC}$

$$M_c = 
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0.9943592 & 0.106064981 & 0.08 \\
0 & -0.10606498 & 0.9943592 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.08 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
0.99999872 & 0.001599998 & 0 & 50 \\
-0.001599998 & 0.99999872 & 0 & 0.04 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

$$M_c = \begin{bmatrix}
1 & 0 & 0 & 50 \\
0 & 0.9985888041 & 0.0531074357 & 0.04 \\
0 & -0.05310743572 & 0.998588804 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$


<span style="background-color: yellow;color: black">
[todo - check the matrix multiplication]
</span>


## 4.9 Viennese Bend

A Viennese Bend transition in cant is represented with an `IfcSeventhOrderPolynomialSpiral`.

### 4.9.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{A_7}{|A_7^9|}s^7 + \frac{1}{A_6^7}s^6 + \frac{A_5}{|A_5^7|}s^5 + \frac{1}{A_4^5}s^4 + \frac{A_{3}}{\left| A_{3}^{5} \right|}s^{3} + \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{7A_7}{|A_7^9|}s^6 + \frac{6}{A_6^7}s^5 + \frac{5A_5}{|A_5^7|}s^4 + \frac{4}{A_4^5}s^3 + \frac{3A_{3}}{\left| A_{3}^{5} \right|}s^{2} + \frac{2}{A_{2}^{3}}s + \frac{A_{1}}{2\left| A_{1}^{3} \right|} \right)$$

$$D_s = \frac{D_{sl} + D_{sr}}{2},\ D_e = \frac{D_{el} + D_{er}}{2},\ \mathrm{\Delta}D = D_e - D_s$$

$$f = \mathrm{\Delta}D$$

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

### 4.9.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a Viennese Bend transition curve **???**.
<span style="background-color: yellow;color: black">
[todo - finish the description]
</span>

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.10,0.03,.VIENNESEBEND.);
~~~

Compute the parent curve parameters.

$$D_{sl} = 0.0\ m$$
$$D_{el} = 0.0\ m$$
$$D_{sr} = 0.1\ m$$
$$D_{er} = 0.03\ m$$

$$D_s = \frac{0\ m + 0.1\ m}{2} = 0.05\ m, D_e = \frac{0\ m + 0.03\ m}{2} = 0.015\ m,\ \mathrm{\Delta}D = 0.015 - 0.05 = -0.035\ m$$

$$f = \mathrm{\Delta}D = -0.035m$$

Constant Term
$$a_{0} = 0.05\ m, A_{0} = \frac{(100\ m)^{2}}{\left| 0.05\ m \right|}\frac{0.05\ m}{\left| 0.05\ m \right|} = 200000\ m$$

Linear Term
$$a_{1} = 0, A_{1} = 0\ m$$

Quadratic Term

$$a_{2} = 0, A_{2} = 0\ m$$

Cubic Term

$$a_{3} = 0, A_{3} = 0\ m$$

Quartic Term

$$a_{4} = 35(-0.035\ m) = -1.225\ m, A_{4} = \frac{(100\ m)^{\frac{6}{5}}}{\sqrt[5]{\left| -1.225\ m \right|}}\ \frac{-1.225\ m}{\left| -1.225\ m \right|} = -241.1974890085123\ m$$

Quintic Term

$$a_{5} = -84(-0.035\ m) = 2.94\ m, A_{5} = \frac{(100\ m)^{\frac{7}{6}}}{\sqrt[6]{\left| 2.94\ m \right|}}\ \frac{2.94\ m}{\left| 2.94\ m \right|} = 180.0012184608678\ m$$

Sextic Term

$$a_{6} = 70(-0.035\ m)=-2.45\ m, A_{6} = \frac{(100\ m)^{\frac{8}{7}}}{\sqrt[7]{\left| -2.45\ m \right|}}\ \frac{-2.45\ m}{\left|-2.45\ m\right|} = -169.87095595653895\ m$$

Septic Term

$$a_{7} = -20(-0.035\ m) = 0.7\ m, A_{7} = \frac{(100\ m)^{\frac{9}{8}}}{\sqrt[8]{\left| 0.7\ m \right|}}\ \frac{0.7\ m}{\left| 0.7\ m \right|} = 185.93568367635672\ m$$

The parent curve is

~~~
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCSEVENTHORDERPOLYNOMIALSPIRAL(#98,185.93568367635649,-169.87095595653892,180.00121846086768,-241.19748900851218,$,$,$,200000.);
~~~

$$D(0\ m) = (100\ m)^2 \left(\frac{185.93568367635672\ m}{|(185.93568367635672\ m)^9|}(0\ m)^7 + \frac{1}{(-169.87095595653895\ m)^7}(0\ m)^6 + \frac{180.0012184608678\ m}{|(180.0012184608678\ m)^7|}(0\ m)^5 + \frac{1}{(-241.1974890085123\ m)^5}(0\ m)^4  + \frac{1}{200000\ m}\right) = 0.05\ m$$

$D'(0) = 0,\ \theta_0 = 0$

$dx_x = cos(\theta) = 1

$dx_y = sin(\theta) = 0

The cross-slope at the start of the segment is

$\phi_s = tan^{-1}\left(\frac{D_{rh}}{D_{sr}-D{sl}}\right) = tan^{-1}\left(\frac{1.5}{0.1-0.0} \right) = 1.504228163$

The cross slope orientation is

$dy_z = cos(\theta_s) = 0.066519011$

$dz_z = sin(\theta_s) = 0.997785158$

~~~
#100=IFCCARTESIANPOINT((0.,0.050000000000000003,0.));
#101=IFCDIRECTION((0.,0.066519010523773944,0.99778515785660904));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~


### 4.9.3 Compute Point on Curve

Compute the cant placement matrix for a point 50 m from the start of the curve segment.

**Step 1 — Evaluate the parent curve at the trim start**

From the parent curve 

$s_0 = 0$

$D(0\ m) = 0.05\ m$

$D'(0) = 0,\ \theta_0 = 0$

**Step 2 — Form the normalization matrix $M_N$**

$$M_N = \begin{bmatrix}
\cos\theta_0 & \sin\theta_0 & 0 & -s_0\cos\theta_0 - D_0\sin\theta_0 \\
-\sin\theta_0 & \cos\theta_0 & 0 & -s_0\sin\theta_0 - D_0\cos\theta_0 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

$$M_N = \begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.05 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

**Step 3 — Form the curve segment placement matrix $M_{CSP}$**

$\mathbf{RefDir}_p = (1,0,0.),\ \mathbf{Axis}_p = (0.,0.06651901,0.99778516)$

$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0, 0.99778516, -0.06651901)$

$$M_{CSP} = \begin{bmatrix} 
1 & 0 & 0 & 0 \\
0 & 0.99778516 & 0.06651901 & 0.05 \\
0 & -0.06651901 & 0.99778516 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

**Step 4 — Evaluate and map each point**

Evaluate the parent curve at $s = 50\ m$


$D(50\ m) = (100\ m)^2 \left(\frac{185.93568367635672\ m}{|(185.93568367635672\ m)^9|}(50\ m)^7 + \frac{1}{(-169.87095595653895\ m)^7}(50m)^6 + \frac{180.0012184608678\ m}{|(180.0012184608678\ m)^7|}(50\ m)^5 + \frac{1}{(-241.1974890085123\ m)^5}(50\ m)^4  + \frac{1}{200000\ m}\right) = 0.0325\ m$

$D'(50\ m) = (100\ m)^2 \left(7\frac{185.93568367635672\ m}{|(185.93568367635672\ m)^9|}(50\ m)^6 + \frac{6}{(-169.87095595653895\ m)^7}(50m)^5 + 5\frac{180.0012184608678\ m}{|(180.0012184608678\ m)^7|}(50\ m)^4 + 4\frac{1}{(-241.1974890085123\ m)^5}(50\ m)^3\right) = -0.00076525$

$\theta = -0.00076562$

$dx_x = cos(\theta) = 0.999999707$

$dy_x = sin(\theta) = -0.00076562$

$$M_{PC} = \begin{bmatrix} 
0.999999707 & 0.00076562 & 0 & 50 \\
-0.00076562 & 0.999999707 & 0 & 0.0325 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Apply the normalization and placement in sequence:

$M_c = M_{CSP}M_N M_{PC}$


$$M_c = 
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 0.99778516 & 0.06651901 & 0.05 \\
0 & -0.06651901 & 0.99778516 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0 \\
0 & 1 & 0 & -0.05 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
\begin{bmatrix}
0.999999707 & 0.00076562 & 0 & 50 \\
-0.00076562 & 0.999999707 & 0 & 0.0325 \\
0 & 0 & 1 & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}
$$

$$M_c = \begin{bmatrix}
1 & 0 & 0 & 50.0 \\
0 & 0.999445843 & 0.0332779172 & 0.0325 \\
0 & -0.0332779270 & 0.999446136 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$


<span style="background-color: yellow;color: black">
[todo - check the matrix multiplication]
</span>

## 4.10 Combined 3D

<span style="background-color: yellow;color: black">
[todo: do a full cant example]
</span>

## 4.11 Deviation from EnrichIfc4x3 Reference Implementation

The cant calculations in this section deviate from the ones performed by the EnrichIfc4x3
reference implementation. The calculations in the reference implementation, published at
[IFC-Rail-Unit-Test-Reference-Code/EnrichIFC4x3/EnrichIFC4x3/business2geometry
at master · bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code
(github.com)](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/tree/master/EnrichIFC4x3/EnrichIFC4x3/business2geometry), yield coefficients for sine, cosine, clothoid, and polynomial spirals that are not in units of length. The IFC specification is clear that the coefficients have
units of length and are represented by `IfcLengthMeasure`.

The basic form of the coefficient of the $i^{th}$ term is 

$$A_{i} = \frac{L^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{\left| a_{i} \right|}}\frac{a_{i}}{\left| a_{i} \right|}$$

Performing a dimensional analysis with $l$ representing term with length units, we see that the resulting coefficient $A_{i}$ has units of length. 

$$\frac{l^{\frac{i + 2}{i + 1}}}{\sqrt[(i + 1)]{|l|}}\frac{l}{|l|} = \frac{l^{\frac{i + 2}{i + 1}}}{l^{\frac{1}{i + 1}}} = l^{\frac{i + 2}{i + 1}}l^{\frac{- 1}{(i + 1)}} = l^{\frac{i + 1}{i + 1}} = l$$

The error in the EnrichIfc4x3 reference implementation is illustrated by way of an example. Consider the Bloss Curve example [GENERATED__CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/blob/master/alignment_testset/IFC-WithGeneratedGeometry/GENERATED__CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc). 

The semantic definition of the cant transition segment is 
~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.,0.16,.BLOSSCURVE.);
~~~

The EnrichIfc4x3 reference implementation maps the semantic definition to the geometric representation as follows:

$D_s = \frac{0 + 0}{2} = 0\ m,\ D_e = \frac{0 + 0.16}{2} = 0.08\ m,\ \Delta D = 0.08-0 = 0.08\ m,\ f = \Delta D = 0.08\ m$

Quadratic Term:

$a_{2} = 3f = 3(0.08\ m) = 0.24\ m$

$A_{2} = \frac{(100\ m)}{\sqrt[3]{|0.24\ m|}}\left( \frac{0.24\ m}{|0.24\ m|} \right) = 160.917897\ m^{2/3}$


Cubic Term:

 $a_{3} = -2f = -0.016\ m$
 
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

$D(50\ m) = (100\ m)^2\left( \frac{-500\ m}{|(-500\ m)^5|}(100\ m)^3 + \frac{1}{(746.90079\ m)^3}(100\ m)^2\right) = (100\ m)^2(-0.000002\ m^{-1} + 0.000006\ m^{-1}) = 0.04\ m$

Both approaches give the same result, however, a serious problem emerges if the EnrichIfc4x3 semantic to geometry mapping is mixed with the deviating elevation equation from this guide and visa-versa. Table 4.10-2 compares the results for all the combinations of the sematic to geometry mapping and deviation elevation computations for the Bloss curve evaluated at $s=50\ m$. The deviating elevation can be incorrect proportional (or inversely proportional) to the length of the segment (100 or 1/100 in this example). 

| Mapping | $D(s)$ Equation | $D(50\ m)$ |
|---|---|---|
| EnrichIfc4x3 | EnrichIfc4x3 | $0.04\ m$ |
| This Guide | This Guide | $0.04\ m$ |
| EnrichIfc4x3 | This Guide | $4.0\ m$ |
| This Guide | EnrichIfc4x3 | $0.0004\ m$ |

*Table 4.10-2 — Comparison of deviation elevation results*
