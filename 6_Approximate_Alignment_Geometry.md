# Chapter 6 — Approximate Alignment Geometry

## 6.0 Introduction

The parametric `IfcCurveSegment`-based representations described in Sections 2 through 4
provide closed-form equations for position, tangent, and curvature at any arc-length along
the alignment. That precision is essential when geometry drives design, construction staking,
linear placement, or quantity takeoff.

Not all alignment data arrives in this form. Field surveys of existing infrastructure
may produce a series of measured points rather than fitted curve parameters. Early-stage
planning alignments may exist only as a sketched centerline digitized from a map. GIS
systems commonly store linear features as coordinate strings. IFC accommodates these cases
through two representation types: `IfcPolyline` and `IfcIndexedPolyCurve`.

Both are **discrete** rather than parametric: geometry is defined by a sequence of control
points with linear interpolation between them. The result is a
piecewise-linear approximation that encodes position only.

The IFC specification lists both types as valid `IfcAlignment` geometry for 2D horizontal
alignments (planning and mapping contexts) and 3D alignments (survey-derived). See
Section 1.5 for the complete list of valid representation types.

## 6.1 Geometric Forms

Both `IfcPolyline` and `IfcIndexedPolyCurve` provide simplified, approximate
representations of alignment geometry. Rather than encoding the mathematical intent of
the design — curve type, radius, spiral parameter — they encode only sampled positions.
The two types differ in storage layout and in how much approximation they can absorb.

**`IfcPolyline`** holds geometry as an ordered list of `IfcCartesianPoint` instances —
each vertex is a discrete entity in the model. Consecutive vertices are connected by
straight line segments, so every curve in the original alignment is approximated by a
series of chords. The curve accepts 2D or 3D coordinates, making it suitable for both
plan-view sketches and full survey point strings.

**`IfcIndexedPolyCurve`** stores coordinates compactly in an `IfcCartesianPointList2D` or
`IfcCartesianPointList3D` and references individual vertices by integer index. When the
optional `Segments` attribute is omitted, the result is functionally identical to `IfcPolyline`. 
When `Segments` is provided, each entry is either
an `IfcLineIndex` (two indices, straight segment) or an `IfcArcIndex` (three indices:
start, a through-point on the arc, and end). Arc segments allow circular curves to be
represented exactly rather than approximated by chords, reducing the number of vertices
needed for a given accuracy. This makes `IfcIndexedPolyCurve` better suited to
map-digitized or GIS-derived data where circular arcs are common but transition spirals
are absent.


## 6.2 Alignments Without Semantic Layout

In contrast to Concept Templates 4.1.7.1.1.1 through 4.1.7.1.1.4, the IFC specification
does not provide concept templates that show how `IfcPolyline` or `IfcIndexedPolyCurve`
provide a geometric representation of an `IfcAlignment`. (The same gap applies to
`IfcOffsetCurveByDistances`, covered in Chapter 5.)

Section 1.4 establishes that every `IfcAlignmentHorizontal`, `IfcAlignmentVertical`, and
`IfcAlignmentCant` must terminate with a zero-length `IfcAlignmentSegment`. When a
geometric representation accompanies the semantic definition, the corresponding last
`IfcCurveSegment` must also be zero length. 

Neither type is composed of `IfcCurveSegment` entities and therefore neither can satisfy
the requirements for the geometric counterpart to a full alignment layout.

While `IfcPolyline` and `IfcIndexedPolyCurve` could each serve as an
`IfcCurveSegment.ParentCurve`, they cannot produce the required zero-length closing
segment. A zero-length polyline segment requires two consecutive coincident vertices;
`IfcPolyline` WHERE rule WR1 explicitly prohibits this. `IfcIndexedPolyCurve` has no
equivalent schema-level prohibition, but a coincident point pair produces a degenerate
segment with an undefined tangent direction. This is unfortunate because an application needing detailed semantic information and only an approximate geometric representation is left with an unsupported use case.

For this reason, `IfcPolyline` and `IfcIndexedPolyCurve` (as well as `IfcOffsetCurveByDistances`) can only represent an
`IfcAlignment` without an accompanying semantic layout definition.
