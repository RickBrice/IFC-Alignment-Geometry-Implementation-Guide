# Author: Richard Brice, PE
# Date: 2026-05-22
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Solid counterpart to Build_IfcSectionedSurface_with_stringlines_guide_curves_as_alignments.py,
# but demonstrates a DIFFERENT rooted-entity technique for comparison: rather than wrapping each
# guide curve in a placeholder IfcAlignment (the surface example's approach, §10.6.1.5), the six
# guide curves here are bare IfcOffsetCurveByDistances entities placed in a sibling "Axis"
# IfcShapeRepresentation alongside the solid's "Body" representation, within the same
# IfcProductDefinitionShape as the IfcPavement that hosts them (§10.5.7, §10.6.2.5). The same
# 200 m straight alignment and variable-width parameters are used as the surface example, but this
# solid extends guide curve control to all six profile vertices, not just the top three: the top
# curves (A_top, B_top, C_top) match the surface example's A/B/C offsets, and the soffit curves
# (A_bot, B_bot, C_bot) mirror them 1 m lower to hold the slab thickness constant. Tags are
# assigned via IfcCartesianPointList2D.TagList on all six vertices of the closed profile.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

CROWN_SLOPE = 0.2    # 20 % cross-slope (matches companion surface example)
WIDTH       = 30.    # m — nominal half-width
THICKNESS   = 1.0    # m — slab thickness

file = ifcopenshell.file(schema="IFC4X3_ADD2")
# ViewDefinition is NotAssigned because IfcOffsetCurveByDistances (used as a stringline guide
# curve) is not part of any standardized MVD schema subset or implementation level.
file.header.file_description.description = ("ViewDefinition [NotAssigned]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid with Stringlines")
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

# Main alignment — 200 m straight, due East, flat grade. Identical to the companion surface example.
start_station = 500.
alignment = ifcopenshell.api.alignment.create(file, "Main-Line", include_vertical=True, start_station=start_station)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=200.,
    PredefinedType="LINE"
)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=200.,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

basis_curve = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, basis_curve)

road      = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(), Name="RoadPart1", UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])

# Guide curves — six total, authored as bare IfcOffsetCurveByDistances resource entities rather
# than wrapped in placeholder IfcAlignment instances. Rootedness (IFC105) is instead satisfied by
# placing all six curves in a sibling "Axis"/GeometricCurveSet IfcShapeRepresentation alongside the
# solid's "Body" representation, within the same IfcProductDefinitionShape — see §10.5.7 and
# §10.6.2.5. All six BasisCurves are the same basis_curve as the solid Directrix, so tags are
# scoped to that shared parameterization (see §10.5.1).
#
# Top surface (matches the surface example's A/B/C offsets exactly):
# A_top-line: right shoulder top — widens from 30 m to 45 m at midpoint, returns.
# B_top-line: crown              — stays fixed at (0, 0) throughout.
# C_top-line: left shoulder top  — mirrors A_top-line on the left side.
#
# Soffit (mirrors the top curves 1 m lower, holding the slab thickness constant):
# A_bot-line, B_bot-line, C_bot-line — same lateral path as A_top/B_top/C_top, OffsetVertical
# shifted down by THICKNESS.
offset_curve_a_top = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
], Tag="A_top")
offset_curve_b_top = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=0., OffsetVertical=0.),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=0., OffsetVertical=0.),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=0., OffsetVertical=0.),
], Tag="B_top")
offset_curve_c_top = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=-1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
], Tag="C_top")

offset_curve_a_bot = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE - THICKNESS),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE - THICKNESS),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE - THICKNESS),
], Tag="A_bot")
offset_curve_b_bot = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=0., OffsetVertical=-THICKNESS),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=0., OffsetVertical=-THICKNESS),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=0., OffsetVertical=-THICKNESS),
], Tag="B_bot")
offset_curve_c_bot = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE - THICKNESS),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=-1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE - THICKNESS),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE - THICKNESS),
], Tag="C_bot")

# Closed crown cross-section profile — V-shaped slab, nominal width 60 m, 1 m thick.
# All six vertices carry TagList labels matching one of the six guide curves above; the soffit
# vertices are guided the same as the top ones, just 1 m lower.
#
# Template profile (before guide curves take effect):
#
#   C_top(-30,-6) _______ B_top(0,0) _______ A_top(30,-6)   ← top surface (20 % crown)
#              /                                  \
#   C_bot(-30,-7)        B_bot(0,-1)        A_bot(30,-7)    ← soffit (1 m below top)
#
# Vertices wound counterclockwise.
point_list = file.createIfcCartesianPointList2D(
    CoordList=[
        (-WIDTH, -WIDTH*CROWN_SLOPE - THICKNESS),  # 1  bottom left   → "C_bot"
        (0.,    -THICKNESS),                        # 2  bottom center → "B_bot"
        (WIDTH,  -WIDTH*CROWN_SLOPE - THICKNESS),  # 3  bottom right  → "A_bot"
        (WIDTH,  -WIDTH*CROWN_SLOPE),              # 4  top right     → "A_top"
        (0.,     0.),                               # 5  crown         → "B_top"
        (-WIDTH, -WIDTH*CROWN_SLOPE),              # 6  top left      → "C_top"
    ],
    TagList=["C_bot", "B_bot", "A_bot", "A_top", "B_top", "C_top"]
)
poly_curve = file.createIfcIndexedPolyCurve(
    Points=point_list,
    Segments=[file.createIfcLineIndex((1, 2, 3, 4, 5, 6, 1))]
)
cs = file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)

op1 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.),   BasisCurve=basis_curve))
op2 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.), BasisCurve=basis_curve))

solid = file.createIfcSectionedSolidHorizontal(
    Directrix=basis_curve,
    CrossSections=[cs, cs],
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
    Items=[offset_curve_a_top, offset_curve_b_top, offset_curve_c_top,
           offset_curve_a_bot, offset_curve_b_bot, offset_curve_c_bot]
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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSolidHorizontal_with_stringlines_guide_curves_as_alignments.ifc")
file.write(output_path)
print("Done!")
