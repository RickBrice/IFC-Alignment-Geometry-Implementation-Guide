outline:
* Introduction — what these representations are and when they arise; contrast with parametric geometry in Sections 2–4
* IfcPolyline
  - Schema structure: Points attribute (list of IfcCartesianPoint), 2D or 3D
  - Use cases: survey of existing alignment, early planning sketch, GIS import
  - Prohibition on coincident points and what that means for zero-length segments
* IfcIndexedPolyCurve
  - Schema structure: Points (IfcCartesianPointList), Segments (optional), SelfIntersect
  - Straight-segment and arc-segment variants
  - Same coincident-point constraints as IfcPolyline when only straight segments are used
* Incompatibility with the full semantic alignment definition
  - Recap the zero-length terminal segment requirement (from Section 1.4)
  - Coincident points are the only mechanism that could satisfy that requirement in a polyline
  - IfcPolyline WHERE rule WR1 prohibits coincident consecutive points
  - IfcIndexedPolyCurve has no coincident-point prohibition in the schema, but coincident
    control points produce degenerate segments that validators may reject
  - Practical consequence: these geometry types cannot be paired with a full IfcAlignment
    semantic definition; they stand alone as geometry-only representations
* Accuracy considerations
  - Polylines discretize curves: tangent and curvature are discontinuous at every vertex
  - Point density governs accuracy; no standard density is prescribed by IFC
  - Comparison with parametric IfcCurveSegment representations
  - Note on using these for visualization vs. engineering computation

# Section 5 - Approximate Alignment Geometry

## 5.0 Introduction

The parametric `IfcCurveSegment`-based representations discussed in Sections 2 through 4
describe alignment geometry exactly: each segment is defined by a closed-form equation,
and position, tangent, and curvature can be evaluated analytically at any arc-length
along the curve. This precision is essential when the geometry will drive construction,
linear placement, or quantity takeoff.

Not all alignment data arrives in this form. Field surveys of existing infrastructure
typically produce a series of measured points rather than fitted curve parameters.
Early-stage planning alignments may exist only as a sketched centerline digitized from a
map. GIS systems commonly store linear features as coordinate strings. The IFC
specification accommodates these cases through two additional representation types:
`IfcPolyline` and `IfcIndexedPolyCurve`.

Both types are **discrete** rather than parametric: geometry is defined entirely by a
sequence of control points, with linear interpolation between them. The result is a
piecewise-linear approximation whose accuracy depends on the density of the control
points. Because tangent direction changes abruptly at each vertex, these representations
carry no curvature information and cannot distinguish a tangent from a curve — the
geometry encodes only position.

The IFC specification lists `IfcPolyline` or `IfcIndexedPolyCurve` as valid
`IfcAlignment` representations for both 2D horizontal alignments (planning/mapping
contexts) and full 3D alignments (survey-derived). See Section 1.5 for the full list of
valid representation types.

## 5.1 IfcPolyline

`IfcPolyline` is the simplest IFC curve type: an ordered list of two or more
`IfcCartesianPoint` instances connected by straight line segments.

```
ENTITY IfcPolyline
  SUBTYPE OF (IfcBoundedCurve);
    Points : LIST [2:?] OF IfcCartesianPoint;
  WHERE
    WR1 : ((SIZEOF(Points) > 2) AND
           IfcMeasureValue(IfcGeometricRepresentationContext.getPrecision()) > 0.0
           -- consecutive points must not be coincident
          ) OR (SIZEOF(Points) = 2);
END_ENTITY;
```

The `Points` list defines vertices in order. Consecutive pairs of points define line
segments. The curve begins at `Points[1]` and ends at `Points[SIZEOF(Points)]`.

### 5.1.1 Dimensional Use

`IfcPolyline` may be used in 2D or 3D depending on the coordinate dimensionality of its
`Points`:

- **2D** — for a horizontal-only alignment representation, used in early planning or as
  a map footprint. Coordinates are (Easting, Northing).
- **3D** — for a survey-derived alignment where field measurements provide (Easting,
  Northing, Elevation) at each measured point.

### 5.1.2 The Coincident-Point Prohibition

`IfcPolyline` WHERE rule WR1 requires that no two consecutive points be coincident (i.e.,
within the geometric precision of the model). This constraint has a significant
consequence for alignment use: as established in Section 1.4, the last
`IfcAlignmentSegment` in every semantic alignment layout must be zero length. The only
way a polyline vertex could produce a zero-length segment would be to place two
coincident points — which WR1 explicitly forbids.

The result is a fundamental incompatibility: **`IfcPolyline` cannot be paired with a
complete semantic alignment definition** that includes zero-length terminal segments.
Section 5.3 discusses this constraint in detail.

## 5.2 IfcIndexedPolyCurve

`IfcIndexedPolyCurve` is a more capable variant that stores its control-point coordinates
in a compact `IfcCartesianPointList` (indexed rather than individual entities) and
optionally defines curve segments by index references.

```
ENTITY IfcIndexedPolyCurve
  SUBTYPE OF (IfcBoundedCurve);
    Points       : IfcCartesianPointList;
    Segments     : OPTIONAL LIST [1:?] OF IfcSegmentIndexSelect;
    SelfIntersect: OPTIONAL IfcBoolean;
END_ENTITY;
```

When `Segments` is omitted, the curve is equivalent to `IfcPolyline`: all points are
connected in sequence by straight line segments. When `Segments` is provided, individual
segments can be declared as either straight (`IfcLineIndex`) or circular-arc
(`IfcArcIndex`). Arc segments are defined by three indexed points — start, an intermediate
point on the arc, and end — allowing `IfcIndexedPolyCurve` to represent a mix of tangent
runs and true circular arcs without transition curves.

### 5.2.1 Arc Segments

An `IfcArcIndex` segment `[i, j, k]` defines a circular arc passing through the three
indexed points: point $i$ is the start, point $j$ is any intermediate point on the arc,
and point $k$ is the end. The unique circle through three non-collinear points in the
plane is used. This makes `IfcIndexedPolyCurve` more geometrically expressive than
`IfcPolyline` for survey data collected along curves — provided the surveyor measured a
mid-arc point in addition to the endpoints.

Arc segments do not provide tangent continuity at junctions with adjacent segments unless
the geometry happens to be tangent; the specification does not enforce it.

### 5.2.2 Coincident-Point Constraints

`IfcIndexedPolyCurve` does not have an explicit WHERE rule prohibiting coincident
consecutive points in the same way `IfcPolyline` does. However, consecutive coincident
control points that produce zero-length line segments are geometrically degenerate: the
tangent direction is undefined, and IFC validation tools may reject the model. The
practical constraint is the same: zero-length terminal segments cannot be produced.

## 5.3 Incompatibility with the Full Semantic Alignment Definition

### 5.3.1 The Zero-Length Segment Requirement

Section 1.4 establishes that every `IfcAlignmentHorizontal`, `IfcAlignmentVertical`, and
`IfcAlignmentCant` must terminate with a zero-length `IfcAlignmentSegment`. When a
geometric representation accompanies the semantic definition, the corresponding last
`IfcCurveSegment` must also be zero length. This requirement exists to provide a
well-defined endpoint for the final segment.

A zero-length `IfcCurveSegment` trims a zero-length arc from its parent curve — the trim
start and trim end are the same point. For `IfcLine`, `IfcCircle`, or any of the
transition spiral types this is a well-defined degenerate case: the segment collapses to
a point, carrying only the position and tangent at that location.

### 5.3.2 Why Polylines Cannot Satisfy This Requirement

An `IfcPolyline` produces a zero-length segment only if two consecutive vertices are
coincident. WHERE rule WR1 explicitly prohibits this. There is no other mechanism within
`IfcPolyline` to represent a zero-length terminal segment.

`IfcIndexedPolyCurve` has no equivalent schema-level prohibition, but inserting a
coincident point to force a zero-length segment is semantically unusual and may trigger
validation warnings or errors in tools that check for degenerate geometry.

The consequence is that **neither `IfcPolyline` nor `IfcIndexedPolyCurve` can correctly
serve as the geometric counterpart to a full semantic alignment definition in a single
combined model.** These curve types must be used as standalone geometry-only alignment
representations, without an accompanying `IfcAlignmentHorizontal` (or vertical/cant)
semantic nest.

### 5.3.3 Guidance on Combined vs. Standalone Use

| Scenario | Appropriate representation |
|---|---|
| Survey of existing alignment, no design intent | `IfcPolyline` or `IfcIndexedPolyCurve` (standalone) |
| Early planning sketch, no curve parameters | `IfcPolyline` or `IfcIndexedPolyCurve` (standalone) |
| GIS centerline import for spatial context | `IfcPolyline` or `IfcIndexedPolyCurve` (standalone) |
| Design alignment with full curve parameters | `IfcCurveSegment`-based `IfcCompositeCurve` or `IfcGradientCurve` |
| Design alignment with semantic and geometric definitions | `IfcCurveSegment`-based curves paired with full semantic nest |

*Table 5.3.3-1 — Guidance on when to use polyline vs. parametric alignment representations*

## 5.4 Accuracy Considerations

Because `IfcPolyline` and `IfcIndexedPolyCurve` discretize a continuous curve into
straight segments (and, for `IfcIndexedPolyCurve`, circular arcs), the geometric accuracy
of the representation depends entirely on the density of control points. IFC prescribes
no minimum point spacing or maximum chord error for these representations.

For alignment-based applications that derive positions or offsets from the curve — such
as `IfcLinearPlacement` or `IfcOffsetCurveByDistances` — the discretization error
propagates into those derived positions. At every vertex, the tangent direction changes
discontinuously, producing a kink in the curve. Quantities that depend on tangent
direction (lateral offset perpendicularity, cant angle) are undefined or poorly defined
at these kinks.

For visualization and spatial context purposes, polyline representations are adequate
provided the point density is sufficient to render the curve smoothly at the intended
display scale. For engineering computation, parametric representations (Sections 2–4)
should be used wherever curve parameters are known.
