# Appendix A — LandXML to IFC Conversion

## A.0 Introduction

LandXML 1.x is the dominant legacy format for civil alignment data; IFC 4x3 is the modern target. The goal of this chapter is to guide implementers through the decisions and pitfalls that arise during conversion, drawn from practical experience implementing [LX2IFC](https://github.com/RickBrice/LX2IFC), the author's open-source LandXML to IFC conversion program. LX2IFC focuses on alignment conversion and is otherwise incomplete as a general-purpose LandXML to IFC conversion utility; it remains a work in progress.

## A.1 Schema Conceptual Comparison

The following table provides a high-level mapping of the two data models.

|LandXML                       |IFC 4x3                                                        |
|------------------------------|---------------------------------------------------------------|
|`<Alignments>` / `<Alignment>`|`IfcAlignment` nested under `IfcProject` via `IfcRelAggregates`|
|`<CoordGeom>`                 |`IfcAlignmentHorizontal` nested via `IfcRelNests`              |
|`<Profile>` / `<ProfAlign>`   |`IfcAlignmentVertical` nested via `IfcRelNests`                |
|`<Cant>`                      |`IfcAlignmentCant` nested via `IfcRelNests`                    |
|`<StaEquation>`               |`IfcReferent` with stationing attributes and properties                       |
|`<Units>`                     |`IfcUnitAssignment` in `IfcProject`                            |

*Table A.1-1 — LandXML to IFC schema conceptual comparison*

The key conceptual difference between the two schemas is that LandXML defines geometry through PI and PVI points with derived curve parameters, whereas IFC defines geometry as explicit typed segments each carrying a start condition, length, and curve parameters.

## A.2 Units

LandXML carries explicit unit declarations (`<Metric>`, `<Imperial>`) for linear and angular measure. IFC requires all geometry in SI base units (meters, radians) or with an explicit `IfcConversionBasedUnit`.

Read `<Units>` before processing any geometry — all coordinate values depend on it.

**Linear units.** Convert foot and US Survey foot to meters as needed. Note that the US Survey foot and the international foot are not the same:

$$1\ \text{US Survey foot} = \frac{1200}{3937}\ \text{m} \approx 0.3048006\ \text{m}$$

$$1\ \text{international foot} = 0.3048\ \text{m (exact)}$$

Using the wrong conversion factor introduces a systematic error that compounds over long alignments.

**Angular units.** LandXML directions can be expressed in decimal degrees, grads, or radians. IFC angular units are declared in `IfcUnitAssignment` — the SI base unit is radians, but `IfcConversionBasedUnit` can declare degrees, grads, or any other angular unit. When constructing an IFC model from LandXML, the converter controls what angular unit the output model declares; declaring radians (the default) avoids an extra conversion step and is the most common choice.

**Bearing convention.** LandXML directions are azimuths measured clockwise from North. IFC plane angles are measured counter-clockwise from the positive X-axis (East). The conversion is

$$\theta_{IFC} = \frac{\pi}{2} - \theta_{bearing}$$

where $\theta_{bearing}$ is in radians.

## A.3 Horizontal Alignment

### A.3.1 LandXML Horizontal Element Types

The LandXML `<CoordGeom>` element contains a sequence of `<Line>`, `<Curve>`, and `<Spiral>` child elements. Each maps to an `IfcAlignmentSegment` nested under `IfcAlignmentHorizontal`.

### A.3.2 Direction from Geometry

LandXML lines and spirals often omit explicit direction attributes (`Dir`, `DirStart`) and rely on the geometry — start/end or start/PI points — to imply direction. `IfcAlignmentHorizontalSegment.StartDirection` is required. When the direction attribute is absent, compute it from the available geometry:

$$\theta = \operatorname{atan2}(\Delta y, \Delta x)$$

then apply the bearing-to-IFC plane angle conversion from Section A.2.

### A.3.3 Circular Curve (`<Curve>` → `CIRCULARARC`)

`<Curve>` provides center, start, end, and radius. IFC requires the start point, the start direction (the tangent direction, not the radial direction), the signed radius, and the arc length.

Compute the tangent direction from the radial line by rotating 90°:

$$\theta_{tangent} = \operatorname{atan2}(y_{start} - y_{center},\ x_{start} - x_{center}) + \text{sign} \cdot \frac{\pi}{2}$$

where $\text{sign} = +1$ for counter-clockwise (`rot="ccw"`) and $\text{sign} = -1$ for clockwise (`rot="cw"`). The signed radius passed to `IfcAlignmentHorizontalSegment` follows the same sign convention.

### A.3.4 Spiral Type Mapping

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
|`revBiquadratic`     |—             |IFC mapping unknown, log warning and skip       |
|`revBloss`           |—             |IFC mapping unknown, log warning and skip       |
|`revCosine`          |—             |IFC mapping unknown, log warning and skip       |
|`revSinusoid`        |—             |IFC mapping unknown, log warning and skip       |
|`radioid`            |—             |IFC mapping unknown, log warning and skip       |
|`weinerBogen`        |—             |IFC mapping unknown, log warning and skip       |

*Table A.3.4-1 — LandXML spiType to IFC type mapping*

> **Note:** The LandXML specification describes the sine half-wavelength spiral as an approximation of a cosine spiral. Mapping it to `COSINECURVE` is therefore reasonable but not exact. Implementations should log a warning when this substitution is made.

### A.3.5 Radius Sign Convention

LandXML uses `rot="cw"` / `rot="ccw"` to indicate curve direction. IFC encodes direction in the sign of `StartRadius` and `EndRadius`: a positive value indicates a left turn (counter-clockwise) and a negative value indicates a right turn (clockwise).

$$\text{sign} = \begin{cases} -1 & \text{if } rot = \mathtt{cw} \\ +1 & \text{if } rot = \mathtt{ccw} \end{cases}$$

Apply this sign to both `StartRadius` and `EndRadius`.

### A.3.6 Infinite Radius

LandXML represents an infinite start or end radius by omitting the attribute or by supplying the value `INF`. IFC uses `0.0` in `IfcAlignmentHorizontalSegment.StartRadius` or `EndRadius` to indicate an infinite radius. Substitute `0.0` whenever the LandXML value is absent or is `INF`.

## A.4 Vertical Alignment

### A.4.1 LandXML Vertical Data Model

LandXML represents vertical geometry as a sequence of PVI-based elements under `<ProfAlign>`: `<PVI>`, `<ParaCurve>`, `<UnsymParaCurve>`, and `<CircCurve>`. This is fundamentally different from IFC’s segment-based model, which requires an explicit start station, start elevation, start grade, end grade, and length for each segment.

### A.4.2 PVI-Based to Segment-Based Conversion

The core translation challenge is that LandXML locates vertical curves by their PVI station and curve length, while IFC needs each segment’s start station explicitly. The conversion procedure is:

1. Compute the entry grade from the PVI station and the previous PVI or curve endpoint.
1. The start station of a symmetric parabolic curve is $\text{PVI station} - L/2$.
1. The start elevation is computed by projecting back from the PVI along the entry grade: $e_{start} = e_{PVI} - g_1 \cdot L/2$.
1. Gradient segments fill any gap between the end of one curve and the start of the next.

### A.4.3 Symmetric Parabolic Arc (`<ParaCurve>` → `PARABOLICARC`)

This is the standard vertical curve case. Given PVI station $s_{PVI}$, PVI elevation $e_{PVI}$, curve length $L$, entry grade $g_1$, and exit grade $g_2$:

$$s_{start} = s_{PVI} - \frac{L}{2}$$

$$e_{start} = e_{PVI} - g_1 \frac{L}{2}$$

Map to `IfcAlignmentVerticalSegment` with `PredefinedType = PARABOLICARC`, `StartDistAlong = s_{start} - s_{alignment\_start}`, `StartHeight = e_{start}`, `StartGradient = g_1`, `EndGradient = g_2`, `HorizontalLength = L`.

### A.4.4 Asymmetric Parabolic Arc (`<UnsymParaCurve>` → Two `PARABOLICARC` Segments)

IFC has no asymmetric vertical curve type. The `<UnsymParaCurve>` must be split into two abutting `PARABOLICARC` segments. Given entry length $L_{in}$, exit length $L_{out}$, entry grade $g_1$, and exit grade $g_2$:

Compute the vertical offset from the composite curve to the PVI:

$$h = \frac{L_{in} \cdot L_{out} \cdot (g_2 - g_1)}{2(L_{in} + L_{out})}$$

The transition point between the two sub-curves occurs at the PVI station with elevation:

$$e_{transition} = e_{PVI} + h$$

The intermediate grade at the transition point is:

$$g_{mid} = g_1 + \frac{2h}{L_{in}}$$

Create two `PARABOLICARC` segments: the first from the curve start to the PVI station with grades $g_1$ and $g_{mid}$, and the second from the PVI station to the curve end with grades $g_{mid}$ and $g_2$.

### A.4.5 Circular Vertical Curve (`<CircCurve>` → `CIRCULARARC`)

LandXML provides the radius and arc length. IFC `IfcAlignmentVerticalSegment` for `CIRCULARARC` accepts the radius directly in the `RadiusOfCurvature` attribute. Compute the start station and elevation the same way as for a symmetric parabolic arc, using $L/2$ as the half-length. Note that this is an approximation — the true tangent length of a circular vertical curve is $T = R \tan(\Delta/2)$ where $\Delta = L/R$, which differs from $L/2$ except for small deflection angles.

### A.4.6 Station to Distance Along

LandXML vertical profile elements are positioned by station. `IfcAlignmentVerticalSegment.StartDistAlong` is distance along the horizontal alignment measured from the alignment start — a continuous value with no breaks. These are not the same thing whenever station equations are present.

In the simplest case — no station equations — the conversion is:

$$\text{StartDistAlong} = s_{LandXML} - s_{alignment\_start}$$

where $s_{alignment\_start}$ is read from `<Alignment staStart="...">`.

When station equations are present, the station numbering is discontinuous: a gap or overlap at each equation point means a given station value does not map to a unique physical distance without knowing which zone it falls in. The conversion must walk the list of `<StaEquation>` elements in order, accumulating the physical distance up to each equation point, then apply the appropriate offset for the zone containing the target station. The `staInternal` attribute on `<StaEquation>` gives the continuous internal distance and can serve as a cross-check.

## A.5 Cant

### A.5.1 LandXML Cant Model

LandXML `<Cant>` uses `<CantStation>` points and `<CantSegment>` elements with left and right cant values at the start and end of each segment, along with a curve type designation.

### A.5.2 Mapping to `IfcAlignmentCant`

Each `<CantSegment>` maps to an `IfcAlignmentCantSegment` with `StartCantLeft`, `StartCantRight`, `EndCantLeft`, `EndCantRight`, and `PredefinedType`. The cant segment type mapping follows the same spiral type table as horizontal alignment (Section A.3.4).

### A.5.3 Rail Head Distance

`IfcAlignmentCant.RailHeadDistance` is the distance between rail heads (track gauge). In LandXML, this value is the `gauge` attribute on the `<Cant>` element:

```xml
<Cant name="001" gauge="1.524" rotationPoint="insideRail">
```

Map `gauge` directly to `IfcAlignmentCant.RailHeadDistance`. The value is in the model's declared length units.

### A.5.4 Rotation Point Mapping

The `rotationPoint` attribute on `<Cant>` indicates which point on the cross-section serves as the pivot for superelevation rotation. LandXML defines three values: `insideRail`, `centerline`, and `outsideRail`. The `curvature` attribute on each `<CantStation>` indicates whether the curve is clockwise (`cw`, right turn) or counter-clockwise (`ccw`, left turn), which determines which physical rail is on the inside or outside.

`IfcAlignmentCantSegment` has no explicit rotation point attribute. Instead, rotation point is encoded implicitly through the combination of `StartCantLeft`, `StartCantRight`, `EndCantLeft`, and `EndCantRight` values. A zero cant value on one side indicates the pivot is on that side; equal and opposite values indicate centerline rotation.

Table A.5.4-1 gives the IFC cant values in terms of the LandXML `appliedCant` magnitude $c$ for each combination of `curvature` and `rotationPoint`:

| `curvature` | `rotationPoint` | `CantLeft` | `CantRight` |
|-------------|-----------------|------------|-------------|
| `ccw` (left turn, right = outside) | `insideRail` | $0$ | $+c$ |
| `ccw` (left turn, right = outside) | `centerline` | $-c/2$ | $+c/2$ |
| `ccw` (left turn, right = outside) | `outsideRail` | $-c$ | $0$ |
| `cw` (right turn, left = outside) | `insideRail` | $+c$ | $0$ |
| `cw` (right turn, left = outside) | `centerline` | $+c/2$ | $-c/2$ |
| `cw` (right turn, left = outside) | `outsideRail` | $0$ | $-c$ |

*Table A.5.4-1 — LandXML curvature and rotationPoint to IFC CantLeft/CantRight mapping*

Apply the same logic to both the start and end values of each segment. The `rotationPoint` is constant for the entire `<Cant>` element; `curvature` and `appliedCant` are read from each `<CantStation>` and applied to the corresponding segment start and end positions.

## A.6 Stationing and Station Equations

### A.6.1 Start Station

The LandXML `<Alignment staStart="...">` attribute gives the station at the beginning of the alignment. Map this to an `IfcReferent` with `PredefinedType = STATION`, with the station value stored in `Pset_Stationing.Station`. See Chapter 9 for the full `IfcReferent` and `Pset_Stationing` structure.

### A.6.2 Station Equations (`<StaEquation>`)

LandXML `<StaEquation>` records station breaks where the back station and ahead station differ. Each equation maps to an additional `IfcReferent`. The relevant attributes are:

|LandXML Attribute|Meaning                                     |
|-----------------|--------------------------------------------|
|`staBack`        |Station value before the equation (incoming)|
|`staAhead`       |Station value after the equation (outgoing) |
|`staInternal`    |Continuous internal station (no breaks)     |

*Table A.6.2-1 — LandXML station equation attributes*

Map each `<StaEquation>` to an `IfcReferent` as follows:

- `staBack` → `Pset_Stationing.IncomingStation` (the station value on the incoming side of the break)
- `staAhead` → `Pset_Stationing.Station` (the station value on the outgoing side)
- `staInternal` → the `DistanceAlong` value in `IfcPointByDistanceExpression` for the referent's `IfcLinearPlacement`

`staInternal` is the continuous internal distance along the alignment with no station breaks. It is therefore the correct value to use as `DistanceAlong` — it maps directly to arc-length along the horizontal curve without any equation adjustment. If `staInternal` is absent, compute `DistanceAlong` by walking the equation list as described in Section A.4.6.

The resulting `IfcReferent` instances, including the starting station referent from A.6.1, are nested under the `IfcAlignment` via a dedicated `IfcRelNests` relationship in order of increasing `DistanceAlong`. See [Chapter 9](9_Referents_and_Stationing.md) for the complete `IfcReferent` structure, the nesting requirements, and the algorithm for converting station labels to `DistanceAlong` when equations are present.
