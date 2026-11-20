# Author: Richard Brice, PE
# Date: 2026-10-13
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcSectionedSurface where edge stringlines are defined from independent curve
# geometry (circular arcs) rather than as parametric offsets from the centerline. The surface
# width varies because the edge curves curve at a different radius than the main line.
#
# The edge curves (left/right) are built directly as bare IfcCompositeCurve/IfcGradientCurve
# entities via build_edge_curve() — there is no IfcAlignment, IfcAlignmentHorizontal/Vertical,
# IfcAlignmentSegment, or IfcRelNests/IfcRelAggregates for them at all. IfcCurveSegment.ParentCurve
# references a bare IfcCircle/IfcLine directly, with no dependency on the semantic alignment layer
# (see chapter 1's discussion of semantic vs. geometric alignment representation), and the "A"/"C"
# guide curves that reference these curves as BasisCurve are already rooted through the sibling
# "Axis" IfcShapeRepresentation construction (§10.5.2) — no host product is needed for the edge
# geometry itself. This was tested (an earlier, throwaway script built the edges as full
# IfcAlignment products, then confirmed the same geometry could be built bare) and the resulting
# model was confirmed to pass the bSI validation service with no IFC105 violation.
#
# The edge curves must pass through the point exactly ±END_WIDTH from Main-Line's own endpoint
# (200 m forward), not merely be at least as long as the surface directrix: an earlier revision of
# this example gave them a 150 m arc length, short of the surface's own extent, and a later
# revision made the mistake of setting arc length equal to forward distance (200 m) directly,
# which still lands short since a curving path always covers more distance than its own forward
# progress. Both are authoring defects of the same kind as the coordinate/guide-curve disagreement
# discussed in §10.5.3, not something the specification permits or resolves. solve_arc_radius()
# computes the radius that makes the circle pass through that point; ARC_LENGTH is then set to
# 205 m, deliberately a bit longer than the ~201.3 m strictly needed to reach it — a guide curve is
# permitted to run past what's required (§10.5.5), only falling short is a defect.

import os
import math
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.util.alignment
import ifcopenshell.api.unit


def make_angle(slope):
    # from Fig 8.15.3.15.A, X is towards the left, Y is up, and angle is positive CW from +X.
    # this function converts tranditional engineering slopes to angular measure for use in IfcOpenCrossProfileDef
    return math.pi + math.atan(slope)


def solve_arc_radius(forward_distance, offset_growth):
    # Solves for the radius R of a circular arc that starts tangent-parallel to a straight
    # reference line and, `forward_distance` further along that line's direction, has drifted
    # `offset_growth` further from it. This radius is a fixed property of that single point on
    # the circle — it does not depend on how much further the arc is actually drawn beyond it, so
    # a guide curve's arc length may exceed the minimum needed to reach that point (see §10.5.5:
    # only a guide curve that is too *short* is an authoring defect).
    #
    # With phi = S/R at the point in question, that point is at
    # (R sin(phi), offset_growth-so-far + R(1-cos(phi))). Requiring the X component to equal
    # forward_distance and the Y component's growth to equal offset_growth gives, via the
    # half-angle identity (1-cos(phi))/sin(phi) = tan(phi/2):
    #     tan(phi/2) = offset_growth / forward_distance
    #     R = (forward_distance**2 + offset_growth**2) / (2 * offset_growth)
    return (forward_distance**2 + offset_growth**2) / (2 * offset_growth)


def build_edge_curve(file, y0, radius, signed_arc_length, start_height):
    """
    Builds a bare IfcGradientCurve for a circular arc starting tangent-parallel to the X axis at
    (0, y0), curving over `signed_arc_length` at `radius` (always positive; the SIGN of
    signed_arc_length — not the sign of radius — determines whether the path curves left
    (positive) or right (negative)), with a constant-height vertical profile at `start_height`.
    No IfcAlignment, layout, or segment entities are created — only the geometry itself, matching
    exactly what ifcopenshell.api.alignment produces for a horizontal CIRCULARARC + vertical
    CONSTANTGRADIENT pair (verified against that construction's own generated STEP entities).
    """
    L = abs(signed_arc_length)
    direction_sign = 1.0 if signed_arc_length >= 0 else -1.0
    phi = L / radius
    x_end = radius * math.sin(phi)
    y_end = y0 + direction_sign * radius * (1 - math.cos(phi))
    tangent_end = (math.cos(phi), direction_sign * math.sin(phi))

    def flat_local_line():
        return file.createIfcLine(
            Pnt=file.createIfcCartesianPoint((0., 0.)),
            Dir=file.createIfcVector(Orientation=file.createIfcDirection((1., 0.)), Magnitude=1.)
        )

    def placement(location, direction):
        return file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint(location),
            RefDirection=file.createIfcDirection(direction)
        )

    circle = file.createIfcCircle(Position=placement((0., 0.), (1., 0.)), Radius=radius)

    arc_segment = file.createIfcCurveSegment(
        Transition="CONTSAMEGRADIENT",
        Placement=placement((0., y0), (1., 0.)),
        SegmentStart=file.createIfcLengthMeasure(0.),
        SegmentLength=file.createIfcLengthMeasure(signed_arc_length),
        ParentCurve=circle
    )
    horizontal_terminator = file.createIfcCurveSegment(
        Transition="DISCONTINUOUS",
        Placement=placement((x_end, y_end), tangent_end),
        SegmentStart=file.createIfcLengthMeasure(0.),
        SegmentLength=file.createIfcLengthMeasure(0.),
        ParentCurve=flat_local_line()
    )
    composite_curve = file.createIfcCompositeCurve(Segments=[arc_segment, horizontal_terminator], SelfIntersect=False)

    vertical_segment = file.createIfcCurveSegment(
        Transition="CONTSAMEGRADIENTSAMECURVATURE",
        Placement=placement((0., start_height), (1., 0.)),
        SegmentStart=file.createIfcLengthMeasure(0.),
        SegmentLength=file.createIfcLengthMeasure(L),
        ParentCurve=flat_local_line()
    )
    vertical_terminator = file.createIfcCurveSegment(
        Transition="DISCONTINUOUS",
        Placement=placement((L, start_height), (1., 0.)),
        SegmentStart=file.createIfcLengthMeasure(0.),
        SegmentLength=file.createIfcLengthMeasure(0.),
        ParentCurve=flat_local_line()
    )
    return file.createIfcGradientCurve(
        Segments=[vertical_segment, vertical_terminator],
        SelfIntersect=False,
        BaseCurve=composite_curve,
        EndPoint=placement((L, start_height), (1., 0.))
    )


file = ifcopenshell.file(schema="IFC4X3_ADD2")
# ViewDefinition is NotAssigned because IfcOffsetCurveByDistances (used as a stringline guide
# curve) is not part of any standardized MVD schema subset or implementation level.
file.header.file_description.description = ("ViewDefinition [NotAssigned]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Surface with Stringlines")
site    = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")

length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
angle  = ifcopenshell.api.unit.add_si_unit(file, unit_type="PLANEANGLEUNIT")
ifcopenshell.api.unit.assign_unit(file, units=[length, angle])

geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
    file,
    context_type="Model",
    context_identifier="Axis",
    target_view="MODEL_VIEW",
    parent=geometric_representation_context,
)
body = ifcopenshell.api.context.add_context(
    file,
    context_type="Model",
    context_identifier="Body",
    target_view="MODEL_VIEW",
    parent=geometric_representation_context,
)

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

CROWNSLOPE  = 0.2
WIDTH       = 30.    # m — half-width at the near cross-section (station 0)
END_WIDTH   = 50.    # m — half-width at the far cross-section (station 200)
ARC_LENGTH  = 205.   # m — deliberately longer than the ~201.3 m strictly needed to reach the far
                     # cross-section; a guide curve is allowed to run past what's required (§10.5.5)
EDGE_RADIUS = solve_arc_radius(200., END_WIDTH - WIDTH)

# Main-Line remains a real IfcAlignment product — it is the surface's actual Directrix and isn't
# part of what this example is demonstrating.
start_station = 500.
alignment = ifcopenshell.api.alignment.create(file, "Main-Line", include_vertical=True)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=200.,
    PredefinedType="LINE"
)

layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

# Define the stationing now that the horizontal layout has segments, so the starting
# referent is placed on the curve (ifcopenshell.api.alignment.create() no longer does this).
ifcopenshell.api.alignment.add_stationing_referent(
    file,
    name=ifcopenshell.util.alignment.station_as_string(file, start_station),
    alignment=alignment,
    distance_along=0.0,
    station=start_station,
)

vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=200.,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

basis_curve = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, basis_curve)

road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])

road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(), Name="RoadPart1", UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])

# Left/right edge geometry — bare IfcGradientCurve entities, never wrapped in an IfcAlignment
# product, never aggregated anywhere. Referenced ONLY as BasisCurve of the "A"/"C" guide curves.
left_curve  = build_edge_curve(file, y0=WIDTH,  radius=EDGE_RADIUS, signed_arc_length=ARC_LENGTH,  start_height=-WIDTH*CROWNSLOPE/2)
right_curve = build_edge_curve(file, y0=-WIDTH, radius=EDGE_RADIUS, signed_arc_length=-ARC_LENGTH, start_height=-WIDTH*CROWNSLOPE/2)

# Guide curves — three bare IfcOffsetCurveByDistances resource entities. Rootedness (IFC105) and
# tag scoping are satisfied by placing all three curves in a sibling "Axis"/GeometricCurveSet
# IfcShapeRepresentation alongside the surface's "Body" representation, within the same
# IfcProductDefinitionShape — see §10.5.2 and §10.6.1.4. "A" and "C" are zero-offset from the
# independent left/right edge curves built above (their own BasisCurve differs from the surface
# Directrix — see §10.5.2 for the tag-scoping consequence); "B" is a zero-offset from Main-Line.
offset_curve_a = file.createIfcOffsetCurveByDistances(BasisCurve=left_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=left_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
], Tag="A")
offset_curve_b = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
], Tag="B")
offset_curve_c = file.createIfcOffsetCurveByDistances(BasisCurve=right_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=right_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
], Tag="C")

cs1 = file.createIfcOpenCrossProfileDef(
        ProfileType="CURVE",
        HorizontalWidths=True,
        Widths=[WIDTH, WIDTH],
        Slopes=[make_angle(-CROWNSLOPE), make_angle(CROWNSLOPE)],
        Tags=["A", "B", "C"],
        OffsetPoint=file.createIfcCartesianPoint((WIDTH, -WIDTH*CROWNSLOPE))
    )

cs2 = file.createIfcOpenCrossProfileDef(
        ProfileType="CURVE",
        HorizontalWidths=True,
        Widths=[END_WIDTH, END_WIDTH],
        Slopes=[make_angle(-CROWNSLOPE), make_angle(CROWNSLOPE)],
        Tags=["A", "B", "C"],
        OffsetPoint=file.createIfcCartesianPoint((END_WIDTH, -END_WIDTH*CROWNSLOPE))
    )

op1 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.),   BasisCurve=basis_curve))
op2 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.), BasisCurve=basis_curve))

surface = file.createIfcSectionedSurface(
    Directrix=basis_curve,
    CrossSectionPositions=[op1, op2],
    CrossSections=[cs1, cs2]
)

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="SectionedSurface", Items=[surface])
axis_representation = file.createIfcShapeRepresentation(
    ContextOfItems=axis_model_representation_subcontext,
    RepresentationIdentifier="Axis",
    RepresentationType="GeometricCurveSet",
    Items=[offset_curve_a, offset_curve_b, offset_curve_c]
)

product_rep = file.createIfcProductDefinitionShape(Representations=[representation, axis_representation])

pavement = file.createIfcPavement(GlobalId=ifcopenshell.guid.new(), Name="Pavement",
        ObjectPlacement=file.createIfcLocalPlacement(
            RelativePlacement=file.createIfcAxis2Placement3D(
                Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0, 0.0))
            )
        ),
        Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=road_part, products=[pavement])

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSurface_with_stringlines_independent_guide_curves.ifc")
file.write(output_path)
print("Done!")
print(f"EDGE_RADIUS = {EDGE_RADIUS:.4f} m, ARC_LENGTH = {ARC_LENGTH:.4f} m")
print(f"IfcAlignment count: {len(file.by_type('IfcAlignment'))} (Main-Line only)")
