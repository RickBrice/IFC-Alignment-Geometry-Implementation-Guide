# Author: Richard Brice, PE
# Date: 2026-05-22
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Solid counterpart to Build_IfcSectionedSurface_with_stringlines_independent_edge_alignments.py.
# Demonstrates IfcSectionedSolidHorizontal where edge guide curves use independent IfcAlignment
# geometry (circular arcs) rather than parametric offsets from the centerline directrix. Main-Line
# is 200 m straight; Left_Edge and Right_Edge are 150 m circular arcs starting at ±30 m from the
# centerline. The open IfcOpenCrossProfileDef is replaced by IfcArbitraryClosedProfileDef with
# IfcCartesianPointList2D.TagList. Because A-line and C-line have BasisCurves independent of the
# solid Directrix, tags must be globally unique across the model. The same two specification gaps
# documented in §10.6.1.6 apply here. See §10.6.2.6 of the guide.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

CROWN_SLOPE = 0.2    # 20 % cross-slope (matches companion surface example)
WIDTH       = 30.    # m — nominal half-width
THICKNESS   = 1.0    # m — slab thickness

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid with Stringlines - Independent BasisCurve")
site    = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")

length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
angle  = ifcopenshell.api.unit.add_si_unit(file, unit_type="PLANEANGLEUNIT")
ifcopenshell.api.unit.assign_unit(file, units=[length, angle])

geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
body = ifcopenshell.api.context.add_context(
    file,
    context_type="Model",
    context_identifier="Body",
    target_view="MODEL_VIEW",
    parent=geometric_representation_context
)

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

# Main alignment — 200 m straight, due East, flat grade.
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

# Left_Edge — 150 m circular arc curving left (R = +300 m), starting 30 m north of Main-Line.
# Right_Edge — 150 m circular arc curving right (R = -300 m), starting 30 m south of Main-Line.
# Both use the same constant-grade vertical, identical to the companion surface example.
edge_vsegment = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=200.,
    StartHeight=-WIDTH * CROWN_SLOPE / 2,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)

left_alignment = ifcopenshell.api.alignment.create(file, "Left_Edge", include_vertical=True)
ifcopenshell.api.alignment.create_layout_segment(
    file, ifcopenshell.api.alignment.get_horizontal_layout(left_alignment),
    file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=(0., WIDTH)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.,
        EndRadiusOfCurvature=300.,
        SegmentLength=150.,
        PredefinedType="CIRCULARARC"
    )
)
ifcopenshell.api.alignment.create_layout_segment(
    file, ifcopenshell.api.alignment.get_vertical_layout(left_alignment), edge_vsegment
)

right_alignment = ifcopenshell.api.alignment.create(file, "Right_Edge", include_vertical=True)
ifcopenshell.api.alignment.create_layout_segment(
    file, ifcopenshell.api.alignment.get_horizontal_layout(right_alignment),
    file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=(0., -WIDTH)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.,
        EndRadiusOfCurvature=-300.,
        SegmentLength=150.,
        PredefinedType="CIRCULARARC"
    )
)
ifcopenshell.api.alignment.create_layout_segment(
    file, ifcopenshell.api.alignment.get_vertical_layout(right_alignment), edge_vsegment
)

basis_curve = ifcopenshell.api.alignment.get_curve(alignment)
left_curve  = ifcopenshell.api.alignment.get_curve(left_alignment)
right_curve = ifcopenshell.api.alignment.get_curve(right_alignment)
ifcopenshell.api.alignment.update_end_point(file, basis_curve)
ifcopenshell.api.alignment.update_end_point(file, left_curve)
ifcopenshell.api.alignment.update_end_point(file, right_curve)

road      = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(), Name="RoadPart1", UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])

# Guide curve alignments — zero-offset wrappers, same structure as the companion surface example.
# A-line follows Left_Edge (BasisCurve = left_curve, independent of basis_curve).
# B-line follows Main-Line (BasisCurve = basis_curve, same as solid Directrix).
# C-line follows Right_Edge (BasisCurve = right_curve, independent of basis_curve).
# Because A-line and C-line have independent BasisCurves, tags "A", "B", "C" must be
# globally unique across the model — basis-curve scoping does not apply (see §10.5).
alignment_a = ifcopenshell.api.alignment.create_as_offset_curve(file, name="A-line", offsets=[
    file.createIfcPointByDistanceExpression(BasisCurve=left_curve,  DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
])
alignment_b = ifcopenshell.api.alignment.create_as_offset_curve(file, name="B-line", offsets=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
])
alignment_c = ifcopenshell.api.alignment.create_as_offset_curve(file, name="C-line", offsets=[
    file.createIfcPointByDistanceExpression(BasisCurve=right_curve, DistanceAlong=file.createIfcLengthMeasure(0.), OffsetLateral=0., OffsetVertical=0.)
])

offset_curve_a = ifcopenshell.api.alignment.get_curve(alignment_a)
offset_curve_b = ifcopenshell.api.alignment.get_curve(alignment_b)
offset_curve_c = ifcopenshell.api.alignment.get_curve(alignment_c)

offset_curve_a.Tag = "A"
offset_curve_b.Tag = "B"
offset_curve_c.Tag = "C"


def make_profile(half_width):
    # Crown cross-section: 2×half_width wide, THICKNESS thick, 20% crown slope. CCW vertices.
    # Top-surface vertices tagged A, B, C; bottom-surface vertices tagged A_bot, B_bot, C_bot
    # (no matching guide curves — bottom linearly interpolates between cross-section positions).
    top_y = -half_width * CROWN_SLOPE
    bot_y = top_y - THICKNESS
    pt_list = file.createIfcCartesianPointList2D(
        CoordList=[
            (-half_width, bot_y),   # 1 bottom left   C_bot
            (0.,         -THICKNESS), # 2 bottom center B_bot
            (half_width,  bot_y),   # 3 bottom right  A_bot
            (half_width,  top_y),   # 4 top right     A
            (0.,          0.),       # 5 crown         B
            (-half_width, top_y),   # 6 top left      C
        ],
        TagList=["C_bot", "B_bot", "A_bot", "A", "B", "C"]
    )
    poly = file.createIfcIndexedPolyCurve(
        Points=pt_list,
        Segments=[file.createIfcLineIndex((1, 2, 3, 4, 5, 6, 1))]
    )
    return file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly)


# cs1: template at distance 0 m — nominal half-width ±30 m.
# cs2: template at distance 200 m — nominal half-width ±60 m.
# Left_Edge and Right_Edge are only 150 m long; their guide curves implicitly extend their final
# position to 200 m. The authored cs2 template (±60 m) and the extended guide curve positions
# may disagree at station 200 m — this is the specification gap documented in §10.6.1.6.
cs1 = make_profile(WIDTH)
cs2 = make_profile(2 * WIDTH)

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
product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSolidHorizontal_with_stringlines_independent_edge_alignments.ifc")
file.write(output_path)
print("Done!")
