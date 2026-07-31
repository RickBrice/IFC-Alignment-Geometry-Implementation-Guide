# Author: Richard Brice, PE
# Date: 2026-05-22 (revised 2026-07-31)
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Solid counterpart to Build_IfcSectionedSurface_with_stringlines_independent_guide_curves.py.
# Demonstrates IfcSectionedSolidHorizontal where edge guide curves use independent curve geometry
# (circular arcs) rather than parametric offsets from the centerline directrix. Main-Line is
# 200 m straight; the left/right edge curves are built directly as bare IfcCompositeCurve/
# IfcGradientCurve entities via build_edge_curve() — there is no IfcAlignment,
# IfcAlignmentHorizontal/Vertical, IfcAlignmentSegment, or IfcRelNests/IfcRelAggregates for them at
# all. This mirrors the surface example exactly: the edge geometry is referenced only as
# BasisCurve of the A_top/C_top guide curves, which are themselves already rooted through the
# sibling "Axis" IfcShapeRepresentation construction (§10.5.2) — confirmed against the bSI
# validation service with no IFC105 violation.
#
# The edge curves must pass through the point exactly ±END_WIDTH from Main-Line's own endpoint
# (200 m forward) — see the surface script for the derivation of solve_arc_radius() and the
# authoring-defect discussion (§10.5.3, §10.5.5) of getting this wrong. ARC_LENGTH is 205 m,
# matching the surface example.
#
# The open IfcOpenCrossProfileDef is replaced by IfcArbitraryClosedProfileDef with
# IfcCartesianPointList2D.TagList. Although A_top/C_top's guide curves have a BasisCurve
# independent of the solid Directrix, this has no effect on tag scoping: all six guide curves are
# hosted in the same sibling "Axis" representation as the solid, so scoping is governed by that
# shared IfcProductDefinitionShape (§10.5.2) regardless of BasisCurve.

import os
import math
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit


def solve_arc_radius(forward_distance, offset_growth):
    # See Build_IfcSectionedSurface_with_stringlines_independent_guide_curves.py for derivation.
    return (forward_distance**2 + offset_growth**2) / (2 * offset_growth)


def build_edge_curve(file, y0, radius, signed_arc_length, start_height):
    # See Build_IfcSectionedSurface_with_stringlines_independent_guide_curves.py for the full
    # derivation and verification of this construction against ifcopenshell.api.alignment's own
    # generated STEP entities.
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


CROWN_SLOPE = 0.2    # 20 % cross-slope (matches companion surface example)
WIDTH       = 30.    # m — nominal half-width at the near cross-section (station 0)
END_WIDTH   = 50.    # m — half-width at the far cross-section (station 200)
ARC_LENGTH  = 205.   # m — deliberately longer than the ~201.3 m strictly needed (§10.5.5)
THICKNESS   = 1.0    # m — slab thickness
EDGE_RADIUS = solve_arc_radius(200., END_WIDTH - WIDTH)

file = ifcopenshell.file(schema="IFC4X3_ADD2")
# ViewDefinition is NotAssigned because IfcOffsetCurveByDistances (used as a stringline guide
# curve) is not part of any standardized MVD schema subset or implementation level.
file.header.file_description.description = ("ViewDefinition [NotAssigned]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid with Stringlines - Independent BasisCurve")
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
    parent=geometric_representation_context
)

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

# Main alignment — 200 m straight, due East, flat grade. This remains a real IfcAlignment product
# — it is the solid's actual Directrix and isn't part of what this example is demonstrating.
start_station = 500.
alignment = ifcopenshell.api.alignment.create(file, "Main-Line", include_vertical=True, start_station=start_station)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, layout,
    file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=200.,
        PredefinedType="LINE"
    )
)
vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout,
    file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.,
        HorizontalLength=200.,
        StartHeight=0.,
        StartGradient=0.,
        EndGradient=0.,
        PredefinedType="CONSTANTGRADIENT"
    )
)

basis_curve = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, basis_curve)

road      = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(), Name="RoadPart1", UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])

# Left/right edge geometry — bare IfcGradientCurve entities, never wrapped in an IfcAlignment
# product, never aggregated anywhere. Referenced ONLY as BasisCurve of the A_top/C_top guide
# curves below.
left_curve  = build_edge_curve(file, y0=WIDTH,  radius=EDGE_RADIUS, signed_arc_length=ARC_LENGTH,  start_height=-WIDTH*CROWN_SLOPE/2)
right_curve = build_edge_curve(file, y0=-WIDTH, radius=EDGE_RADIUS, signed_arc_length=-ARC_LENGTH, start_height=-WIDTH*CROWN_SLOPE/2)

# Guide curves — bare IfcOffsetCurveByDistances entities, same structure as the companion surface
# example. Only the top vertices are guided; the soffit falls back to linear interpolation.
# A_top-line follows the left edge curve (BasisCurve = left_curve, independent of basis_curve).
# B_top-line follows Main-Line (BasisCurve = basis_curve, same as solid Directrix).
# C_top-line follows the right edge curve (BasisCurve = right_curve, independent of basis_curve).
offset_curve_a_top = file.createIfcOffsetCurveByDistances(BasisCurve=left_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=left_curve,  DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
], Tag="A_top")
offset_curve_b_top = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
], Tag="B_top")
offset_curve_c_top = file.createIfcOffsetCurveByDistances(BasisCurve=right_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=right_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
], Tag="C_top")


def make_profile(half_width):
    # Crown cross-section: 2×half_width wide, THICKNESS thick, 20% crown slope. CCW vertices.
    # Top-surface vertices tagged A_top, B_top, C_top; bottom-surface vertices tagged A_bot, B_bot,
    # C_bot (no matching guide curves — bottom linearly interpolates between cross-section positions).
    # Profile X is positive to the left of the directrix (§10.3.3), so A_top/A_bot (+half_width)
    # are on the left and C_top/C_bot (-half_width) are on the right.
    top_y = -half_width * CROWN_SLOPE
    bot_y = top_y - THICKNESS
    pt_list = file.createIfcCartesianPointList2D(
        CoordList=[
            (-half_width, bot_y),   # 1 bottom right  C_bot
            (0.,         -THICKNESS), # 2 bottom center B_bot
            (half_width,  bot_y),   # 3 bottom left   A_bot
            (half_width,  top_y),   # 4 top left      A_top
            (0.,          0.),       # 5 crown         B_top
            (-half_width, top_y),   # 6 top right     C_top
        ],
        TagList=["C_bot", "B_bot", "A_bot", "A_top", "B_top", "C_top"]
    )
    poly = file.createIfcIndexedPolyCurve(
        Points=pt_list,
        Segments=[file.createIfcLineIndex((1, 2, 3, 4, 5, 6, 1))]
    )
    return file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly)


# cs1: template at distance 0 m — nominal half-width ±30 m.
# cs2: template at distance 200 m — nominal half-width ±50 m, matching where the edge curves
# actually land (see solve_arc_radius / build_edge_curve above).
cs1 = make_profile(WIDTH)
cs2 = make_profile(END_WIDTH)

op1 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.),   BasisCurve=basis_curve))
op2 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.), BasisCurve=basis_curve))

solid = file.createIfcSectionedSolidHorizontal(
    Directrix=basis_curve,
    CrossSections=[cs1, cs2],
    CrossSectionPositions=[op1, op2]
)

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body,
    RepresentationIdentifier="Body",
    RepresentationType="SolidModel",
    Items=[solid]
)
axis_representation = file.createIfcShapeRepresentation(
    ContextOfItems=axis_model_representation_subcontext,
    RepresentationIdentifier="Axis",
    RepresentationType="GeometricCurveSet",
    Items=[offset_curve_a_top, offset_curve_b_top, offset_curve_c_top]
)
product_rep = file.createIfcProductDefinitionShape(Representations=[representation, axis_representation])

pavement = file.createIfcPavement(
    GlobalId=ifcopenshell.guid.new(),
    Name="Pavement",
    ObjectPlacement=file.createIfcLocalPlacement(
        RelativePlacement=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint(Coordinates=(0., 0., 0.))
        )
    ),
    Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=road_part, products=[pavement])

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSolidHorizontal_with_stringlines_independent_guide_curves.ifc")
file.write(output_path)
print("Done!")
print(f"EDGE_RADIUS = {EDGE_RADIUS:.4f} m, ARC_LENGTH = {ARC_LENGTH:.4f} m")
print(f"IfcAlignment count: {len(file.by_type('IfcAlignment'))} (Main-Line only)")
