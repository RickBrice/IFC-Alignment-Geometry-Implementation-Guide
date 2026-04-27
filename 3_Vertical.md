# Section 3 - Vertical Alignment

## 3.1 General

The geometric representation of a vertical alignment is accomplished with `IfcGradientCurve`. This defines the vertical alignment in a "distance along, elevation" coordinate system. Distance along is measured along `IfcGradientCurve.BaseCurve` = `IfcCompositeCurve`.

Table 3.1 maps each `IfcAlignmentVertical.PredefinedType` to its corresponding parent curve type.

  Business Logic (`IfcAlignmentVertical.PredefinedType`) | Geometric Representation (`IfcCurveSegment.ParentCurve`)
  ---------------------------------------|-----------------------------------
  CONSTANTGRADIENT                       |`IfcLine`
  CIRCULARARC                            |`IfcCircle`
  CLOTHOID                               |`IfcClothoid`
  PARABOLICARC                           |`IfcPolynomialCurve`

  *Table 3.1 — Mapping of business logic to geometric representation for vertical alignment*

The following parameters are used throughout this section:

$L =$ Horizontal Length

$g_{s} =$ Start Gradient

$g_{e} =$ End Gradient

## 3.2 Curve Segment Evaluation Algorithm

Vertical segments are evaluated in a two-dimensional "distance along, elevation" coordinate system. In this system $x(s)$ is the distance measured along the horizontal `IfcCompositeCurve` and $y(s)$ is the elevation above datum. The grade angle at arc-length $s$ is $\theta(s) = \tan^{-1}(g(s))$ where $g(s)$ is the gradient.

**Steps 1–5** follow the identical procedure described in Section 2.2 for horizontal segments, substituting distance along for the horizontal $x$-coordinate and elevation for the horizontal $y$-coordinate. Let $s_0$ = `SegmentStart`.

**Step 1 — Evaluate the parent curve at the trim start**

Compute the distance along $d_0 = x(s_0)$, elevation $z_0 = y(s_0)$, and grade angle $\theta_0 = \theta(s_0)$.

$$M_{PCS} = \begin{bmatrix} \cos\theta_0 & -\sin\theta_0 & 0 & d_0 \\ \sin\theta_0 & \cos\theta_0 & 0 & z_0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

**Step 2 — Form the translation matrix $M_T$**

$M_T$ moves the trim-start point to the origin of the distance-along/elevation plane.

$$M_T = \begin{bmatrix} 1 & 0 & 0 & -d_0 \\ 0 & 1 & 0 & -z_0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

**Step 3 — Form the rotation matrix $M_R$**

$M_R$ rotates so the grade direction at the trim start aligns with the positive $x$-direction, the inverse of the rotational part of $M_{PCS}$.

$$M_R = \begin{bmatrix} \cos\theta_0 & \sin\theta_0 & 0 & 0 \\ -\sin\theta_0 & \cos\theta_0 & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

**Step 4 — Form the curve segment placement matrix $M_{CSP}$**

$M_{CSP}$ is constructed from `IfcCurveSegment.Placement`, where $(d_p, z_p)$ is the `Location` (distance along, elevation) and $\theta_p$ is the grade angle of the `RefDirection`.

$$M_{CSP} = \begin{bmatrix} \cos\theta_p & -\sin\theta_p & 0 & d_p \\ \sin\theta_p & \cos\theta_p & 0 & z_p \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

**Step 5 — Evaluate and map each point in the vertical plane**

For the point at arc-length $s$, compute $x(s)$, $y(s)$, and $\theta(s)$:

$$M_{PC} = \begin{bmatrix} \cos\theta(s) & -\sin\theta(s) & 0 & x(s) \\ \sin\theta(s) & \cos\theta(s) & 0 & y(s) \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

$$M_v = M_{CSP}\, M_R\, M_T\, M_{PC}$$

Column 4 of $M_v$ contains the distance along $d$ and elevation $z$ of the evaluated point. Column 1 contains $(dx_v, dy_v) = (\cos\theta_v, \sin\theta_v)$, the grade direction at that point. Step 6 is performed immediately for this point before moving to the next arc-length $s$.

**Step 6 — Combine with the horizontal alignment to produce the 3D placement matrix**

The vertical result lives in the (distance along, elevation) plane and must be merged with the horizontal alignment to form a 3D position and orientation. The two coordinate systems share one axis — distance along — but their remaining axes are orthogonal to each other: horizontal $x$ and $y$ are Easting and Northing; vertical $y$ is elevation (Z in 3D).

Evaluate the horizontal placement matrix $M_h$ at distance $d$ along the `IfcCompositeCurve`. This yields the horizontal 2D position $(x_h, y_h)$ and the horizontal tangent direction $(dx_h, dy_h) = (\cos\theta_h, \sin\theta_h)$.

$M_v$ is a two-dimensional matrix whose rows index the vertical frame: row 1 = distance-along, row 2 = elevation, row 3 = out-of-plane. Three modifications produce $M'_v$, the form required for multiplication with $M_h$.

**Column 4** — The distance-along value $d$ is replaced with zero. The horizontal position already comes from $M_h$; retaining $d$ would displace the point a second time along the horizontal tangent.

**Rows 2 and 3** — $M_h$'s third row $(0,\ 0,\ 1,\ 0)$ passes row 3 of the right operand through unchanged into row 3 of the product. Because row 3 of $M_{3D}$ must carry the elevation (Z) component of every vector, elevation must occupy row 3 of $M'_v$ — not row 2 as in $M_v$. The row semantics are therefore swapped: in $M'_v$, row 2 is the cross-track (lateral) component and row 3 is the elevation (Z) component.

**Columns 2 and 3** — The row reordering reindexes the column values and exchanges the columns. $M_v$ column 2, the in-plane normal $(-dy_v,\ dx_v,\ 0)$ in [d-along, elevation, out-of-plane] ordering, becomes $(-dy_v,\ 0,\ dx_v)$ in [d-along, cross-track, elevation] ordering — the 3D up direction — and moves to column 3. $M_v$ column 3, the out-of-plane unit direction $(0,\ 0,\ 1)$, becomes $(0,\ 1,\ 0)$ — the cross-track direction — and moves to column 2.

$${M'}_v = \begin{bmatrix} dx_v & 0 & -dy_v & 0 \\ 0 & 1 & 0 & 0 \\ dy_v & 0 & dx_v & z \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

The columns of $M'_v$ define directions in the 3D frame local to the alignment:

- **Column 1** $(dx_v,\ 0,\ dy_v)$: the grade direction — $dx_v$ scales the contribution along the horizontal tangent; $dy_v$ is the elevation rate of change (Z component of the 3D tangent).
- **Column 2** $(0,\ 1,\ 0)$: the cross-track direction, always lateral to the alignment and always horizontal.
- **Column 3** $(-dy_v,\ 0,\ dx_v)$: the "up" direction in the vertical plane of the alignment, orthogonal to the grade direction.
- **Column 4** $(0,\ 0,\ z)$: the elevation offset with no horizontal displacement.

The 3D placement matrix is:

$$M_{3D} = M_h \cdot {M'}_v$$

Multiplying out, the columns of $M_{3D}$ are:

- **Column 1** (RefDirection / 3D tangent): $(dx_h \cdot dx_v,\ dy_h \cdot dx_v,\ dy_v)$ — the horizontal tangent scaled by $\cos\theta_v$, with $\sin\theta_v$ as the Z component.
- **Column 2** (Y / cross-track): $(-dy_h,\ dx_h,\ 0)$ — the horizontal normal direction, unchanged from $M_h$.
- **Column 3** (Axis / up): $(-dx_h \cdot dy_v,\ -dy_h \cdot dy_v,\ dx_v)$ — orthogonal to both the 3D tangent and the cross-track direction.
- **Column 4** (Location): $(x_h,\ y_h,\ z)$ — the full 3D position.

## 3.3 Constant Gradient

### 3.3.1 Parent Curve Parametric Equations

$$x(s) = p_{x} + s$$

$$y(s) = p_{y} + s(dy/dx)$$

Note that these equations are different from the equations for
horizontal.

### 3.3.2 Semantic Definition to Geometry Mapping

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

## 3.4 Circular Arc

Vertical circular arcs are tricky. For vertical, the "distance along" is
a horizontal dimension. The `IfcCurveSegment` trimming parameters `SegmentStart` and `SegmentLength` are measured along the `IfcCircle`. 

The following procedure maps the semantic parameters of a vertical circular arc to its geometric definition.

Determine the tangent slope angle at the start and end of the segment.

$\theta_{start} = tan^{-1}(g_{start})$

$\theta_{end} = tan^{-1}(g_{end})$

Compute the radius of the circle and the direction of vectors that are perpendicular to the circle, directed away from the center point.

if $\theta_{start} < \theta_{end}$

Curve is sagging (curve is on the bottom half of the circle)

$$h_l = $$ horizontal length = `IfcAlignmentVerticalSegment.HorizontalLength`

$R = \frac{h_l}{sin(\theta_{end}) - sin(\theta_{start})}$

$\Delta_{start} = \theta_{start} + \frac{3}{2}\pi$

$\Delta_{end} = \theta_{end} + \frac{3}{2}\pi$

else

Curve is cresting (curve is on top half of the circle)


$R = \frac{ul}{sin(\theta_{start}) - sin(\theta_{end})}$

$\Delta_{start} = \theta_{start} + \frac{1}{2}\pi$

$\Delta_{end} = \theta_{end} + \frac{1}{2}\pi$

Compute the curve trimming parameters `SegmentStart` and `SegmentLength`

$Segment Start = R\Delta_{start}$

$Segment Length = R(\Delta_{end} - \Delta_{start})$

### 3.4.1 Example

Given the following semantic definition of a vertical circular arc, create the geometric definition.

~~~
#320 = IFCALIGNMENTVERTICALSEGMENT($, $, 144.917656958471, 239.704902937655, 25.3780433292418, -8.17722122076371E-4, -1.28040164299203E-2, -20000., .CIRCULARARC.);
~~~

#### 3.4.1.1 Compute radius for the parent curve

$g_{start} = -8.17722122076371E-4$
$\theta_{start} = tan^{-1}(-8.17722122076371E-4) = -8.177219398E-4$

$g_{end} = -1.28040164299203E-2$
$\theta_{end} = tan^{-1}(-1.28040164299203E-2) = -1.2803316789E-4$

$ul = 239.704902937655$

$R = \frac{239.704902937655}{sin(-1.2803316789E-4) - sin(-8.177219398E-4)} = -20000.0$

Radius is negative which means a CW direction, so the curve is cresting. Radius needs to be a positive value for `IfcCircle` so use the absolute value.

~~~
#1983 = IFCCIRCLE(#1984, 20000.);
#1984 = IFCAXIS2PLACEMENT2D(#1985, #1986);
#1985 = IFCCARTESIANPOINT((0., 0.));
#1986 = IFCDIRECTION((1., 0.));
~~~

#### 3.4.1.2 Compute curve trimming parameters

$\Delta_{start} = \theta_{start} + \frac{1}{2}\pi = 1.56997860486$

$\Delta_{end} = \theta_{end} + \frac{1}{2}\pi = 1.55799301001$

$Segment Start = R\Delta_{start} = (20000.0)(1.56997860486) = 31399.5720971$

$Segment Length = R(\Delta_{end} - \Delta_{start}) = (20000.0)(1.55799301001 - 1.56997860486) = -239.711897$

~~~
#1974 = IFCCURVESEGMENT(.CONTSAMEGRADIENT., #1980, IFCLENGTHMEASURE(31399.5720971016), IFCLENGTHMEASURE(-239.711897000001), #1983);
~~~

#### 3.4.1.3 Placement of trimmed curve

X = `IfcAlignmentVerticalSegment.StartDistAlong` = 144.917656958471

Y = `IfcAlignmentVerticalSegment.StartHeight` = 25.3780433292418

$dx = cos(\theta_{start}) = cos(-8.177219398x10^{-4} = 0.9999966566$
$dy = sin(\theta_{start}) = sin(-8.177219398x10^{-4}) = -8.1772184868x10^{-4}$

~~~
#1980 = IFCAXIS2PLACEMENT2D(#1981, #1982);
#1981 = IFCCARTESIANPOINT((144.917656958471, 25.3780433292418));
#1982 = IFCDIRECTION((9.99999665665433E-1, -8.177218486836E-4));
~~~

## 3.5 Clothoid

:warning: **[Finish this]** :warning:

Start angle = atan(startGradient)

End angle = atan(endGradient)

Start radius = start radius of curvature

End radius = end radius of curvature

Set equal to horizontal length, adjust curve length until computed value
is equal to the specified horizontal length. Numerically solve 

![](images/image11.png)

## 3.6 Parabolic Arc
The geometric representation of vertical parabolic curves as a parabola is a little bit tricky.

Consider the equation for a parabola in the form 
 $y(x) = Ax^2 + Bx + C$

where:

A = (end gradient - start gradient)/(2 * horizontal length)

B = start gradient

C = start height

These parameters are obtained from the semantic definition of the curve segment, `IfcAlignmentVerticalSegment`.

The parent curve for `IfcCurveSegment.ParentCurve` is `IfcPolynomialCurve`. The coefficients are:

~~~
IfcPolynomialCurve.CoefficientsX = (0,1)
IfcPolynomialCurve.CoefficientsY = (C, B, A)
~~~

---
:information_source: Note 1: Even though vertical is typically Z, we are using 2.5D geometry and the coordinate system of gradient curve is "Distance along Horizontal", "Elevation" which is a 2D curve in the plane of the horizontal curve. When the `IfcGradientCurve` and `IfcCompositeCurve` are combined to get a 3D point, the elevation is then mapped to Z.

:information_source: Note 2: The coefficients A, B, and C must have the following unit of measure, consistent with the project units:

A = $Length{^-1}$

B = $Length^0$

C = $Length^1$

The coefficients of `IfcPolynomialCurve` expect real numbers without explictit unit of measure. This is a problem with the IFC Specification. See the discussion of `IfcAlignmentHorizontalSegment` and `IfcPolynomialCurve` for Cubic Transition Curve in [Section 2 - Horizontal Alignment](./2_Horizontal.md). Implicit units of measure are required for the polynomial coefficients.

---

The challenging part is `IfcCurveSegment.SegmentLength`. The length along the parabolic curve is needed.

The distance along a curve is

$s(x) = \int_{}^{}(\sqrt{(y')^{2} + 1}) dx$

The parabola equation is

 $y(x) = Ax^2 + Bx + C$

 and it's derivative is

 $y'(x) = 2Ax + B$

The equation along the parabolic curve is then:

$s(x) = \int_{}^{}\sqrt{4A^2x^2 + 4ABx + B^2 + 1} dx$

This equation can be solved numerically.

Alternatively, there is a closed form solution, see https://www.integral-table.com, equation #37.

$s(x)=\int_{}^{}\sqrt{ax^2 + bx + c} dx = \frac{b+2x}{4a}\sqrt{ax^2 + bx + c} + \frac{4ac-b^2}{8 a^\frac{3}{2}} ln\left|2ax + b + 2\sqrt{a(ax^2 + bx + c)}\right|$

Let

$a = 4A^2$

$b = 4AB$

$c = B^2 + 1$

Substitute into the above closed form equation. The curve length is

$Lc = s(L) - s(0.0)$

Finally, `IfcCurveSegment.SegmentLength = Lc`

In summary,

~~~
IfcCurveSegment.Placement = IfcAxis2Placement2D
with 
IfcAxis2Placement2D.Location=IfcCartesianPoint(start distance along, start height)
IfcAxis2Placement2D.RefDirection=IfcDirection(1,0)

IfcCurveSegment.SegmentStart=0.0

IfcCurveSegment.SegmentLength=Lc

IfcCurveSegment.ParentCurve = IfcPolynomialCurve
~~~
