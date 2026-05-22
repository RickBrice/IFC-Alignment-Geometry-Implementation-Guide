# Author: Richard Brice, PE
# Date: 2026-05-22
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Solid counterpart to Build_IfcSectionedSurface_with_stringlines_guide_curves_as_alignments.py.
# Demonstrates IfcSectionedSolidHorizontal with guide curves controlling tagged vertices of an
# IfcArbitraryClosedProfileDef. The same 200 m straight alignment, three offset-curve guide
# alignments (A-line, B-line, C-line), and variable-width parameters are used. Tags are assigned
# via IfcCartesianPointList2D.TagList on the three top-surface vertices of the closed profile;
# the three bottom-surface vertices are untagged and interpolate linearly between the two defined
# cross-section positions. See §10.6.2.5 of the guide.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

CROWN_SLOPE = 0.2    # 20 % cross-slope (matches companion surface example)
WIDTH       = 30.    # m — nominal half-width
THICKNESS   = 1.0    # m — slab thickness

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid with Stringlines")
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

# Guide curve alignments — identical offsets to the companion surface example.
# A-line: right shoulder top (tag "A") — widens from 30 m to 45 m at midpoint, returns.
# B-line: crown (tag "B")              — stays fixed at (0, 0) throughout.
# C-line: left shoulder top (tag "C")  — mirrors A-line on the left side.
# All three BasisCurves are the same basis_curve as the solid Directrix, so tags are
# scoped to that shared parameterization (see §10.5).
alignment_a = ifcopenshell.api.alignment.create_as_offset_curve(file, name="A-line", offsets=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
])
alignment_b = ifcopenshell.api.alignment.create_as_offset_curve(file, name="B-line", offsets=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=0., OffsetVertical=0.),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=0., OffsetVertical=0.),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=0., OffsetVertical=0.),
])
alignment_c = ifcopenshell.api.alignment.create_as_offset_curve(file, name="C-line", offsets=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=-1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
])

offset_curve_a = ifcopenshell.api.alignment.get_curve(alignment_a)
offset_curve_b = ifcopenshell.api.alignment.get_curve(alignment_b)
offset_curve_c = ifcopenshell.api.alignment.get_curve(alignment_c)

offset_curve_a.Tag = "A"
offset_curve_b.Tag = "B"
offset_curve_c.Tag = "C"

# Closed crown cross-section profile — V-shaped slab, nominal width 60 m, 1 m thick.
# Top-surface vertices carry TagList labels matching the guide curve tags.
# Bottom-surface vertices are untagged (None) and interpolate linearly between the
# two cross-section positions; they do not follow the guide curves.
#
# Template profile (before guide curves take effect):
#
#   C(-30,-6) ___________ B(0,0) ___________ A(30,-6)   ← top surface (20 % crown)
#            /                                \
#   (-30,-7)              (0,-1)              (30,-7)    ← soffit (1 m below top)
#
# Vertices wound counterclockwise.
point_list = file.createIfcCartesianPointList2D(
    CoordList=[
        (-WIDTH, -WIDTH*CROWN_SLOPE - THICKNESS),  # 1  bottom left   (untagged)
        (0.,    -THICKNESS),                        # 2  bottom center (untagged)
        (WIDTH,  -WIDTH*CROWN_SLOPE - THICKNESS),  # 3  bottom right  (untagged)
        (WIDTH,  -WIDTH*CROWN_SLOPE),              # 4  top right     → "A"
        (0.,     0.),                               # 5  crown         → "B"
        (-WIDTH, -WIDTH*CROWN_SLOPE),              # 6  top left      → "C"
    ],
    TagList=["C_bot", "B_bot", "A_bot", "A", "B", "C"]
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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSolidHorizontal_with_stringlines_guide_curves_as_alignments.ifc")
file.write(output_path)
print("Done!")
