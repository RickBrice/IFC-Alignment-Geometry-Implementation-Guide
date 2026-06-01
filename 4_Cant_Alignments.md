# Chapter 4 — Cant Alignments

## 4.0 Introduction

Cant (also called superelevation) is the transverse inclination of a railway track cross-section: the elevation difference between the two railheads when one rail is raised above the other. By tilting the track into a curve, cant directs a component of gravitational force inward, partially offsetting the centrifugal acceleration experienced by vehicles negotiating the curve. The result is improved ride quality, reduced wheel–rail lateral forces, and the ability to operate at higher speeds through curves without exceeding comfort or safety limits.

Cant is measured as a length — the height difference between railheads — rather than as an angle. The conversion between the two depends on track gauge. `IfcAlignmentCant.RailHeadDistance` supplies the center-to-center distance between railheads, which is the lever arm for this conversion.

The geometric representation of a cant alignment is accomplished with `IfcSegmentedReferenceCurve`. As a subtype of `IfcCompositeCurve`, it is an end-to-start collection of `IfcCurveSegment` segments. Its `BasisCurve` is typically an `IfcGradientCurve`, which supplies the combined horizontal and vertical geometry to which the cant offsets are applied to produce the full 3D track centerline.

Table 4.0-1 maps each `IfcAlignmentCantSegment.PredefinedType` to its corresponding parent curve type used in the geometric representation.

| Business Logic (`IfcAlignmentCantSegment.PredefinedType`) | Geometric Representation (`IfcCurveSegment.ParentCurve`) |
|-----------------------------------|-------------------------------------------------------------------|
| `CONSTANTCANT` | `IfcLine` |
| `LINEARTRANSITION` | `IfcClothoid` |
| `HELMERTCURVE` | `IfcSecondOrderPolynomialSpiral` |
| `BLOSSCURVE` | `IfcThirdOrderPolynomialSpiral` |
| `COSINECURVE` | `IfcCosineSpiral` |
| `SINECURVE` | `IfcSineSpiral` |
| `VIENNESEBEND` | `IfcSeventhOrderPolynomialSpiral` |

*Table 4.0-1 — Mapping of business logic to geometric representation for cant alignment*

This chapter covers:

- The cant segment types in Table 4.0-1 and the geometric curve types that represent them.
- Parametric equations and geometry mapping examples for the curve types in Table 4.0-1.
- An algorithm for composing cant, horizontal, and vertical matrices to produce a full 3D placement frame.
- An implementation checklist in Section 4.13.

## 4.1 Fundamentals

Each `IfcAlignmentCantSegment` is parameterized by distance along the horizontal alignment. The key semantic attributes are `StartDistAlong`, `SegmentLength` (the horizontal length of the cant segment), `StartCantLeft`, `EndCantLeft`, `StartCantRight`, and `EndCantRight`. From these, the deviating elevation $D_s$ at the start and $D_e$ at the end are derived as the averages of their respective left and right rail values (Section 4.1.3). Each cant curve segment uses `IfcAxis2Placement3D` for its placement, in contrast to the 2D placements used for horizontal and vertical segments, because cant carries an out-of-plane cross-slope rotation.

### 4.1.1 Cant Transition

Cant transitions occur when the segment start elevation differs from the
segment start elevation of the next segment. The left section in Figure 4.1.1-1 shows the cross section of a rail line. At the start of the segment, right rail is elevated above the left rail. The y-ordinate of `IfcCurveSegment.Placement.Location` indicates the deviating elevation at the centerline between rails, which is one-half the cant value at the right rail. The y-ordinate of `IfcCurveSegment.Placement.Location` for the next segment indicates a value of 0.0 meaning that the cant transitioned from the starting value to zero over the length of the segment. This transition is the rotation of the right rail about the left rail, and the corresponding change in deviating elevation at the centerline over the length of the segment. The cant transition is shown in the right section of Figure 4.1.1-1 as a linear transition. `IfcCurveSegment.ParentCurve` defines how the transition occurs. Figure 4.1.1-2 shows a non-linear transition of the centerline and right rail deviating elevations. Notice that the deviating elevation of the left rail is constant at zero because it is the point of rotation.

When the segment start elevation is the same as the start of the next segment, the deviating elevation along the length of the segment is constant. This occurs when centrifugal forces are constant or zero, in constant radius curvature and straight sections of the railway, respectively.

![Figure 4.1.1-1 — Two-panel bSI diagram. Left panel: railway track cross-section showing the right rail elevated above the left rail; the IfcCurveSegment.Placement.Location y-ordinate marks the deviating elevation at the centreline (half the cant). Right panel: elevation view showing the linear cant transition along the segment, with IfcGradientCurve, IfcSegmentedReferenceCurve, and placement annotations.](images/Figure_4.1.1-1_Cant_Segment_Cross_Section.jpg)

*Figure 4.1.1-1 - cross section and elevation of a cant segment (source: bSI)*

![Figure 4.1.1-2 — Matplotlib line plot of deviating elevation versus distance for a non-linear cant transition. Two curves show the first half (blue) and second half (orange) of the right-rail deviating elevation profile. The left rail is the rotation pivot and remains at zero.](images/Figure_4.1.1-2_Deviating_Elevation.svg)

*Figure 4.1.1-2 - Deviating elevation of rails*

The railhead cross slope angle is defined by the `IfcCurveSegment.Placement.Axis` attribute. The `Axis` direction is generally upwards. The cross slope angle is measured from the y-axis and orients a vector that is perpendicular to the plane of the railheads. Figure 4.1.1-3 shows the cross slope angle for the transitions in Figure 4.1.1-2. The direction perpendicular to the plane of the railhead is about 1.46 rad at the start of the segment and increases to about 1.57 rad as the rotation decreases. When the left and right rails are at the same elevation the cross slope angle is $\frac{\pi}{2}$.

![Figure 4.1.1-3 — Matplotlib line plot of the rail head cross slope angle (IfcCurveSegment.Placement.Axis direction, in radians) versus distance along a cant segment. The angle transitions from approximately 1.46 rad at the segment start toward π/2 (≈ 1.57 rad) as the rails reach equal elevation.](images/Figure_4.1.1-3_Rail_Head_Cross_Slope.svg)

*Figure 4.1.1-3 - Rail head cross slope*

### 4.1.2 Coordinate System

Figure 4.1.1-1 illustrates the cant coordinate system.

`IfcCurveSegment.Placement.RefDirection` is tangent to the "distance along" the base curve in the horizontal plane, (e.g. `IfcSegmentedReferenceCurve.BaseCurve` => `IfcGradientCurve.BaseCurve` => `IfcCompositeCurve`).

The railway cross section is in the plane defined by `Y` and `Z`. Looking in the positive sense down the alignment, `Y` is towards the left and `Z` is upwards. The cross slope angle is measured clockwise from `Y`.

### 4.1.3 Transition Functions

The transition functions used to shape cant variation have the same functional form as functions used for horizontal transition curves: line, clothoid (linear cant), Helmert, Bloss, cosine, sine, and Viennese bend. In practice, the cant transition type always matches the horizontal transition type and segment length, though IFC does not enforce this constraint.

As an example, the horizontal tangent direction, $\theta(t)$, and the radius of curvature, $\kappa(t)$, for a Helmert curve is a second order polynomial of the form

$$\theta(t) = \frac{t^{3}}{3A_{2}^{3}} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}t^{2} + \frac{t}{A_{0}}$$

$$\kappa(t) = \frac{1}{A_{2}^{3}}t^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}t + \frac{1}{A_{0}}$$

The cant deviating elevation for a Helmert transition is

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

The deviating elevation has the same functional form as the radius of curvature of the horizontal alignment segment. 

In IFC, the semantic cant profile is encoded in `IfcAlignmentCant` and its child `IfcAlignmentCantSegment` entities. The geometric representation is an `IfcSegmentedReferenceCurve`, which evaluates the cant at every point along the alignment and, in conjunction with the horizontal alignment `IfcCompositeCurve` and the vertical alignment `IfcGradientCurve`, produces the full 3D track centerline geometry.

Each `IfcCurveSegment` in an `IfcSegmentedReferenceCurve` is evaluated in a two-dimensional coordinate system whose axes are *distance along the horizontal alignment* $\ell$ and *deviating elevation* $D$. The deviating elevation is the vertical offset applied to the track centerline, away from the gradient curve, to produce the correct cross-slope angle at every point along the segment.

The `StartCantLeft` $D_{sl}$, `EndCantLeft` $D_{el}$, `StartCantRight` $D_{sr}$, and `EndCantRight` $D_{er}$ attributes of `IfcAlignmentCantSegment` determine $D_s$ and $D_e$ as the averages of their respective left and right values:

$$D_s = \frac{D_{sl} + D_{sr}}{2}, \quad D_e = \frac{D_{el} + D_{er}}{2} \quad \Delta D = D_e - D_s$$

The cross-slope angle $\phi$ at a given point is not obtained directly from the parent curve equation; instead it is interpolated between the start and end cross-slope angles encoded in the `Axis` vector of the `IfcCurveSegment.Placement`, using the deviating elevation as the interpolation parameter:

$$\phi(\ell) = \phi_s + \left(\frac{\phi_e - \phi_s}{\Delta D}\right)\bigl(D(\ell) - D_s\bigr)$$

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}} \right)$$

where $\phi_s$ and $\phi_e$ are the cross-slope angles at the start and end of the segment and $D(\ell)$ is the deviating elevation at $\ell$. The cross-slope angle $\phi$ is the angle from the transverse $y$ axis to the projection of the `Axis` vector onto the Y-Z plane. In sections without cant, $\phi = \frac{\pi}{2}$.

The cross-slope angle can be determined from the `Axis` vector as $\phi = \tan^{-1}\left(\frac{Axis.dz}{Axis.dy}\right)$

Together, the distance along, the deviating elevation $D(\ell)$, and the cross-slope angle $\phi(\ell)$ fully specify a 3D placement frame for the track centerline at each $\ell$. Section 4.2 describes an algorithm for constructing that frame and composing it with the horizontal and vertical matrices to produce a 3D position.

All examples use a railhead distance $D_{rh} = 1.5\ m$.

## 4.2 Curve Segment Evaluation Algorithm

Cant segments are evaluated in a two-dimensional "distance along, deviating elevation" $(\ell,D(\ell))$ coordinate system in which $\ell$ is the distance measured along the horizontal `IfcCompositeCurve` and $D(\ell)$ is the deviating elevation: the vertical offset applied to the track centerline to accommodate the cross slope. Unlike horizontal and vertical segments, each cant point also carries a cross slope angle $\phi(\ell)$, making the local frame inherently three-dimensional.

Let $s_0$ = `IfcAlignmentCantSegment.StartDistAlong`.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$M_{CSP}$ is constructed from `IfcCurveSegment.Placement`: $(s_p, D_p)$ is the `Location` (distance along, deviating elevation).

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p$$

$$\mathbf{X}_p = \mathbf{Y}_p \times \mathbf{Axis}_p$$

$$\mathbf{Z}_p = \mathbf{Axis}_p$$

The placement in matrix form is

$$M_{CSP} = \begin{bmatrix} 
X_p.x & Y_p.x & Z_p.x & s_p \\
X_p.y & Y_p.y & Z_p.y & D_p \\
X_p.z & Y_p.z & Z_p.z & 0 \\
0 & 0 & 0 & 1 
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start - $M_{PCS}$

Compute the deviating elevation $D_s = D(s_0)$ and the slope angle $\theta_s = \tan^{-1}(D'(s_0))$.

Compute the cross slope
$$\phi(s_0) = \phi_s + \left(\frac{\phi_e - \phi_s}{\Delta D}\right)(D(s_0) - D_s)$$

Because $D(s_0) = D_s,\ \phi(s_0) = \phi_s$.

Construct the orthogonal vectors

$$\mathbf{X}_{pcs} = (\cos\theta_s,\ \sin\theta_s,\ 0)$$
$$\mathbf{Z}_{pcs} = (0,\ \cos\phi_s,\ \sin\phi_s)$$
$$\mathbf{Y}_{pcs} = \mathbf{Z}_{pcs} \times \mathbf{X}_{pcs}$$
$$\mathbf{Axis}_{pcs} = \mathbf{X}_{pcs} \times \mathbf{Y}_{pcs}$$
$$\mathbf{RefDir}_{pcs} = \mathbf{Y}_{pcs} \times \mathbf{Axis}_{pcs}$$


In matrix form

$$M_{PCS} = \begin{bmatrix}
RefDir_{pcs}.x & Y_{pcs}.x & Axis_{pcs}.x & s_0 \\
RefDir_{pcs}.y & Y_{pcs}.y & Axis_{pcs}.y & D_s \\
RefDir_{pcs}.z & Y_{pcs}.z & Axis_{pcs}.z & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

#### Step 3 — Evaluate the parent curve at the point under consideration, $\ell$ - $M_{PC\ell}$

This step follows the same calculations as Step 2, except $D$ and $D'$ are evaluated at $\ell$.

The resulting matrix is

$$M_{PC\ell} = \begin{bmatrix}
RefDir_{\ell}.x & Y_{\ell}.x & Axis_{\ell}.x & {\ell} \\
RefDir_{\ell}.y & Y_{\ell}.y & Axis_{\ell}.y & D_{\ell} \\
RefDir_{\ell}.z & Y_{\ell}.z & Axis_{\ell}.z & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

The cant frame at $\ell$ is obtained by applying the incremental change in the parent curve — from the trim start to $\ell$ — to the curve segment placement. Because the 4×4 matrices encode both orientation and parameter-space coordinates (distance along, deviating elevation) in column 4, the rotation and translation must be computed separately to prevent the rotation from acting on the position coordinates.

**Rotation**

Let $R_{CSP}$, $R_{PCS}$, and $R_{PC\ell}$ denote the upper-left 3×3 rotation submatrix of $M_{CSP}$, $M_{PCS}$, and $M_{PC\ell}$ respectively. The incremental rotation from trim start to $\ell$ is:

$$\Delta R = R_{PC\ell} \cdot R_{PCS}^T$$

Apply the increment to the curve segment placement:

$$R_c = \Delta R \cdot R_{CSP} = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

Let $\mathbf{T} _{CSP}$, $\mathbf{T} _{PCS}$, and $\mathbf{T} _{PC\ell}$ denote column 4, rows 1–3, of $M_{CSP}$, $M_{PCS}$, and $M_{PC\ell}$ respectively. The incremental translation from trim start to $\ell$ is:

$$\Delta\mathbf{T} = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS}$$

Apply the increment to the curve segment placement:

$$\mathbf{T}_c = \Delta\mathbf{T} + \mathbf{T}_{CSP} = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

Step 5 is performed immediately for this point before moving to the next $\ell$.

#### Step 5 — Combine with horizontal and vertical to produce the 3D placement matrix

The cant result must be combined with the horizontal matrix $M_h$ (evaluated at distance $\ell$ along the `IfcCompositeCurve`) and the vertical matrix $M_v$ (evaluated at the same $\ell$). All three coordinate systems share the distance-along axis, so the positional components of $M_v$ and $M_c$ must be extracted before multiplication and added back afterward to avoid incorrectly rotating the position offsets.

Construct $M^\prime_v$ as described in Section 3.2.

Construct $M^\prime_c$ by zeroing the distance-along $\ell$ component in row 1, column 4 and moving the deviating elevation $D_{\ell}$ from row 2 to row 3 in column 4 of $M_c$:

$${M'}_c = \begin{bmatrix} 
X.x & Y.x & Z.x & 0 \\ 
X.y & Y.y & Z.y & 0 \\ 
X.z & Y.z & Z.z & D_{\ell} \\ 
0 & 0 & 0 & 1 
\end{bmatrix}$$

Extract position vectors from each modified matrix, $M^\prime_v,\ M^\prime_c$, (setting row 4 to zero), then zero column 4 before multiplying:

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

Numerical examples of Steps 1–4 are given in Sections 4.3 through 4.9. A complete worked example including Step 5 is in Section 4.10.

## 4.3 Constant Cant

Cant has a constant deviating elevation and cross-slope angle in rail segments between curves or in the circular portion of curves where the tracks are banked at a constant rate.

The parent curve is `IfcLine`. The slope-intercept form of a line is $y = mx + b$, where $m$ is the slope and $b$ is the $y$-intercept. The derivative is $y' = m$, and the second derivative is $y''= 0$.

In the context of cant, $D(s) = y'(x)$, so the deviating elevation is a constant value, $m$, and the rate of change of the deviating elevation $D'(s) = y''(x) = 0$.

### 4.3.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$D(s) = D_s = D_e$$

$$\frac{d}{ds}D(s) = D'(s) = 0.0$$

### 4.3.2 Semantic Definition to Geometry Mapping

Consider 100 m long segment of a railway that is turning towards the left. The right rail is raised 0.16 m through the circular portion of the curve. The semantic definition is

~~~
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 0.16, 0.16, .CONSTANTCANT.);
~~~

$$D_s = \frac{0.0\ m + 0.16\ m}{2} = 0.08\ m$$

$$D_e = \frac{0.0\ m + 0.16\ m}{2} = 0.08\ m$$

$$\Delta D = D_e - D_s = 0.08\ m - 0.08\ m = 0.0\ m$$

The parent curve has a constant deviating elevation at $0.08\ m$ and a slope of $0.0$.

Define the parent curve as an `IfcLine` passing through (0,0) in the direction (1,0).

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCVECTOR(#97,1.);
#99=IFCLINE(#96,#98);
~~~

The `IfcCurveSegment` trims a segment from the parent curve. The curve segment placement must capture the cross-slope rotation between the rail heads. For this reason the placement is an `IfcAxis2Placement3D` (instead of `IfcAxis2Placement2D` used for horizontal and vertical representations).

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10666666666666667,0.99429483666678176));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.3.3 Compute Point on Curve

Compute the placement matrix for a point $\ell = 50\ m$ from the start of the curve segment using the algorithm in Section 4.2.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (1,\ 0,\ 0)$$

$$\mathbf{Axis}_p = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ 0.994295,\ -0.106667)$$

$$M_{CSP} = \begin{bmatrix} 
        1 &         0 &         0 &         0 \\
       0 &  0.994295 &  0.106667 &      0.08 \\
        0 & -0.106667 &  0.994295 &         0 \\
        0 &         0 &         0 &         1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$s_0 = 0,\ D(0) = 0\ m,\ D'(0) = 0,\ \theta_s = 0$$

For constant cant $\Delta D = 0$, so $\phi(s_0) = \phi_s = \phi_e = 1.463926346$.

$$\mathbf{X}_s = (1,\ 0,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0,\ 0.994295,\ -0.106667)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (1,\ 0,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
        1 &        0 &         0 &         0 \\
        0 &  0.994295 &  0.106667 &         0 \\
        0 & -0.106667 &  0.994295 &         0 \\
        0 &         0 &         0 &         1
\end{bmatrix}$$

#### Step 3 — Evaluate the parent curve at $\ell = 50\ m$ — $M_{PC\ell}$

$$D(50\ m) = 0\ m,\ D'(50\ m) = 0,\ \theta_{\ell} = 0$$

Since $\Delta D = 0$, $\phi(50\ m) = \phi_s = 1.463926346$.

$$\mathbf{X} _{\ell} = (1,\ 0,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0,\ 0.994295,\ -0.106667)$$

$$M_{PC\ell} = \begin{bmatrix}
        1 &        0 &         0 &        50 \\
        0 &  0.994295 &  0.106667 &         0 \\
        0 & -0.106667 &  0.994295 &         0 \\
        0 &         0 &         0 &         1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_{CSP} = \begin{bmatrix} 
        1 &         0 &         0 \\
       0 &  0.994295 &  0.106667 \\
        0 & -0.106667 &  0.994295
\end{bmatrix}$$

$$R_{PCS} = \begin{bmatrix}
        1 &        0 &         0 \\
        0 &  0.994295 &  0.106667 \\
        0 & -0.106667 &  0.994295
\end{bmatrix}$$

$$R_{PC\ell} = \begin{bmatrix}
        1 &        0 &         0 \\
        0 &  0.994295 &  0.106667 \\
        0 & -0.106667 &  0.994295
\end{bmatrix}$$

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}=
\begin{bmatrix}
        1 &        0 &         0 \\
        0 &  0.994295 &  0.106667 \\
        0 & -0.106667 &  0.994295
\end{bmatrix}
 \begin{bmatrix}
        1 &        0 &         0 \\
        0 &  0.994295 & -0.106667 \\
        0 &  0.106667 &  0.994295
\end{bmatrix}
\begin{bmatrix} 
        1 &         0 &         0 \\
       0 &  0.994295 &  0.106667 \\
        0 & -0.106667 &  0.994295
\end{bmatrix}
$$

$$R_c = 
\begin{bmatrix} 
        1 &         0 &         0 \\
       0 &  0.994295 &  0.106667 \\
        0 & -0.106667 &  0.994295
\end{bmatrix}
$$

**Translation**

$$\mathbf{T_c} = \mathbf{T_{CSP}} + \mathbf{T_{PC\ell}} - \mathbf{T_{PCS}}$$

$$\mathbf{T_{CSP}} = (0,\ 0.08,\ 0)^T$$
$$\mathbf{T_{PC\ell}} = (50,\ 0,\ 0)^T$$
$$\mathbf{T_{PCS}} = (0,\ 0,\ 0)^T$$

$$\mathbf{T_c} = (0,\ 0.08,\ 0)^T + (50,\ 0,\ 0)^T - (0,\ 0,\ 0)^T$$

$$\mathbf{T_c} = (50,\ 0.08,\ 0\ ,\ 0)^T$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix} 
        1 &         0 &         0 &        50 \\
        0 &  0.994295 &  0.106667 &      0.08 \\
        0 & -0.106667 &  0.994295 &         0 \\
        0 &         0 &         0 &         1
\end{bmatrix}$$

## 4.4 Linear Transition

A linear transition in cant is represented with an `IfcClothoid`.

### 4.4.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s\ $$

$$\frac{d}{ds}D(s) = L^{2}\frac{A_{1}}{\left| A_{1}^{3} \right|}$$

$$a_{0} = D_{s},\ A_{0} = \frac{L^{2/1}}{a_{0}^{1}}\frac{a_0}{\left|a_0\right|},\ A_{0} = \frac{L^{2}}{a_{0}}$$

$$a_1 = \Delta D,\ A_1 = \frac{L^{\frac{3}{2}}}{{\left| a_{1} \right|}^{\frac{1}{2}}}\frac{a_{1}}{\left| a_{1} \right|}$$

$A_1$ is the clothoid constant.

### 4.4.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a clothoid transition curve towards the left. The track banks at a constantly increasing rate resulting in a linear deviation in the right rail elevation relative to the left rail. The right rail raises 160 mm over the 100 m segment length.

The semantic representation of the cant alignment is

~~~
#64 = IFCALIGNMENTCANTSEGMENT($, $, 0., 100., 0., 0., 0.16, 0., .LINEARTRANSITION.);
~~~

Compute the parent curve parameters.

$$D_{sl} = 0\ m\quad D_{el} = 0\ m$$

$$D_{sr} = 0.16\ m\quad D_{er} = 0\ m$$

$$D_s = \frac{(0.16 + 0)}{2} = 0.08\ m$$

$$D_e = \frac{(0 + 0)}{2} = 0\ m$$

$$\Delta D = D_e - D_s = 0.0 - 0.08 = -0.08\ m$$

$$a_0 = D_s = 0.08\ m,\ A_0 = \frac{(100\ m)^2}{0.08\ m} = 125000\ m$$

$$a_{1} = \Delta D = -0.08\ m \quad A_{1} = \frac{{(100\ m)}^{\frac{3}{2}}}{{\left|-0.08\ m\right|}^{\frac{1}{2}}}\frac{-0.08\ m}{\left|-0.08\ m\right|} = -3535.533906\ m$$

The clothoid parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCCLOTHOID(#98,-3535.533905932738);
~~~

The cant segment begins with a deviating elevation of

$$D(0\ m) = (100\ m)^2\left(\frac{1}{125000} + \frac{-3535.533906}{\left|-3535.533906\right|^3}(0\ m)\right) = 0.08\ m$$

The slope at the start of the segment is

$$D'(0\ m) = (100\ m)^{2}\frac{-3535.533906}{\left| -3535.533906^{3} \right|} = -0.0008$$

$$\theta_0 = \tan^{-1}(-0.0008) = -0.00079999$$

$$dx_x = \cos(\theta_0) = 0.999999680$$

$$dy_x = \sin(\theta_0) = -0.000799999744$$

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10666666666666667,0.99429483666678176));
#102=IFCDIRECTION((0.999999680,-0.000799999744,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.4.3 Compute Point on Curve

Compute the cant placement matrix for a point $\ell = 50\ m$ from the start of the curve segment using the algorithm in Section 4.2.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (0.9999996800,\ -0.000799999744,\ 0)$$

$$\mathbf{Axis}_p = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0.0007954871,\ 0.9943588828,\ -0.1060649471)$$

$$M_{CSP} = \begin{bmatrix}
    0.999999683641039 &   0.00079543561769016 &                     0 &                     0 \\
-0.000790897527570178 &       0.9942945221127 &     0.106666666666667 &                  0.08 \\
 8.48464658869504e-05 &    -0.106666632921711 &     0.994294836666782 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$s_0 = 0,\ D(0) = 0\ m,\ D'(0) = -0.0008,\ \theta_s = -0.00079999$$

$$dx_x = \cos(\theta_s) = \cos(-0.00079999) = 0.999999680$$

$$dx_y = \sin(\theta_s) = \sin(-0.00079999) = -0.000799999744$$

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

$$\mathbf{X}_s = (0.999999680,\ -0.000799999744,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.106666667,\ 0.994294837)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0.0007954871,\ 0.9943588828,\ -0.1060649471)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (0.0000849,\ 0.106666667,\ 0.994294837)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (0.999999680,\ -0.000799999744,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
      0.999999999968 & 7.95435869307971e-06 &  8.5333333327872e-07 &                    0 \\
 -7.999999999744e-06 &    0.994294836634964 &     0.10666666665984 &                   -0 \\
                   0 &   -0.106666666663253 &    0.994294836666782 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 3 — Evaluate the parent curve at $\ell = 50\ m$ — $M_{PC\ell}$

$$D(50\ m) = 0.04\ m,\ D'(50\ m) = -0.0008,\ \theta_{\ell} = -0.00079999$$

$\phi_e = \cos^{-1}(\frac{0.0}{1.5}) = \frac{\pi}{2}$ (both rails level at segment end)

$$\phi(50\ m) = 1.463926346 + \left(\frac{\frac{\pi}{2} - 1.463926346}{-0.08}\right)(0.04 - 0.08) = 1.517361336$$

$$\mathbf{X} _{\ell} = (0.999999680,\ -0.000799999744,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.053107436,\ 0.998588804)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0.000798871,\ 0.998588485,\ -0.053107419)$$

$$M_{PC\ell} = \begin{bmatrix}
      0.999999999968 & 7.98858152422898e-06 & 4.27276522453101e-07 &                   50 \\
 -7.999999999744e-06 &    0.998572690528623 &   0.0534095653066376 &                -0.04 \\
                   0 &  -0.0534095653083467 &    0.998572690560578 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

$$\mathbf{T}_c = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix}
    0.999999683613726 &  0.000795469840510406 &  -4.2605681082593e-07 &                    50 \\
-0.000794311703395977 &      0.99857237464344 &    0.0534095653134254 &                  0.04 \\
 4.29111469629201e-05 &   -0.0534095480769501 &      0.99857269055985 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

## 4.5 Helmert Curve

Like the Helmert transition spiral, the Helmert cant semantic definition maps to two `IfcCurveSegment` instances for the geometric representation. The parent curve is `IfcSecondOrderPolynomialSpiral`.

### 4.5.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{2s}{A_{2}^{3}} + \frac{A_{1}}{\left| A_{1}^{3} \right|} \right)$$

The polynomial coefficients carry a second subscript to indicate first half $1$, and second half $2$. For example, $A_{21}$ is coefficient $A_2$ for the first half and $A_{02}$ is coefficient $A_0$ for the second half. 

In the first half of the cant transition

Constant Term:

 $a_{01} = 4D_{s}$,
$$A_{01} = \frac{L^{2}}{\left| a_{01} \right|}\frac{a_{01}}{\left| a_{01} \right|}$$

Linear Term: 

$a_{11} = 0$,
$$A_{11} = \frac{L^{\frac{3}{2}}}{{\left| a_{11} \right|}^{\frac{1}{2}}}\frac{a_{11}}{\left| a_{11} \right|} = 0$$

Quadratic Term:

$a_{21} = 8\Delta D$,
$$A_{21} = \frac{L^{4/3}}{{\left| a_{21} \right|}^{\frac{1}{3}}}\frac{a_{21}}{\left| a_{21} \right|}$$

In the second half

Constant Term: 

$a_{02} = -4\Delta D + 4D_{s}$,
$$A_{02} = \frac{L^{2}}{\left| a_{02} \right|}\frac{a_{02}}{\left| a_{02} \right|}$$

Linear Term: 

$a_{12} = 16\Delta D$,
$$A_{12} = \frac{L^{\frac{3}{2}}}{{\left| a_{12} \right|}^{\frac{1}{2}}}\frac{a_{12}}{\left| a_{12} \right|}$$

Quadratic Term: 

$a_{22} = -8\Delta D$,
$$A_{22} = \frac{L^{\frac{4}{3}}}{{\left| a_{22} \right|}^{\frac{1}{3}}}\frac{a_{22}}{\left| a_{22} \right|}$$


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

First half:

$$a_{01} = 4D_{s} = 4(0.08\ m) = 0.32\ m$$

$$A_{01} = \frac{L^{2}}{\left| a_{01} \right|}\frac{a_{01}}{\left| a_{01} \right|} = \frac{(100\ m)^{2}}{\left|0.32\ m\right|}\frac{0.32\ m}{\left|0.32\ m\right|} = 31250\ m$$

$$a_{11} = 0,\ A_{11} = 0$$

$$a_{21} = 8\Delta D = 8(-0.08\ m) = -0.64\ m$$

$$A_{21} = \frac{L^{4/3}}{{\left| a_{21} \right|}^{\frac{1}{3}}}\frac{a_{21}}{\left| a_{21} \right|} = \frac{(100\ m)^\frac{4}{3}}{{\left| - 0.64\ m\right|}^{\frac{1}{3}}}\frac{-0.64\ m}{\left|-0.64\ m\right|} = -538.6086725\ m$$

The first half parent curve `IfcSecondOrderPolynomialSpiral` is

~~~
#104=IFCCARTESIANPOINT((0.,0.));
#105=IFCDIRECTION((1.,0.));
#106=IFCAXIS2PLACEMENT2D(#104,#105);
#107=IFCSECONDORDERPOLYNOMIALSPIRAL(#106,-538.60867250797071,$,31250.);
~~~

Determine the first half placement and trimming.

> **Note:** The length of the first half curve is $L_1 = 50\ m$, half the length of the full Helmert transition.

The spiral coefficients $A_{01}$ and $A_{21}$ are computed from the **full** transition
length $L = 100\ m$. The evaluation formula, by contrast, multiplies by the curve segment
length squared — $(L_1)^2 = (50\ m)^2$ — because $L_1 = 50\ m$ is the trim length of
the first-half curve segment. These two lengths work together by design. The $A$
coefficients fix the boundary conditions of the deviating elevation profile at $s = 0$,
$s = L/2$, and $s = L$ relative to the complete $100\ m$ transition. Using $(L_1)^2$
in the evaluation then scales those boundary conditions correctly to physical distances
within the trimmed half. Substituting $A_{01} = L^2/a_{01}$ confirms this:

$$\left(\frac{L}{2}\right)^2 \cdot \frac{a_{01}}{L^2} = \frac{a_{01}}{4} = \frac{4D_s}{4} = D_s$$

Figure 4.5.2-1 illustrates this geometrically. Each parent curve is drawn solid over
the portion used by its curve segment and dashed beyond the trim boundary. The dashed
extension of the first-half curve diverges from the second-half curve after $s = 50\ m$,
confirming that the two polynomials are distinct — each is correct only within its own
half.

The deviating elevation at the start of the first half transition is

$$D(0\ m) = (50\ m)^{2}\left( \frac{1}{31250\ m} + \frac{1}{(-538.6086725\ m)^{3}}(0\ m)^{2} \right) = 0.08\ m$$

$$D'(0\ m) = (50\ m)^{2}\left( \frac{2(0\ m)}{(-538.6086725\ m)^{3}}\right) = 0$$

$$\theta = 0,\ dx_x = 1, dy_x = 0$$

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

~~~
#108=IFCCARTESIANPOINT((0.,0.08,0.));
#109=IFCDIRECTION((0.,0.10666666666666667,0.99429483666678176));
#110=IFCDIRECTION((1.,0.,0.));
#111=IFCAXIS2PLACEMENT3D(#108,#109,#110);
#112=IFCCURVESEGMENT(.CONTINUOUS.,#111,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(50.),#107);
~~~

Second half:

$$a_{02} = -4\Delta D + 4D_{s} = -4(-0.08\ m) + 4(0.08)\ m = 0.64\ m$$

$$A_{02} = \frac{L^{2}}{\left| a_{02} \right|}\frac{a_{01}}{\left| a_{02} \right|} = \frac{(100\ m)^{2}}{\left|0.64\ m\right|}\frac{0.64\ m}{\left|0.64\ m\right|} = 15625\ m$$

$$a_{12} = 16\Delta D = 16(-0.08\ m) = -1.28\ m$$

$$A_{12} = \frac{L^{\frac{3}{2}}}{{\left| a_{12} \right|}^{\frac{1}{2}}}\frac{a_{12}}{\left| a_{12} \right|} = \frac{(100\ m)^{\frac{3}{2}}}{{\left|-1.28\ m\right|}^{\frac{1}{2}}}\frac{-1.28\ m}{\left|-1.28\ m\right|} = -883.8834765\ m$$

$$a_{22} = -8\Delta D = -8(-0.08\ m) = 0.64\ m$$

$$A_{22} = \frac{L^{\frac{4}{3}}}{{\left| a_{22} \right|}^{\frac{1}{3}}}\frac{a_{22}}{\left| a_{22} \right|} = \frac{(100\ m)^{\frac{4}{3}}}{{\left|0.64\ m\right|}^{\frac{1}{3}}}\frac{0.64\ m}{\left|0.64\ m\right|} = 538.6086725\ m$$

Figure 4.5.2-1 shows the first and second half parent curves.

![Figure 4.5.2-1 — Matplotlib XY plot of two IfcSecondOrderPolynomialSpiral parent curves for a Helmert cant transition, showing the first half (blue) and second half (orange). Dashed lines extend each curve beyond its active range to show the suppressed portion of the full spiral.](images/Figure_4.5.2-1_Helmert_Cant_Parent_Curves.svg)

*Figure 4.5.2-1 - `IfcSecondOrderPolynomialSpiral` parent curves. The dashed lines represent the projection of the parent curve over the full length of the semantic segment.*

The second half parent curve `IfcSecondOrderPolynomialSpiral` is

~~~
#113=IFCCARTESIANPOINT((0.,0.));
#114=IFCDIRECTION((1.,0.));
#115=IFCAXIS2PLACEMENT2D(#113,#114);
#116=IFCSECONDORDERPOLYNOMIALSPIRAL(#115,538.60867250797071,-883.8834764831845,15625.);
~~~

Determine the second half placement and trimming.

The starting elevation of the second half is the end elevation of the first half. Use the first half parent curve to determine the start of the second half curve.

$$D(50\ m) = (50\ m)^{2}\left( \frac{1}{31250\ m} + \frac{1}{(-538.6086725\ m)^{3}}(50\ m)^{2} \right) = 0.04\ m$$

$$D'(50\ m) = (50\ m)^2\left(\frac{2\cdot 50\ m}{(-538.6086725\ m)^3}\right) = -0.0016$$

$$dx_x = \frac{1}{\sqrt{(-0.0016)^2 + 1}} = 0.999998724,\ dy_x = \frac{-0.0016}{\sqrt{(-0.0016)^2 + 1}} = -0.00159999795$$

The cant at the end of the first half is one-half of the total cant change over the length of the transition segment.

$$\frac{(D_{sr} - D_{sl}) + (D_{er} - D_{el})}{2} = \frac{(0.16 - 0.0) + (0.0 + 0.0)}{2} = 0.08$$

The cross slope at the end of the first half is 

$$\phi(50\ m) = \cos^{-1}\left(\frac{0.08}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.08}{1.5}\right) = 1.517437677$$

$$dy_z = \cos(\phi_s) = \cos(1.517437677) = 0.053333333$$

$$dz_z = \sin(\phi_s) = \sin(1.517437677) = 0.998576765$$

The trimming begins at $50\ m$ and progresses for a length of $50\ m$ for the second half segment.

~~~
#117=IFCCARTESIANPOINT((50.,0.04,0.));
#118=IFCDIRECTION((0.,0.053333333333333337,0.99857676497881498));
#119=IFCDIRECTION((0.9999987200024576,-0.0015999979520039342,0.));
#120=IFCAXIS2PLACEMENT3D(#117,#118,#119);
#121=IFCCURVESEGMENT(.CONTINUOUS.,#120,IFCLENGTHMEASURE(50.),IFCLENGTHMEASURE(50.),#116);
~~~

### 4.5.3 Compute Point on Curve

Compute the cant placement matrix for a point $75\ m$ from the start of the curve segment using the algorithm in Section 4.2. $75\ m$ falls in the second half of the Helmert
transition, $\ell = 75\ m - 50\ m = 25\ m$.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (0.9999987200024576,\ -0.0015999979520039342,\ 0.)$$

$$\mathbf{Axis}_p = (0.,\ 0.053333333333333337,\ 0.99857676497881498)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0.00159772,\ 0.998575,\  -0.0533333)$$

$$M_{CSP} = \begin{bmatrix}
   0.999998723643333 &  0.00159772078470193 &                    0 &                   50 \\
-0.00159544685252706 &    0.998575490438703 &   0.0533333333333333 &                 0.04 \\
8.52117751841028e-05 &  -0.0533332652609777 &    0.998576764978815 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$D_s = D(50\ m) = (50\ m)^{2}\left(\frac{1}{(538.6086725\ m)^{3}}(50\ m)^{2} + \frac{-883.8834765\ m}{\left| (-883.8834765\ m)^{3} \right|}(50\ m) + \frac{1}{15625\ m}\right) = 0.16\ m$$

$$D'(s) = D'(50\ m) = (50\ m)^{2}\left( \frac{(2)(50\ m)}{(538.6086725\ m)^{3}} + \frac{(-883.8834765\ m)}{\left| (-883.8834765\ m)^{3} \right|} \right) = -0.0016$$

$$dx_x = \frac{1}{\sqrt{(-0.0016)^2 + 1}} = 0.99999872$$

$$dy_x = \frac{-0.0064}{\sqrt{(-0.0016)^2 + 1}} = -0.001599998$$

$$\phi_s = \tan^{-1}\left(\frac{dz_z}{dz_y} \right) = \tan^{-1}\left(\frac{ 0.99858080467782662}{0.053257642916150753} \right) = 1.517513475$$

$$\mathbf{X}_s = (0.99999872,\ -0.001599998,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.053257642916150753,\ 0.99858080467782662)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0.0015977272423949591,\ 0.99857952649685078,\ -0.053257574746498774)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (8.5212010523094261e-05,\ 0.053257506576933983,\ 0.99858080467782662)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (0.99999872,\ -0.001599998,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
   0.999998720002458 &  0.00159772077888481 &  8.5333114880559e-05 &                    0 \\
-0.00159999795200393 &     0.99857548680301 &   0.0533331968003495 &   0.0400000000000001 \\
                   0 &  -0.0533332650667977 &    0.998576764978815 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 3 — Evaluate the parent curve at $\ell = 25\ m$ — $M_{PC\ell}$

Add curve start $25 + 50 = 75\ m$.

$$D_{\ell} = D(75\ m) = (50\ m)^{2}\left(\frac{1}{(538.6086725\ m)^{3}}(75\ m)^{2} + \frac{-883.8834765\ m}{\left| (-883.8834765\ m)^{3} \right|}(75\ m) + \frac{1}{15625\ m}\right) = 0.01\ m$$

$$D'_{\ell} = D'(75\ m) = (50\ m)^{2}\left( \frac{(2)(75\ m)}{(538.6086725\ m)^{3}} + \frac{(-883.8834765\ m)}{\left| (-883.8834765\ m)^{3} \right|} \right) = -0.0008$$

$$dx_x = \cos(\theta) = 0.99999968000015360$$

$$dx_y = \sin(\theta) = -0.00079999974400011946$$

$$\phi(\ell) = 1.517437677 + \left(\frac{\frac{\pi}{2} - 1.517437677}{-0.04}\right)(0.01 - 0.08) = 1.5574756139049735$$

$$dz_y = \cos(1.5574756139049735) = 0.013320318952445506$$

$$dz_z = \sin(1.5574756139049735) = 0.99991128061593804$$

$$\mathbf{X} _{\ell} = (0.99999968000015360,\ -0.00079999974400011946,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.013320318952445506,\ 0.99991128061593804)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0.00079992876851558200,\ 0.99991096064448182,\ -0.013320314689945486)$$

$$\mathbf{Axis} _{\ell} = \mathbf{X} _{\ell} \times \mathbf{Y} _{\ell} = (1.0656248341957419e-05,\ 0.013320310427446832,\ 0.99991128061593804)$$

$$\mathbf{RefDir} _{\ell} = \mathbf{Y} _{\ell} \times \mathbf{Axis} _{\ell} = (0.99999968000015360,\ -0.00079999974400011946,\ 0)$$

$$M_{PC\ell} = \begin{bmatrix}
    0.999999680000154 &  0.000799928566440938 &  1.06714066139122e-05 &                    25 \\
-0.000799999744000119 &     0.999910708051177 &    0.0133392582673903 &    0.0100000000000002 \\
                    0 &   -0.0133392625359523 &     0.999911028022552 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

$$\mathbf{T}_c = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix}
    0.999999677269901 &  0.000799928563528498 &  -7.4661790264052e-05 &                    75 \\
-0.000798861459176414 &     0.999910704410622 &    0.0133393264368146 &    0.0100000000000001 \\
 8.53256315305252e-05 &   -0.0133392624873857 &     0.999911020741441 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

## 4.6 Bloss Curve

A Bloss transition in cant is represented with an `IfcThirdOrderPolynomialSpiral`.

### 4.6.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{A_{3}}{\left| A_{3}^{5} \right|}s^{3} + \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{3A_{3}}{\left| A_{3}^{5} \right|}s^{2} + \frac{2}{A_{2}^{3}}s + \frac{A_{1}}{2\left| A_{1}^{3} \right|} \right)$$

Constant Term

$$a_{0} = D_s,\ A_{0} = \frac{L^{\frac{2}{1}}}{{\left|a_0\right|}^{1}}\frac{a_0}{\left|a_0\right|} = \frac{L^{2}}{\left| a_{0} \right|}\frac{a_{0}}{\left| a_{0} \right|}$$

Linear Term

$$a_1 = 0,\ A_{1}$$

Quadratic Term

$$a_{2} = 3\Delta D,\ A_{2} = \frac{L^{\frac{4}{3}}}{{\left|a_2\right|}^{\frac{1}{3}}}\frac{a_2}{\left|a_2\right|}$$

Cubic Term

$$a_{3} = -2\Delta D,\ A_{3} = \frac{{L}^{\frac{5}{4}}}{{\left|a_3\right|}^{\frac{1}{4}}}\frac{a_3}{\left|a_3\right|}$$

### 4.6.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a Bloss transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.BLOSSCURVE.);
~~~

Compute the parent curve parameters

$$D_{s} = \frac{0 + 0.16}{2} = 0.08\ m,\ D_{e} = \frac{0 + 0\ m}{2} = 0.\ m,\ \Delta D = 0.0 - 0.16 = -0.08\ m$$

Constant Term

$$a_{0} = -0.08\ m,\ A_{0} = \frac{(100\ m)^{2}}{\left|-0.08\ m \right|}\frac{-0.08\ m}{\left| -0.08\ m \right|} = 125000\ m$$

Linear Term

$$A_{1} = 0\ m$$

Quadratic Term

$$a_{2} = 3(-0.08\ m) = -0.24\ m,\ A_{2} = \frac{(100\ m)^{\frac{4}{3}}}{{\left|-0.24\ m\right|}^{\frac{1}{3}}}\left( \frac{-0.24\ m}{\left|-0.24\ m\right|} \right) = -746.9007911\ m$$

Cubic Term

$$a_{3} = -2\Delta D = -2(-0.08\ m) = 0.16\ m,\ A_{3} = \frac{{(100\ m)}^{\frac{5}{4}}}{{\left|0.16\ m\right|}^{\frac{1}{4}}}\left( \frac{0.16\ m}{\left|0.16\ m\right|} \right) = 500\ m$$

The parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCTHIRDORDERPOLYNOMIALSPIRAL(#98,500.00000000000006,-746.90079109286057,$,125000.);
~~~


$$D_0 = D(0\ m) = (100\ m)^2\left( \frac{500\ m}{\left| (500\ m)^{5} \right|}(0\ m)^{3} + \frac{1}{(-746.9007911\ m)^{3}}(0\ m)^{2} + \frac{1}{125000\ m} \right) = 0.08\ m$$

$$D'(0) = 0,\ \theta_0 = 0$$

$$dx_x = \cos(\theta_0) = 1$$

$$dy_x = \sin(\theta_0) = 0$$

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10666666666666667,0.99429483666678176));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.6.3 Compute Point on Curve

Compute the cant placement matrix for a point $\ell = 50\ m$ from the start of the curve segment using the algorithm in Section 4.2.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (1,\ 0,\ 0)$$

$$\mathbf{Axis}_p = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ 0.994295,\ -0.1066667)$$

$$M_{CSP} = \begin{bmatrix}
                 1 &                  0 &                  0 &                  0 \\
                -0 &  0.994294836666782 &  0.106666666666667 &               0.08 \\
                 0 & -0.106666666666667 &  0.994294836666782 &                  0 \\
                 0 &                  0 &                  0 &                  1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$s_0 = 0,\ D(0) = 0.08\ m,\ D'(0) = 0,\ \theta_s = 0$$

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}} \right) = \cos^{-1}\left(\frac{{0.16 - 0}}{1.5} \right) = 1.463926346$$

$$\mathbf{X}_s = (1,\ 0,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0,\ 0.994295,\ -0.106667)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (0,\ 0.106667,\ 0.994295)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (1,\ 0,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
                 1 &                  0 &                 -0 &                  0 \\
                 0 &  0.994294836666782 &  0.106666666666667 &               0.08 \\
                 0 & -0.106666666666667 &  0.994294836666782 &                  0 \\
                 0 &                  0 &                  0 &                  1
\end{bmatrix}$$

$M_{PCS} = M_{CSP}$, because $\theta_s = 0$ and the placement location and orientation match the parent curve at the trim start exactly.

#### Step 3 — Evaluate the parent curve at $\ell = 50\ m$ — $M_{PC\ell}$

$$D(50\ m) = 0.04\ m$$

$$D'(50\ m) = (100\ m)^{2}\left( 3\frac{500\ m}{\left| (500\ m)^{5} \right|}(50\ m)^{2} + \frac{2}{(-746.9007911\ m)^{3}}(50\ m) \right) = -0.0012$$

$$\theta_{\ell} =\tan^{-1}(-0.0012) = -0.0011999994240005001$$

$$\phi(\ell) = 1.463926346 + \left(\frac{\frac{\pi}{2} - 1.463926346}{-0.08}\right)(0.04 - 0.08) = 1.517361336$$

$$\mathbf{X} _{\ell} = (0.9999980,\ -0.0019997,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.053107436,\ 0.998588804)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0.001997,\ 0.998587,\ -0.053107)$$

$$\mathbf{Axis} _{\ell} = \mathbf{X} _{\ell} \times \mathbf{Y} _{\ell} = (0.000106,\ 0.053107,\ 0.998589)$$

$$\mathbf{RefDir} _{\ell} = \mathbf{Y} _{\ell} \times \mathbf{Axis} _{\ell} = (0.9999980,\ -0.0019997,\ 0)$$

$$M_{PC\ell} = \begin{bmatrix}
   0.999999280000778 &  0.00119828636590682 & 6.40913860804715e-05 &                   50 \\
-0.00119999913600094 &    0.998571971589017 &   0.0534094884003928 &   0.0399999999999999 \\
                   0 &  -0.0534095268552106 &    0.998572690560578 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

$$\mathbf{T}_c = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix}
   0.999999280000778 &  0.00119828636590682 & 6.40913860804715e-05 &                   50 \\
-0.00119999913600094 &    0.998571971589017 &   0.0534094884003928 &   0.0399999999999999 \\
                   0 &  -0.0534095268552106 &    0.998572690560578 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

## 4.7 Cosine Curve

A Cosine transition in cant is represented with an `IfcCosineSpiral`.

### 4.7.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{1}{A_{1}}\cos\left( \pi\frac{s}{L} \right)$$

$$\frac{d}{ds}D(s) = L^{2}\left( -\frac{\pi}{A_1 L}\sin\left( \pi\frac{s}{L} \right) \right)$$

Constant term,

$$a_0 = D_s + \frac{\Delta D}{2}$$

$$A_0 = L^{2}\frac{1}{a_0}\frac{a_0}{\left|a_0\right|}$$

Cosine term, 

$$a_1 = -\frac{1}{2} \Delta D$$

$$A_1 = L^{2}\frac{1}{a_1}\frac{a_1}{\left|a_1\right|}$$

### 4.7.2 Semantic Definition to Geometry Mapping

Consider and alignment segment that has a Cosine transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.COSINECURVE.);
~~~

Compute the parent curve parameters

$$D_{s} = \frac{0 + 0.16}{2} = 0.08\ m,\ D_{e} = \frac{0 + 0\ m}{2} = 0.\ m,\ \Delta D = 0.0\ m - 0.08\ m = -0.08\ m$$

$$a_0 = 0.08\ m + \frac{-0.08\ m}{2} = 0.04$$

$$A_0 = (100\ m)^{2} \frac{1}{0.04\ m}\frac{0.04\ m}{\left|0.04\ m\right|} = 250000\ m$$

$$a_1 = -\frac{1}{2}(-0.08\ m) = -0.04\ m$$

$$A_1 = (100\ m)^2\frac{1}{-0.04\ m}\frac{-0.04\ m}{\left|-0.04\ m\right|} = 250000\ m$$

The parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCCOSINESPIRAL(#98,250000.,250000.);
~~~

$$D(0\ m) = (100\ m)^{2}\left( \frac{1}{250000\ m} + \frac{1}{250000\ m}\cos\left( \pi\frac{0\ m}{100\ m} \right) \right) = 0.08\ m$$

$$ D'(0\ m) = (100\ m)^{2}\left( -\frac{\pi}{(250000\ m)(100\ m)}\sin\left( \pi\frac{0\ m}{100\ m} \right) \right) = 0$$

$$\theta_0 = 0,\ dx_x = 1,\ dy_x = 0$$

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10666666666666667,0.99429483666678176));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.7.3 Compute Point on Curve

Compute the cant placement matrix for a point $\ell = 50\ m$ from the start of the curve segment using the algorithm in Section 4.2.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (1,\ 0,\ 0)$$

$$\mathbf{Axis}_p = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ 0.9943592,\ -0.10606498)$$

$$M_{CSP} = \begin{bmatrix}
                 1 &                  0 &                  0 &                  0 \\
                -0 &  0.994294836666782 &  0.106666666666667 &               0.08 \\
                 0 & -0.106666666666667 &  0.994294836666782 &                  0 \\
                 0 &                  0 &                  0 &                  1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$s_0 = 0,\ D(0) = 0.08\ m,\ D'(0) = 0,\ \theta_s = 0$$

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}} \right) = \cos^{-1}\left(\frac{0.16 - 0}{1.5} \right) = 1.463926346$$

$$\mathbf{X}_s = (1,\ 0,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0,\ 0.9943592,\ -0.10606498)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (1,\ 0,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
                 1 &                  0 &                  0 &                  0 \\
                -0 &  0.994294836666782 &  0.106666666666667 &               0.08 \\
                 0 & -0.106666666666667 &  0.994294836666782 &                  0 \\
                 0 &                  0 &                  0 &                  1
\end{bmatrix}$$

$M_{PCS} = M_{CSP}$, because $\theta_s = 0$ and the placement location and orientation match the parent curve at the trim start exactly.

#### Step 3 — Evaluate the parent curve at $\ell = 50\ m$ — $M_{PC\ell}$

$$D(50\ m) = 0.04\ m,\ D'(50\ m) = -0.00125664,\ \theta_{\ell} = -0.001256636$$

$$\phi(\ell) = 1.463926346 + \left(\frac{\frac{\pi}{2} - 1.463926346}{-0.08}\right)(0.04 - 0.08) = 1.517361336$$

$$\mathbf{X} _{\ell} = (0.99999921,\ -0.001256636,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.053107436,\ 0.998588804)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0.001255,\ 0.998588,\ -0.053107)$$

$$\mathbf{Axis} _{\ell} = \mathbf{X} _{\ell} \times \mathbf{Y} _{\ell} = (0.0000667,\ 0.053107,\ 0.998589)$$

$$\mathbf{RefDir} _{\ell} = \mathbf{Y} _{\ell} \times \mathbf{Axis} _{\ell} = (0.99999921,\ -0.001256636,\ 0)$$

$$M_{PC\ell} = \begin{bmatrix}
   0.999999999921043 & 1.25484345139712e-05 & 6.71164391931997e-07 &                   50 \\
-1.2566370613367e-05 &    0.998572690481733 &   0.0534095653016217 &                 0.04 \\
                   0 &  -0.0534095653058388 &    0.998572690560578 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

$$\mathbf{T}_c = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix}
   0.999999999921043 & 1.25484345139712e-05 & 6.71164391931997e-07 &                   50 \\
-1.2566370613367e-05 &    0.998572690481733 &   0.0534095653016218 &                 0.04 \\
                   0 &  -0.0534095653058388 &    0.998572690560577 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

## 4.8 Sine Curve

A Sine transition in cant is represented with an `IfcSineSpiral`

### 4.8.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{1}{A_{0}} + \frac{A_{1}}{\left| A_{1} \right|}\left( \frac{1}{A_{1}} \right)^{2}s + \frac{1}{A_{2}}\sin\left( 2\pi\frac{s}{L} \right)$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{A_{1}}{\left| A_{1} \right|}\left( \frac{1}{A_{1}} \right)^{2} + \frac{2\pi}{LA_{2}}\cos\left( 2\pi\frac{s}{L} \right) \right)$$

Constant term: 
$$a_0 = D_s$$
$$A_0 = L^2\frac{1}{a_0}\frac{a_0}{\left|a_0\right|} $$

Linear term: 

$$a_1 = \Delta D$$
$$A_1 = L^{\frac{3}{2}}\frac{1}{{\left|a_1\right|}^{\frac{1}{2}}}\frac{a_1}{\left|a_1\right|} $$

Sine term: 
$$a_2 = -\frac{1}{2\pi} \Delta D$$
$$A_2 = L^2\frac{1}{a_2}\frac{a_2}{\left|a_2\right|} $$

### 4.8.2 Semantic Definition to Geometry Mapping

Consider an alignment segment that has a Sine transition curve towards the left. The start cant is $160\ mm$ and transitions to zero over $100\ m$.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.16,0.,.SINECURVE.);
~~~

Compute the parent curve parameters

$$D_{s} = \frac{0 + 0.16}{2} = 0.08\ m,\ D_{e} = \frac{0 + 0\ m}{2} = 0.\ m,\ \Delta D = 0.0\ m - 0.08\ m = -0.08\ m$$

Constant term:
$$a_0 = 0.08\ m$$

$$A_0 = (100\ m)^2\frac{1}{0.08\ m}\frac{0.08\ m}{\left|0.08\ m\right|} = 125000\ m$$

Linear term:
$$a_1 = -0.08\ m$$

$$A_1 = (100\ m)^{\frac{3}{2}} \frac{1}{{\left|-0.08\ m\right|}^{\frac{1}{2}}}\frac{-0.08\ m}{\left|-0.08\ m\right|} = -3535.533906\ m$$

Sine term:
$$a_2 = -\frac{1}{2\pi} (0.08\ m) = -0.0127324\ m$$

$$A_2 = (100\ m)^2\frac{1}{-0.0127324\ m}\frac{-0.0127324\ m}{\left|-0.0127324\ m\right|} = 785398.1634\ m$$

The parent curve is

~~~
#96=IFCCARTESIANPOINT((0.,0.));
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCSINESPIRAL(#98,785398.16339744814,-3535.533905932738,125000.);
~~~

$$D(0\ m) = (100\ m)^{2}\left(\frac{1}{125000\ m} + \left( \frac{-3535.533906\ m}{\left|-3535.533906\ m\right|} \right)\left( \frac{1}{-3535.533906\ m} \right)^{2}(0\ m) + \frac{1}{785398.1634\ m}\sin\left( 2\pi\frac{0\ m}{100\ m} \right) \right) = 0.08\ m$$

$$D'(0\ m) = (100\ m)^{2}\left( \frac{-3535.533906}{\left| -3535.533906 \right|}\left( \frac{1}{-3535.533906} \right)^{2} + \frac{2\pi}{(100\ m)(785398.1634\ m)}\cos\left( 2\pi\frac{0\ m}{100\ m} \right) \right) = 0.$$

$$\theta_0 = 0$$

$$dx_x = \cos(\theta_0) = 1$$

$$dx_y = \sin(\theta_0) = 0$$

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.16 - 0.0}{1.5}\right) = 1.463926346$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = \cos(1.463926346) = 0.106666667$$

$$dz_z = \sin(\phi_s) = \sin(1.463926346) = 0.994294837$$

~~~
#100=IFCCARTESIANPOINT((0.,0.08,0.));
#101=IFCDIRECTION((0.,0.10666666666666667,0.99429483666678176));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~

### 4.8.3 Compute Point on Curve

Compute the cant placement matrix for a point $\ell = 50\ m$ from the start of the curve segment using the algorithm in Section 4.2.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (1,\ 0,\ 0)$$

$$\mathbf{Axis}_p = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ 0.9943592,\ -0.10606498)$$

$$M_{CSP} = \begin{bmatrix}
                 1 &                  0 &                  0 &                  0 \\
                -0 &  0.994294836666782 &  0.106666666666667 &               0.08 \\
                 0 & -0.106666666666667 &  0.994294836666782 &                  0 \\
                 0 &                  0 &                  0 &                  1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$s_0 = 0,\ D(0) = 0.08\ m,\ D'(0) = 0,\ \theta_s = 0$$

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}} \right) = \cos^{-1}\left(\frac{0.16 - 0}{1.5} \right) = 1.463926346$$

$$\mathbf{X}_s = (1,\ 0,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0,\ 0.9943592,\ -0.10606498)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (0,\ 0.106064981,\ 0.994359201)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (1,\ 0,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
                    1 & -3.36880194376639e-21 & -3.61400724161835e-22 &                     0 \\
  3.3881317890172e-21 &     0.994294836666782 &     0.106666666666667 &                  0.08 \\
                    0 &    -0.106666666666667 &     0.994294836666782 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

$M_{PCS} = M_{CSP}$, because $\theta_s = 0$ and the placement location and orientation match the parent curve at the trim start exactly.

#### Step 3 — Evaluate the parent curve at $\ell = 50\ m$ — $M_{PC\ell}$

$$D(50\ m) = 0.04\ m,\ D'(50\ m) = -0.0016,\ \theta_{\ell} = -0.0016$$

$$\phi(\ell) = 1.463926346 + \left(\frac{\frac{\pi}{2} - 1.463926346}{-0.08}\right)(0.04 - 0.08) = 1.517361336$$

$$\mathbf{X} _{\ell} = (0.99999872,\ -0.0016,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.053107436,\ 0.998588804)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0.001598,\ 0.998588,\ -0.053107)$$

$$\mathbf{Axis} _{\ell} = \mathbf{X} _{\ell} \times \mathbf{Y} _{\ell} = (0.0000850,\ 0.053107,\ 0.998589)$$

$$\mathbf{RefDir} _{\ell} = \mathbf{Y} _{\ell} \times \mathbf{Axis} _{\ell} = (0.99999872,\ -0.0016,\ 0)$$

$$M_{PC\ell} = \begin{bmatrix}
      0.999999999872 & 1.59771630469242e-05 & 8.54553044742128e-07 &                   50 \\
-1.5999999997952e-05 &     0.99857269043276 &    0.053409565296383 &                 0.04 \\
                   0 &  -0.0534095653032194 &    0.998572690560578 &                    0 \\
                   0 &                    0 &                    0 &                    1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

$$\mathbf{T}_c = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix}
       0.999999999872 &  1.59771630469242e-05 &  8.54553044742129e-07 &                    50 \\
 -1.5999999997952e-05 &      0.99857269043276 &     0.053409565296383 &                  0.04 \\
-1.80958646087621e-22 &   -0.0534095653032194 &     0.998572690560578 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

$$\mathbf{Axis} = (0.0000850,\ 0.053107,\ 0.998589),\quad \phi(50\ m) = 1.517361336$$

## 4.9 Viennese Bend

A Viennese Bend transition in cant is represented with an `IfcSeventhOrderPolynomialSpiral`.

### 4.9.1 Parent Curve Parametric Equations

The deviating elevation and its rate of change are given by the following equations.

$$\frac{D(s)}{L^{2}} = \frac{A_7}{\left|A_7^9\right|}s^7 + \frac{1}{A_6^7}s^6 + \frac{A_5}{\left|A_5^7\right|}s^5 + \frac{1}{A_4^5}s^4 + \frac{A_{3}}{\left| A_{3}^{5} \right|}s^{3} + \frac{1}{A_{2}^{3}}s^{2} + \frac{A_{1}}{2\left| A_{1}^{3} \right|}s + \frac{1}{A_{0}}$$

$$\frac{d}{ds}D(s) = L^{2}\left( \frac{7A_7}{\left|A_7^9\right|}s^6 + \frac{6}{A_6^7}s^5 + \frac{5A_5}{\left|A_5^7\right|}s^4 + \frac{4}{A_4^5}s^3 + \frac{3A_{3}}{\left| A_{3}^{5} \right|}s^{2} + \frac{2}{A_{2}^{3}}s + \frac{A_{1}}{2\left| A_{1}^{3} \right|} \right)$$

$$D_s = \frac{D_{sl} + D_{sr}}{2},\ D_e = \frac{D_{el} + D_{er}}{2},\ \Delta D = D_e - D_s$$

Constant Term

$$a_{0} = D_{1}, A_{0} = \frac{L^{2}}{\left| a_{0} \right|}\frac{a_{0}}{\left| a_{0} \right|}$$

Linear Term

$$a_{1} = 0, A_{1} = \frac{L^{\frac{3}{2}}}{{\left| a_{1} \right|}^{\frac{1}{2}}}\frac{a_{1}}{\left| a_{1} \right|}$$

Quadratic Term

$$a_{2} = 0, A_{2} = \frac{L^{\frac{4}{3}}}{{\left| a_{2} \right|}^{\frac{1}{3}}}\frac{a_{2}}{\left| a_{2} \right|}$$

Cubic Term

$$a_{3} = 0, A_{3} = \frac{L^{\frac{5}{4}}}{{\left| a_{3} \right|}^{\frac{1}{4}}}\ \frac{a_{3}}{\left| a_{3} \right|}$$

Quartic Term

$$a_{4} = 35\Delta D, A_{4} = \frac{L^{\frac{6}{5}}}{{\left| a_{4} \right|}^{\frac{1}{5}}}\ \frac{a_{4}}{\left| a_{4} \right|}$$

Quintic Term

$$a_{5} = -84\Delta D, A_{5} = \frac{L^{\frac{7}{6}}}{{\left| a_{5} \right|}^{\frac{1}{6}}}\ \frac{a_{5}}{\left| a_{5} \right|}$$

Sextic Term

$$a_{6} = 70\Delta D, A_{6} = \frac{L^{\frac{8}{7}}}{{\left| a_{6} \right|}^{\frac{1}{7}}}\ \frac{a_{6}}{\left| a_{6} \right|}$$

Septic Term

$$a_{7} = -20\Delta D, A_{7} = \frac{L^{\frac{9}{8}}}{{\left| a_{7} \right|}^{\frac{1}{8}}}\ \frac{a_{7}}{\left| a_{7} \right|}$$

### 4.9.2 Semantic Definition to Geometry Mapping

Consider a Viennese Bend cant transition on a left-hand curve where the curvature decreases — a transition from a tighter arc to an arc of larger radius. The right rail begins at 100 mm of superelevation and decreases to 30 mm over 100 m. The left rail carries no cant throughout.

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.10,0.03,.VIENNESEBEND.);
~~~

Compute the parent curve parameters.

$$D_{sl} = 0.0\ m$$
$$D_{el} = 0.0\ m$$
$$D_{sr} = 0.1\ m$$
$$D_{er} = 0.03\ m$$

$$D_s = \frac{0\ m + 0.1\ m}{2} = 0.05\ m, D_e = \frac{0\ m + 0.03\ m}{2} = 0.015\ m,\ \Delta D = 0.015 - 0.05 = -0.035\ m$$

Constant Term
$$a_{0} = 0.05\ m, A_{0} = \frac{(100\ m)^{2}}{\left| 0.05\ m \right|}\frac{0.05\ m}{\left| 0.05\ m \right|} = 200000\ m$$

Linear Term
$$a_{1} = 0, A_{1} = 0\ m$$

Quadratic Term

$$a_{2} = 0, A_{2} = 0\ m$$

Cubic Term

$$a_{3} = 0, A_{3} = 0\ m$$

Quartic Term

$$a_{4} = 35(-0.035\ m) = -1.225\ m, A_{4} = \frac{(100\ m)^{\frac{6}{5}}}{{\left| -1.225\ m \right|}^{\frac{1}{5}}}\ \frac{-1.225\ m}{\left| -1.225\ m \right|} = -241.1974890085123\ m$$

Quintic Term

$$a_{5} = -84(-0.035\ m) = 2.94\ m, A_{5} = \frac{(100\ m)^{\frac{7}{6}}}{{\left| 2.94\ m \right|}^{\frac{1}{6}}}\ \frac{2.94\ m}{\left| 2.94\ m \right|} = 180.0012184608678\ m$$

Sextic Term

$$a_{6} = 70(-0.035\ m)=-2.45\ m, A_{6} = \frac{(100\ m)^{\frac{8}{7}}}{{\left| -2.45\ m \right|}^{\frac{1}{7}}}\ \frac{-2.45\ m}{\left|-2.45\ m\right|} = -169.87095595653895\ m$$

Septic Term

$$a_{7} = -20(-0.035\ m) = 0.7\ m, A_{7} = \frac{(100\ m)^{\frac{9}{8}}}{{\left| 0.7\ m \right|}^{\frac{1}{8}}}\ \frac{0.7\ m}{\left| 0.7\ m \right|} = 185.93568367635672\ m$$

The parent curve is

~~~
#97=IFCDIRECTION((1.,0.));
#98=IFCAXIS2PLACEMENT2D(#96,#97);
#99=IFCSEVENTHORDERPOLYNOMIALSPIRAL(#98,185.93568367635649,-169.87095595653892,180.00121846086768,-241.19748900851218,$,$,$,200000.);
~~~

$$D(0\ m) = (100\ m)^2 \left(\frac{185.93568367635672\ m}{\left|(185.93568367635672\ m)^9\right|}(0\ m)^7 + \frac{1}{(-169.87095595653895\ m)^7}(0\ m)^6 + \frac{180.0012184608678\ m}{\left|(180.0012184608678\ m)^7\right|}(0\ m)^5 + \frac{1}{(-241.1974890085123\ m)^5}(0\ m)^4  + \frac{1}{200000\ m}\right) = 0.05\ m$$

$$D'(0) = 0,\ \theta_0 = 0$$

$$dx_x = \cos(\theta) = 1$$

$$dx_y = \sin(\theta) = 0$$

The cross-slope at the start of the segment is

$$\phi_s = \cos^{-1}\left(\frac{D_{sr}-D_{sl}}{D_{rh}}\right) = \cos^{-1}\left(\frac{0.1-0.0}{1.5} \right) = 1.504080178$$

The cross slope orientation is

$$dy_z = \cos(\phi_s) = 0.066666667$$

$$dz_z = \sin(\phi_s) = 0.997775303$$

~~~
#100=IFCCARTESIANPOINT((0.,0.05,0.));
#101=IFCDIRECTION((0.,0.066666666666666666,0.99777530313971774));
#102=IFCDIRECTION((1.,0.,0.));
#103=IFCAXIS2PLACEMENT3D(#100,#101,#102);
#104=IFCCURVESEGMENT(.DISCONTINUOUS.,#103,IFCLENGTHMEASURE(0.),IFCLENGTHMEASURE(100.),#99);
~~~


### 4.9.3 Compute Point on Curve

Compute the cant placement matrix for a point $\ell = 50\ m$ from the start of the curve segment using the algorithm in Section 4.2.

#### Step 1 — Form the curve segment placement matrix $M_{CSP}$

$$\mathbf{RefDir}_p = (1,\ 0,\ 0)$$

$$\mathbf{Axis}_p = (0,\ 0.066519011,\ 0.99778516)$$

$$\mathbf{Y}_p = \mathbf{Axis}_p \times \mathbf{RefDir}_p = (0,\ 0.99778516,\ -0.066519011)$$

$$M_{CSP} = \begin{bmatrix}
                  1 &                   0 &                   0 &                   0 \\
                 -0 &   0.997775303139718 &  0.0666666666666667 &                0.05 \\
                  0 & -0.0666666666666667 &   0.997775303139718 &                   0 \\
                  0 &                   0 &                   0 &                   1
\end{bmatrix}$$

#### Step 2 — Evaluate the parent curve at the trim start — $M_{PCS}$

$$s_0 = 0,\ D(0) = 0.05\ m,\ D'(0) = 0,\ \theta_s = 0$$

$$\phi_s = \cos^{-1}\left(\frac{D_{sr} - D_{sl}}{D_{rh}} \right) = \cos^{-1}\left(\frac{0.10 - 0.0}{1.5} \right) = 1.504080178$$

$$\mathbf{X}_s = (1,\ 0,\ 0)$$

$$\mathbf{Z}_s = (0,\ 0.066666667,\ 0.997775303)$$

$$\mathbf{Y}_s = \mathbf{Z}_s \times \mathbf{X}_s = (0,\ 0.99778516,\ -0.066519011)$$

$$\mathbf{Axis}_s = \mathbf{X}_s \times \mathbf{Y}_s = (0,\ 0.066519011,\ 0.99778516)$$

$$\mathbf{RefDir}_s = \mathbf{Y}_s \times \mathbf{Axis}_s = (1,\ 0,\ 0)$$

$$M_{PCS} = \begin{bmatrix}
                  1 &                   0 &                  -0 &                   0 \\
                  0 &   0.997775303139718 &  0.0666666666666667 &                0.05 \\
                  0 & -0.0666666666666667 &   0.997775303139718 &                   0 \\
                  0 &                   0 &                   0 &                   1
\end{bmatrix}$$

$M_{PCS} = M_{CSP}$, because $\theta_s = 0$ and the placement location and orientation match the parent curve at the trim start exactly.

#### Step 3 — Evaluate the parent curve at $\ell = 50\ m$ — $M_{PC\ell}$

$$D(50\ m) = 0.0325\ m,\ D'(50\ m) = -0.00076525,\ \theta_{\ell} = -0.00076562$$

$$\phi_e = cos^{-1}\left(\frac{D_{er} - D_{el}}{D_{rh}}\right) = cos^{-1}\left(\frac{0.03 - 0.0}{1.5}\right) = 1.550794993$$

$$\phi(\ell) = 1.504080178 + \left(\frac{1.550799 - 1.504080178}{-0.035}\right)(0.0325 - 0.05) = 1.527439589$$

$$\mathbf{X} _{\ell} = (0.999999707,\ -0.00076562,\ 0)$$

$$\mathbf{Z} _{\ell} = (0,\ 0.04327,\ 0.999063)$$

$$\mathbf{Y} _{\ell} = \mathbf{Z} _{\ell} \times \mathbf{X} _{\ell} = (0.000765,\ 0.999063,\ -0.04327)$$

$$\mathbf{Axis} _{\ell} = \mathbf{X} _{\ell} \times \mathbf{Y} _{\ell} = (3.31e-05,\ 0.04327,\ 0.999063)$$

$$\mathbf{RefDir} _{\ell} = \mathbf{Y} _{\ell} \times \mathbf{Axis} _{\ell} = (0.999999707,\ -0.00076562,\ 0)$$

$$M_{PC\ell} = \begin{bmatrix}
    0.999999706909309 &  0.000764905208550319 &    3.318611612348e-05 &                    50 \\
-0.000765624775602475 &     0.999059864228941 &    0.0433451312633188 &    0.0324999999999996 \\
                    0 &    -0.043345143967377 &     0.999060157044173 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

#### Step 4 — Compute the cant placement matrix $M_c$

**Rotation**

$$R_c = R_{PC\ell} \cdot R_{PCS}^T \cdot R_{CSP}$$

**Translation**

$$\mathbf{T}_c = \mathbf{T}_{PC\ell} - \mathbf{T}_{PCS} + \mathbf{T}_{CSP}$$

**Assemble**

$$M_c = 
\begin{bmatrix} 
R_c & \mathbf{T}_c \\
\mathbf{0}^T & 1 
\end{bmatrix}$$

$$M_c = \begin{bmatrix}
    0.999999706909309 &  0.000764905208550319 &    3.318611612348e-05 &                    50 \\
-0.000765624775602475 &     0.999059864228941 &    0.0433451312633188 &    0.0324999999999996 \\
                    0 &    -0.043345143967377 &     0.999060157044173 &                     0 \\
                    0 &                     0 &                     0 &                     1
\end{bmatrix}$$

## 4.10 Combined 3D

The cant segment result is computed with the 2D vertical and 2D horizontal to complete the evaluation of a point on the alignment. The result is a 3D point and reference frame.

Using the example horizontal Bloss curve from Section 2.8 $M_h$ at $s = 50\ m$ is

$$M_{h} = 
\begin{bmatrix}
0.999512 & -0.031245 & 0 & 49.9962109\\
0.031245 & 0.999512 & 0 & 0.416638875\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Assume a vertical alignment that is flat. At $s = 50\ m$

$$M_v = \begin{bmatrix}
1 & 0 & 0 & 50\\
0 & 1 & 0 & 0\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1 
\end{bmatrix}$$

From the Bloss cant example in Section 4.6

$$M_c = \begin{bmatrix}
0.999999280 & 0.00119830570 & 0.0 & 50.0 \\
-0.00119999914 & 0.998588085 & 0.0531073592 & 0.04 \\
0 & 0 & 0.9985888041 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

#### Step 5 — Combine with horizontal and vertical to produce the 3D placement matrix

Construct $M^\prime_v$ as described in Section 3.2

$$M'_v =
 \begin{bmatrix}
1 & 0 & 0 & 0\\
0 & 0 & 1 & 0\\
0 & 1 & 0 & 0\\
0 & 0 & 0 & 1 
\end{bmatrix}$$

Construct $M^\prime_c$ by zeroing the distance-along $\ell$ component in row 1, column 4 and moving the deviating elevation $D$ from row 2 to row 3 in column 4 of $M_c$:

$$M'_c = \begin{bmatrix}
0.999999280 & 0.00119830570 & 0.0 & 0.0 \\
-0.00119999914 & 0.998588085 & 0.0531073592 & 0 \\
0 & 0 & 0.9985888041 & 0.04 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

Extract position vectors from each modified matrix, $M^\prime_v,\ M^\prime_c$, (setting row 4 to zero), then zero column 4:

$$P_v = M'_v \text{ column 4, row 4 set to 0} = \begin{bmatrix} 0 \\ 0 \\ 0 \\ 0 \end{bmatrix}, \qquad P_c = M'_c \text{ column 4, row 4 set to 0} = \begin{bmatrix} 0 \\ 0 \\ 0.04 \\ 0 \end{bmatrix}$$

$$M''_v = M'_v \text{ with column 4 set to } (0,0,0,1)^T, \qquad M''_c = M'_c \text{ with column 4 set to } (0,0,0,1)^T$$

$$M''_{v} = \begin{bmatrix}
1 & 0 & 0 & 0\\  
0 & 0 & 1 & 0\\  
0 & 1 & 0 & 0\\  
0 & 0 & 0 & 1   
\end{bmatrix}$$

$$M''_c = \begin{bmatrix}
0.999999280 & 0.00119830570 & 0.0 & 0.0 \\
-0.00119999914 & 0.998588085 & 0.0531073592 & 0.0 \\
0 & 0 & 0.9985888041 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}$$

Multiply the three orientation matrices, then add back both position offsets:

$$M' = M_h \cdot M''_v \cdot M''_c$$

$$M' = 
\begin{bmatrix}
0.999512 & -0.031245 & 0 & 49.9962109\\
0.031245 & 0.999512 & 0 & 0.416638875\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1 
\end{bmatrix}
\begin{bmatrix}
1 & 0 & 0 & 0\\  
0 & 0 & 1 & 0\\  
0 & 1 & 0 & 0\\  
0 & 0 & 0 & 1   
\end{bmatrix}
\begin{bmatrix}
0.999999280 & 0.00119830570 & 0.0 & 0.0 \\
-0.00119999914 & 0.998588085 & 0.0531073592 & 0.0 \\
0 & 0 & 0.9985888041 & 0 \\
0 & 0 & 0 & 1
\end{bmatrix}
$$

$$M' = \begin{bmatrix}
0.999473545 & -0.0324443047 & 0 &  49.9962109\\
0.0324443047 &  0.999473545 & 0 &  0.416638875\\
 0 & 0 & 1 & 0 \\
 0 & 0 & 0 & 1
 \end{bmatrix}$$

$$M_{3Dcant} = 
\begin{bmatrix}
0.999473545 & -0.0324443047 & 0 &  49.9962109\\
0.0324443047 &  0.999473545 & 0 & 0.416638875\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1
\end{bmatrix}
+
\begin{bmatrix}
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0
\end{bmatrix}
+
\begin{bmatrix}
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0\\
0 & 0 & 0 & 0.04\\
0 & 0 & 0 & 0
\end{bmatrix}
$$

$$M_{3Dcant} = 
\begin{bmatrix}
0.999473545 & -0.0324443047 & 0 &  49.9962109\\
0.0324443047 &  0.999473545 & 0 & 0.416638875\\
0 & 0 & 1 & 0.04\\
0 & 0 & 0 & 1
\end{bmatrix}
$$

## 4.11 Deviation from EnrichIfc4x3 Reference Implementation

The cant calculations in this section deviate from the ones performed by the EnrichIfc4x3
reference implementation. The calculations in the reference implementation, published at
[IFC-Rail-Unit-Test-Reference-Code/EnrichIFC4x3/EnrichIFC4x3/business2geometry
at master · bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code
(github.com)](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/tree/master/EnrichIFC4x3/EnrichIFC4x3/business2geometry), yield coefficients for sine, cosine, clothoid, and polynomial spirals that are not in units of length. The IFC specification is clear that the coefficients have
units of length and are represented by `IfcLengthMeasure`.

The basic form of the coefficient of the $i^{th}$ term is 

$$A_{i} = \frac{L^{\frac{i + 2}{i + 1}}}{{\left| a_{i} \right|}^{\frac{1}{(i + 1)}}}\frac{a_{i}}{\left| a_{i} \right|}$$

Performing a dimensional analysis with $l$ representing term with length units, we see that the resulting coefficient $A_{i}$ has units of length. 

$$\frac{l^{\frac{i + 2}{i + 1}}}{{\left|l\right|}^{\frac{1}{(i + 1)}}}\frac{l}{\left|l\right|} = \frac{l^{\frac{i + 2}{i + 1}}}{l^{\frac{1}{i + 1}}} = l^{\frac{i + 2}{i + 1}}l^{\frac{- 1}{(i + 1)}} = l^{\frac{i + 1}{i + 1}} = l$$

The error in the EnrichIfc4x3 reference implementation is illustrated by way of an example. Consider the Bloss Curve example [GENERATED__CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc](https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/blob/master/alignment_testset/IFC-WithGeneratedGeometry/GENERATED__CantAlignment_BlossCurve_100.0_1000_300_1_Meter.ifc). 

The semantic definition of the cant transition segment is 

~~~
#64=IFCALIGNMENTCANTSEGMENT($,$,0.,100.,0.,0.,0.,0.16,.BLOSSCURVE.);
~~~

The EnrichIfc4x3 reference implementation maps the semantic definition to the geometric representation as follows:

$$D_s = \frac{0.0 + 0.0}{2} = 0\ m,\ D_e = \frac{0.0 + 0.16}{2} = 0.08\ m,\ \Delta D = 0.08 - 0.0 = 0.08\ m$$

Quadratic Term:

$$a_{2} = 3\Delta D = 3(0.08\ m) = 0.24\ m$$

$$A_{2} = \frac{(100\ m)}{{\left|0.24\ m\right|}^{\frac{1}{3}}}\left( \frac{0.24\ m}{\left|0.24\ m\right|} \right) = 160.917897\ m^{2/3}$$


Cubic Term:

$$a_{3} = -2\Delta D = -0.016\ m$$
 
$$A_{3} = \frac{100\ m}{{\left|-0.16\ m\right|}^{\frac{1}{4}}}\frac{-0.16\ m}{\left|-0.16\ m\right|} = -158.113883\ m^{3/4}$$

Notice that the polynomial coefficients do not have whole length units (e.g. the units aren't $m$).

 The mapped geometric representation is
 
 ~~~
#127 = IFCTHIRDORDERPOLYNOMIALSPIRAL(#128, -158.113883008419, 160.914897434272, $, $);
 ~~~

Recalling from Bloss Curve example above, 

Quadratic Term

$$A_{2} = \frac{(100m)^{\frac{4}{3}}}{{\left|0.24m\right|}^{\frac{1}{3}}}\left( \frac{0.24m}{\left|0.24m\right|} \right) = 746.9007911\ m$$

Cubic Term

$$A_{3} = \frac{{(100\ m)}^{\frac{5}{4}}}{{\left|-0.16\ m\right|}^{\frac{1}{4}}}\left( \frac{-0.16\ m}{\left|-0.16\ m\right|} \right) = -500\ m$$

The polynomial coefficients have units of length as required by IFC.

The resulting geometric representation is

~~~
#127=IFCTHIRDORDERPOLYNOMIALSPIRAL(#98,-500.,746.900791092861,$,$);
~~~

Table 4.11-1 compares the third order polynomial terms.

| Polynomial Term | EnrichIfc4x3 | This Guide |
|-------------------------|-------------------------------------|--------------------------------------|
| Constant | $0.0$ (unitless) | $0\ m$|
| Linear | $0\ m^{1/2}$ | $0\ m$|
| Quadratic | $160.91789\ m^{2/3}$| $746.90078\ m$|
| Cubic | $-158.113883\ m^{3/4}$| $-500\ m$|

*Table 4.11-1 — Comparison of polynomial coefficients*

The EnrichIfc4x3 reference implementation computes the correct value for the deviating elevation. This is because there is a compensating error in the implementation. The deviating elevation is computed as

$$D(s) = L\left( \frac{A_3}{\left|A_3^5\right|}s^3 + \frac{1}{A_2^3}s^2\right)$$

Evaluated at $s = 50\ m$

$$D(50\ m) = (100\ m)\left( \frac{-158.113883\ m^{3/4}}{\left|(-158.113883\ m^{3/4})^5\right|}(100\ m)^3 + \frac{1}{(160.914897434272\ m^{2/3})^3}(100\ m)^2\right) = (100\ m)(-0.0002+0.0006) = 0.04\ m$$

The deviating elevation as computed in this guide is

$$D(s)= L^2\left( \frac{A_3}{\left|A_3^5\right|}s^3 + \frac{1}{A_2^3}s^2\right)$$

Notice that the first term is $L^2$, not $L$ as in the reference implementation.

$$D(50\ m) = (100\ m)^2\left( \frac{-500\ m}{\left|(-500\ m)^5\right|}(100\ m)^3 + \frac{1}{(746.90079\ m)^3}(100\ m)^2\right) = (100\ m)^2(-0.000002\ m^{-1} + 0.000006\ m^{-1}) = 0.04\ m$$

Both approaches give the same result, however, a serious problem emerges if the EnrichIfc4x3 semantic to geometry mapping is mixed with the deviating elevation equation from this guide and vice versa. Table 4.11-2 compares the results for all the combinations of the semantic to geometry mapping and deviating elevation computations for the Bloss curve evaluated at $s=50\ m$. The deviating elevation can be incorrect proportional (or inversely proportional) to the length of the segment (100 or 1/100 in this example). 

| Mapping | $D(s)$ Equation | $D(50\ m)$ |
|-----------------------------|---------------------------------------------|-------------------------|
| EnrichIfc4x3 | EnrichIfc4x3 | $0.04\ m$ |
| This Guide | This Guide | $0.04\ m$ |
| EnrichIfc4x3 | This Guide | $4.0\ m$ |
| This Guide | EnrichIfc4x3 | $0.0004\ m$ |

*Table 4.11-2 — Comparison of deviating elevation results*

## 4.12 Zero-Length Closing Segment and `IfcSegmentedReferenceCurve.EndPoint`

The zero-length closing segment requirement described in Section 2.12 applies equally to `IfcSegmentedReferenceCurve`. The final `IfcAlignmentCantSegment` nested within `IfcAlignmentCant` must have `SegmentLength = 0`, and the corresponding geometric counterpart in `IfcSegmentedReferenceCurve` must be a zero-length `IfcCurveSegment` placed at the endpoint of the cant alignment with its placement matching the end cant state of the preceding segment.

`IfcSegmentedReferenceCurve.EndPoint` is an *optional* `IfcCartesianPoint` attribute whose purpose overlaps with the zero-length segment: it encodes the 3D endpoint of the segmented reference curve, providing the same geometric information as the placement of the zero-length `IfcCurveSegment`. Because `EndPoint` is optional and the zero-length segment is required by the IFC Concept Templates, the zero-length segment is the primary, normative source of the endpoint geometry. When `EndPoint` is present, it must be consistent with the placement of the zero-length closing segment — a discrepancy between the two is a data error. Implementations should not rely on `EndPoint` as a substitute for the zero-length segment, nor assume it will be populated.

## 4.13 Summary and Implementation Checklist

| # | Item | Notes |
|-----|-----------------------------------------------|------------------------------------------------|
| 1 | Use `IfcAxis2Placement3D` (not `IfcAxis2Placement2D`) for cant curve segment placements | Cant encodes a cross-slope rotation that a 2D placement cannot represent; the `Axis` vector carries the cross-slope angle $\phi$ at the segment start |
| 2 | The cross-slope angle $\phi$ is interpolated using deviating elevation as the interpolation parameter, not arc length | The interpolation formula in Section 4.1.3 uses $D(\ell) - D_s$ as the parameter; $\phi$ does not vary linearly with distance along the segment |
| 3 | When forming $M^\prime_c$ for Step 5, zero the distance-along in column 4, row 1 and move the deviating elevation $D$ from row 2 to row 3 in column 4 | This maps the deviating elevation onto the Z axis where $M_h$ expects it; failure to do so incorrectly applies the translation offsets to the rotated frame |
| 4 | Do not mix the EnrichIfc4x3 semantic-to-geometry mapping with the deviating elevation equations from this guide | EnrichIfc4x3 contains two compensating errors that yield correct results within its own implementation; mixing its coefficient mapping with this guide's deviating elevation equation (or vice versa) breaks the cancellation and produces results off by a factor of $L$ or $1/L$ — see Section 4.11 |
| 5 | Include a zero-length `IfcCurveSegment` at the end of `IfcSegmentedReferenceCurve`; treat `IfcSegmentedReferenceCurve.EndPoint` as secondary | The zero-length segment is required by the IFC Concept Templates and is the normative endpoint; `EndPoint` is optional — if present, it must agree with the zero-length segment placement |
