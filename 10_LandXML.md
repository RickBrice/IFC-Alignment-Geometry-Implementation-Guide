# Section 10 - LandXML

Placeholder - in this section it is intended that there is a discussion of mapping LandXML alignment constructs to IFC 4.3

# Section 10 - LandXML to IFC Conversion

## 10.1 Introduction

LandXML 1.x is the dominant legacy format for civil alignment data; IFC 4x3 is the modern target. The goal of this chapter is to guide implementers through the non-obvious decisions and pitfalls that arise during conversion, drawn from practical experience.

## 10.2 Schema Conceptual Comparison

The following table provides a high-level mapping of the two data models.

|LandXML                       |IFC 4x3                                                        |
|------------------------------|---------------------------------------------------------------|
|`<Alignments>` / `<Alignment>`|`IfcAlignment` nested under `IfcProject` via `IfcRelAggregates`|
|`<CoordGeom>`                 |`IfcAlignmentHorizontal` nested via `IfcRelNests`              |
|`<Profile>` / `<ProfAlign>`   |`IfcAlignmentVertical` nested via `IfcRelNests`                |
|`<Cant>`                      |`IfcAlignmentCant` nested via `IfcRelNests`                    |
|`<StaEquation>`               |`IfcReferent` with stationing attributes                       |
|`<Units>`                     |`IfcUnitAssignment` in `IfcProject`                            |

The key conceptual difference between the two schemas is that LandXML describes geometry procedurally — PI-based for vertical alignment, point-to-point for horizontal — whereas IFC describes segments declaratively as typed business objects with a start point, radii, and length.

## 10.3 Units

LandXML carries explicit unit declarations (`<Metric>`, `<Imperial>`) for linear and angular measure. IFC requires all geometry in SI base units (metres, radians) or with an explicit `IfcConversionBasedUnit`.

Read `<Units>` before processing any geometry — all coordinate values depend on it.

**Linear units.** Convert foot and US Survey foot to metres as needed. Note that the US Survey foot and the international foot are not the same:

$$1\ \text{US Survey foot} = \frac{1200}{3937}\ \text{m} \approx 0.3048006\ \text{m}$$

$$1\ \text{international foot} = 0.3048\ \text{m (exact)}$$

Using the wrong conversion factor introduces a systematic error that compounds over long alignments.

**Angular units.** LandXML directions can be expressed in decimal degrees, grads, or radians. `IfcAlignmentHorizontalSegment.StartDirection` is always in radians. Apply the appropriate conversion before writing IFC output.

**Bearing convention.** LandXML directions are azimuths measured clockwise from North. IFC plane angles are measured counter-clockwise from the positive X-axis (East). The conversion is

$$\theta_{IFC} = \frac{\pi}{2} - \theta_{bearing}$$

where $\theta_{bearing}$ is in radians.

## 10.4 Horizontal Alignment

### 10.4.1 LandXML Horizontal Element Types

The LandXML `<CoordGeom>` element contains a sequence of `<Line>`, `<Curve>`, and `<Spiral>` child elements. Each maps to an `IfcAlignmentSegment` nested under `IfcAlignmentHorizontal`.

### 10.4.2 Direction from Geometry

LandXML lines and spirals often omit explicit direction attributes (`Dir`, `DirStart`) and rely on the geometry — start/end or start/PI points — to imply direction. `IfcAlignmentHorizontalSegment.StartDirection` is required. When the direction attribute is absent, compute it from the available geometry:

$$\theta = \arctan2(\Delta y, \Delta x)$$

then apply the bearing-to-IFC plane angle conversion from Section 10.3.

### 10.4.3 Circular Curve (`<Curve>` → `CIRCULARARC`)

`<Curve>` provides center, start, end, and radius. IFC requires the start point, the start direction (the tangent direction, not the radial direction), the signed radius, and the arc length.

Compute the tangent direction from the radial line by rotating 90°:

$$\theta_{tangent} = \arctan2(y_{start} - y_{center},\ x_{start} - x_{center}) + \text{sign} \cdot \frac{\pi}{2}$$

where $\text{sign} = +1$ for counter-clockwise (`rot="ccw"`) and $\text{sign} = -1$ for clockwise (`rot="cw"`). The signed radius passed to `IfcAlignmentHorizontalSegment` follows the same sign convention.

### 10.4.4 Spiral Type Mapping

The following table maps LandXML `spiType` values to `IfcAlignmentHorizontalSegmentTypeEnum`.

|LandXML `spiType`    |IFC Type      |Notes                                           |
|---------------------|--------------|------------------------------------------------|
|`clothoid`           |`CLOTHOID`    |Direct mapping                                  |
|`bloss`              |`BLOSSCURVE`  |Direct mapping                                  |
|`biquadratic`        |`HELMERTCURVE`|Direct mapping                                  |
|`biquadraticParabola`|`HELMERTCURVE`|Equivalent to biquadratic                       |
|`cubic`              |`CUBIC`       |Direct mapping                                  |
|`cubicParabola`      |`CUBIC`       |Equivalent to cubic                             |
|`cosine`             |`COSINECURVE` |Direct mapping                                  |
|`sinusoid`           |`SINECURVE`   |Direct mapping                                  |
|`sineHalfWave`       |`COSINECURVE` |Approximation — loss of fidelity, see note below|
|`japaneseCubic`      |`VIENNESEBEND`|Direct mapping                                  |
|`revBiquadratic`     |—             |No IFC equivalent, log warning and skip         |
|`revBloss`           |—             |No IFC equivalent, log warning and skip         |
|`revCosine`          |—             |No IFC equivalent, log warning and skip         |
|`revSinusoid`        |—             |No IFC equivalent, log warning and skip         |
|`radioid`            |—             |No IFC equivalent, log warning and skip         |
|`weinerBogen`        |—             |No IFC equivalent, log warning and skip         |


> **Note on `sineHalfWave`.** The LandXML specification describes the sine half-wavelength spiral as an approximation of a cosine spiral. Mapping it to `COSINECURVE` is therefore reasonable but not exact. Implementations should log a warning when this substitution is made.

### 10.4.5 Radius Sign Convention

LandXML uses `rot="cw"` / `rot="ccw"` to indicate curve direction. IFC encodes direction in the sign of `StartRadius` and `EndRadius`: a positive value indicates a left turn (counter-clockwise) and a negative value indicates a right turn (clockwise).

$$\text{sign} = \begin{cases} -1 & \text{if } rot = \texttt{cw} \ +1 & \text{if } rot = \texttt{ccw} \end{cases}$$

Apply this sign to both `StartRadius` and `EndRadius`.

### 10.4.6 Infinite Radius

LandXML represents an infinite start or end radius by omitting the attribute or by supplying `DBL_MAX`. IFC uses `0.0` in `IfcAlignmentHorizontalSegment.StartRadius` or `EndRadius` to indicate an infinite radius. Substitute `0.0` whenever the LandXML value is absent or exceeds a practical threshold.

### 10.4.7 Unhandled Horizontal Element Types

`<Chain>` and `<IrregularLine>` elements have no direct equivalent in the IFC alignment semantic model. Log a warning when these elements are encountered and skip them. If approximate geometric fidelity is acceptable, a `<Chain>` (polyline) could be decomposed into a sequence of `LINE` segments.

## 10.5 Vertical Alignment

### 10.5.1 LandXML Vertical Data Model

LandXML represents vertical geometry as a sequence of PVI-based elements under `<ProfAlign>`: `<PVI>`, `<ParaCurve>`, `<UnsymParaCurve>`, and `<CircCurve>`. This is fundamentally different from IFC’s segment-based model, which requires an explicit start station, start elevation, start grade, end grade, and length for each segment.

### 10.5.2 PVI-Based to Segment-Based Conversion

The core translation challenge is that LandXML locates vertical curves by their PVI station and curve length, while IFC needs each segment’s start station explicitly. The conversion procedure is:

1. Compute the entry grade from the PVI station and the previous PVI or curve endpoint.
1. The start station of a symmetric parabolic curve is $\text{PVI station} - L/2$.
1. The start elevation is computed by projecting back from the PVI along the entry grade: $e_{start} = e_{PVI} - g_1 \cdot L/2$.
1. Gradient segments fill any gap between the end of one curve and the start of the next.

### 10.5.3 Symmetric Parabolic Arc (`<ParaCurve>` → `PARABOLICARC`)

This is the standard vertical curve case. Given PVI station $s_{PVI}$, PVI elevation $e_{PVI}$, curve length $L$, entry grade $g_1$, and exit grade $g_2$:

$$s_{start} = s_{PVI} - \frac{L}{2}$$

$$e_{start} = e_{PVI} - g_1 \frac{L}{2}$$

Map to `IfcAlignmentVerticalSegment` with `PredefinedType = PARABOLICARC`, `StartDistAlong = s_{start} - s_{alignment\_start}`, `StartHeight = e_{start}`, `StartGradient = g_1`, `EndGradient = g_2`, `HorizontalLength = L`.

### 10.5.4 Asymmetric Parabolic Arc (`<UnsymParaCurve>` → Two `PARABOLICARC` Segments)

IFC has no asymmetric vertical curve type. The `<UnsymParaCurve>` must be split into two abutting `PARABOLICARC` segments. Given entry length $L_{in}$, exit length $L_{out}$, entry grade $g_1$, and exit grade $g_2$:

Compute the vertical offset from the composite curve to the PVI:

$$h = \frac{L_{in} \cdot L_{out} \cdot (g_2 - g_1)}{2(L_{in} + L_{out})}$$

The transition point between the two sub-curves occurs at the PVI station with elevation:

$$e_{transition} = e_{PVI} + h$$

The intermediate grade at the transition point is:

$$g_{mid} = g_1 + \frac{2h}{L_{in}}$$

Create two `PARABOLICARC` segments: the first from the curve start to the PVI station with grades $g_1$ and $g_{mid}$, and the second from the PVI station to the curve end with grades $g_{mid}$ and $g_2$.

### 10.5.5 Circular Vertical Curve (`<CircCurve>` → `CIRCULARARC`)

LandXML provides the radius and arc length. IFC `IfcAlignmentVerticalSegment` for `CIRCULARARC` accepts the radius directly in the `RadiusOfCurvature` attribute. Compute the start station and elevation the same way as for a symmetric parabolic arc, using $L/2$ as the half-length. Note that this is an approximation — the true tangent length of a circular vertical curve is $T = R \tan(\Delta/2)$ where $\Delta = L/R$, which differs from $L/2$ except for small deflection angles.

### 10.5.6 Start Station Offset

LandXML stations are absolute. `IfcAlignmentVerticalSegment.StartDistAlong` is measured from the start of the alignment. Subtract the alignment start station from every LandXML station:

$$\text{StartDistAlong} = s_{LandXML} - s_{alignment_start}$$

The alignment start station is found in `<Alignment staStart="...">` and must be read before processing any profile elements.

## 10.6 Cant

### 10.6.1 LandXML Cant Model

LandXML `<Cant>` uses `<CantStation>` points and `<CantSegment>` elements with left and right cant values at the start and end of each segment, along with a curve type designation.

### 10.6.2 Mapping to `IfcAlignmentCant`

Each `<CantSegment>` maps to an `IfcAlignmentCantSegment` with `StartCantLeft`, `StartCantRight`, `EndCantLeft`, `EndCantRight`, and `PredefinedType`. The cant segment type mapping follows the same spiral type table as horizontal alignment (Section 10.4.4).

### 10.6.3 Rail Head Distance

`IfcAlignmentCant.RailHeadDistance` is required and represents the distance between rail heads (track gauge). LandXML may carry gauge information in a `<Roadway>` or project-level element, or it may need to be supplied as an external parameter. The conversion must account for this value explicitly — it is used in the Viennese Bend cant factor calculation described in Section 2.

## 10.7 Stationing and Station Equations

### 10.7.1 Start Station

The LandXML `<Alignment staStart="...">` attribute gives the station at the beginning of the alignment. Map this to an `IfcReferent` with `PredefinedType = REFERENCEMARKER` at `DistanceAlong = 0.0`, with the station value stored as a property in an associated property set.

### 10.7.2 Station Equations (`<StaEquation>`)

LandXML `<StaEquation>` records station breaks where the back station and ahead station differ. Each equation maps to an additional `IfcReferent`. The relevant attributes are:

|LandXML Attribute|Meaning                                     |
|-----------------|--------------------------------------------|
|`staBack`        |Station value before the equation (incoming)|
|`staAhead`       |Station value after the equation (outgoing) |
|`staInternal`    |Continuous internal station (no breaks)     |

The `staInternal` value should equal `staAhead` in a well-formed LandXML file. Log a warning if `staInternal != staAhead`, as this indicates an unusual stationing condition that may require manual review.

## 10.8 IFC Project Structure

LandXML has no concept of project hierarchy. IFC requires a minimum entity graph regardless of what is in the LandXML file. The required structure is:

```
IfcProject
  └── IfcRelAggregates
        ├── IfcSite
        └── IfcAlignment
              └── IfcRelNests
                    ├── IfcAlignmentHorizontal
                    │     └── IfcRelNests → IfcAlignmentSegment (×n)
                    ├── IfcAlignmentVertical
                    │     └── IfcRelNests → IfcAlignmentSegment (×n)
                    └── IfcAlignmentCant (if cant data present)
                          └── IfcRelNests → IfcAlignmentSegment (×n)
```

The `IfcProject` must include an `IfcUnitAssignment` derived from the LandXML `<Units>` element (Section 10.3). The `IfcSite` provides the spatial context and local placement for the alignment.

## 10.9 Known Limitations and Unresolved Issues

The following issues are known limitations of the LandXML-to-IFC conversion and should be documented for users of any converter implementation.

**Unhandled spiral types.** The LandXML spiral types `radioid`, `weinerBogen`, `revBiquadratic`, `revBloss`, `revCosine`, and `revSinusoid` have no IFC equivalent. Segments of these types are skipped with a warning.

**Unhandled horizontal element types.** `<Chain>` (polyline) and `<IrregularLine>` elements are skipped. A future implementation could decompose them into sequences of `LINE` segments.

**`sineHalfWave` approximation.** Mapped to `COSINECURVE` as an approximation. The two curves are similar but not identical.

**Circular vertical curve half-length approximation.** The start station of a `<CircCurve>` is approximated as $s_{PVI} - L/2$. The exact value depends on the tangent length, which requires iteration for large deflection angles.

**Asymmetric parabolic arc split.** The split of `<UnsymParaCurve>` into two `PARABOLICARC` segments is geometrically correct but results in two IFC segments where LandXML had one. Downstream tools must be able to handle this.

**Imperial units.** Imperial linear unit conversion (foot, US Survey foot) must be applied to all coordinate values. Partial implementations that read the unit declaration but do not scale the coordinates will produce incorrect geometry.

**No support for LandXML surface or roadway data.** `<Roadway>`, `<Survey>`, `<Surfaces>`, and other LandXML elements beyond alignment geometry are out of scope for an alignment-focused converter.
