# Notation

## Scalars and Parameters

### Arc-Length and Distance

| Symbol | Definition |
|--------|------------|
| $s$ | Arc-length parameter along the parent curve |
| $s_0$ | Arc-length at the start of the trim; equals `SegmentStart` |
| $L$ | Segment length; equals `SegmentLength` |
| $\ell$ | Horizontal distance from the segment start; evaluation variable in vertical and cant sections |
| $d$ | Distance measured along the horizontal `IfcCompositeCurve` |
| $d_0$ | Distance along at the trim start; $d_0 = x(s_0)$ |
| $h_l$ | Horizontal length of a vertical segment; equals `HorizontalLength` |

### Angles

| Symbol | Definition |
|--------|------------|
| $\theta(s)$ | Bearing angle at arc-length $s$ in the horizontal plane |
| $\theta(\ell)$ | Tangent angle at horizontal distance $\ell$; grade angle $\tan^{-1}(g(\ell))$ in the vertical plane; slope of deviating elevation $\tan^{-1}(D'(\ell))$ in the cant plane |
| $\theta_0$ | Tangent angle at the trim start $s_0$ |
| $\theta_p$ | Tangent angle of `IfcCurveSegment.Placement.RefDirection` |
| $\theta_v$ | Grade direction angle; $\theta_v = \tan^{-1}(dy_v / dx_v)$ |
| $\phi$ | Cross-slope angle; angle from the transverse $y$-axis to the `Axis` vector |
| $\phi_s,\ \phi_e$ | Cross-slope angle at the start and end of a cant segment |
| $\phi_p$ | Cross-slope angle of `IfcCurveSegment.Placement.Axis` |
| $\Delta$ | Sweep angle of a circular arc; angle subtended at the center by the arc from the trim start to an evaluation point |
| $\Delta_0$ | Angular position of the trim-start point on the parent circle; angle from the circle's positive $x$-axis to the radius vector at the trim start (Section 3.4) |
| $\Delta_{pc}$ | Radial angle at the evaluation point on the parent circle; $\Delta_{pc} = \Delta_0 - \Delta$ for a clockwise segment, $\Delta_0 + \Delta$ for counter-clockwise (Section 3.4) |

### Curvature and Radius

| Symbol | Definition |
|--------|------------|
| $\kappa(s)$ | Curvature at arc-length $s$; $\kappa = 1/R$ |
| $\kappa_s$ | Curvature at the segment start; $\kappa_s = 1/R_s$ |
| $\kappa_e$ | Curvature at the segment end; $\kappa_e = 1/R_e$ |
| $R$ | Radius of curvature |
| $R_s$ | Radius at the segment start; equals `StartRadius` |
| $R_e$ | Radius at the segment end; equals `EndRadius` |
| $f$ | Cumulative change in curvature over the segment; $f = L(1/R_e - 1/R_s)$ |

### Grade

| Symbol | Definition |
|--------|------------|
| $g(s)$ | Gradient (slope) at arc-length $s$ |
| $g_s$ | Gradient at the segment start; equals `StartGradient` |
| $g_e$ | Gradient at the segment end; equals `EndGradient` |

### Position and Elevation

| Symbol | Definition |
|--------|------------|
| $x(s),\ y(s)$ | Coordinates of the parent curve at arc-length $s$ |
| $x_0,\ y_0$ | Parent curve position at the trim start $s_0$ |
| $x_p,\ y_p$ | Placement location; equals `IfcCurveSegment.Placement.Location` |
| $z$ | Elevation (vertical $y$-coordinate mapped to 3D $z$) |
| $z_0$ | Elevation at the trim start; equals `StartHeight` |
| $C_x,\ C_y$ | Center coordinates of a circular arc parent curve |
| $c$ | Chord length from the trim start to an evaluation point |

### Cant (Deviating Elevation)

| Symbol | Definition |
|--------|------------|
| $D(s)$ | Deviating elevation at arc-length $s$; vertical offset of the track centerline from the gradient curve |
| $D_0$ | Deviating elevation at the trim start; $D_0 = D(s_0)$ |
| $D_s,\ D_e$ | Deviating elevation at the segment start and end; $D_s = (D_{sl} + D_{sr})/2$ |
| $D_{sl},\ D_{sr}$ | Left and right cant elevation at the segment start; equals `StartCantLeft`, `StartCantRight` |
| $D_{el},\ D_{er}$ | Left and right cant elevation at the segment end; equals `EndCantLeft`, `EndCantRight` |
| $D_p$ | Deviating elevation component of `IfcCurveSegment.Placement.Location` |
| $\Delta D$ | Change in deviating elevation over the segment; $\Delta D = D_e - D_s$ |
| $D_{rh}$ | Rail head distance; center-to-center distance between railheads; equals `RailHeadDistance` |
| $\beta_s$ | Cross-slope ratio at the segment start; $\beta_s = (D_{sr} - D_{sl}) / D_{rh}$ |
| $\beta_e$ | Cross-slope ratio at the segment end; $\beta_e = (D_{er} - D_{el}) / D_{rh}$ |
| $h_{cg}$ | Gravity centerline height; height of the vehicle center of gravity above the rail plane; equals `GravityCenterLineHeight` |
| $cf$ | Cant factor; $cf = -420\,(h_{cg}/L)(\beta_e - \beta_s)$; scales the Viennese Bend polynomial coefficients |

### Spiral Curve Coefficients

| Symbol | Definition |
|--------|------------|
| $A$ | Clothoid constant |
| $u$ | Clothoid unit parameterization parameter; $u = s\,/\,\lvert A\sqrt{\pi}\rvert$ |
| $A_i$ | Dimensional polynomial coefficient (with units) for spiral and parabolic curves |
| $a_i$ | Normalized (dimensionless) polynomial coefficient prior to scaling |
| $A_{i1},\ A_{i2}$ | Coefficient $A_i$ for the first and second halves of a Helmert segment |

---

## Vectors

| Symbol | Definition |
|--------|------------|
| $dx,\ dy$ | Horizontal tangent direction components; $dx = \cos\theta$, $dy = \sin\theta$ |
| $dx_p,\ dy_p$ | Tangent direction components at the placement; $dx_p = \cos\theta_p$, $dy_p = \sin\theta_p$ |
| $dx_v,\ dy_v$ | Grade direction components from $M_v$; $dx_v = \cos\theta_v$, $dy_v = \sin\theta_v$ |
| $\mathbf{RefDir}_p$ | Reference direction of `IfcCurveSegment.Placement`; equals `Placement.RefDirection` |
| $\mathbf{Axis}_p$ | Axis direction of `IfcCurveSegment.Placement`; equals `Placement.Axis` |
| $\mathbf{X}_p,\ \mathbf{Y}_p,\ \mathbf{Z}_p$ | Orthonormal basis vectors of the placement frame |

---

## Matrices

All matrices are $4 \times 4$ homogeneous transformation matrices. Column 4 carries position; columns 1–3 carry the frame orientation.

| Symbol | Definition |
|--------|------------|
| $M_{CSP}$ | Curve segment placement matrix; constructed from `IfcCurveSegment.Placement`; maps the trimmed segment into the alignment coordinate system |
| $M_N$ | Normalization matrix; translates the trim-start point to the origin and rotates the tangent to align with the positive $x$-direction |
| $M_{PC}$ | Parent curve matrix at the evaluation point; encodes $x(s)$, $y(s)$, and $\theta(s)$ |
| $M_h$ | Horizontal placement matrix; $M_h = M_{CSP}\,M_N\,M_{PC}$ |
| $M_v$ | Vertical placement matrix; $M_v = M_{CSP}\,M_N\,M_{PC}$ in the (distance-along, elevation) plane |
| $M'_v$ | Modified vertical matrix; rows 2 and 3 of $M_v$ swapped, distance-along component zeroed, for multiplication with $M_h$ |
| $M''_v$ | Orientation-only form of $M'_v$; column 4 set to $(0,0,0,1)^T$ for use in the cant 3D composition |
| $M_c$ | Cant placement matrix; $M_c = M_{CSP}\,M_N\,M_{PC}$ in the (distance-along, deviating elevation) plane |
| $M'_c$ | Modified cant matrix; deviating elevation moved from row 2 to row 3, distance-along component zeroed, for multiplication |
| $M''_c$ | Orientation-only form of $M'_c$; column 4 set to $(0,0,0,1)^T$ for use in the cant 3D composition |
| $M_{3D}$ | Full 3D placement matrix combining horizontal and vertical; $M_{3D} = M_h\,M'_v$ |
| $M_{3D,cant}$ | Full 3D placement matrix combining horizontal, vertical, and cant; $M_{3D,cant} = M_h\,M''_v\,M''_c$ |
| $I$ | $4 \times 4$ identity matrix |
