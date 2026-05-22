# Author: Richard Brice, PE
# Date: 2026-05-22
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcSectionedSolidHorizontal with a crowned pavement cross-section swept along a
# three-segment highway alignment (tangent–arc–tangent). Six distinct IfcArbitraryClosedProfileDef
# instances — one per cross-section position — directly encode the cross-slope geometry at each
# station. The left and right shoulders vary independently, matching the superelevation progression
# of Build_IfcSectionedSurface_Superelevation.py: normal crown → adverse crown → full
# superelevation → full superelevation → adverse crown → normal crown. No rotation operators,
# tags, or guide curves are used. See §10.6.2.2 of the guide.

import math
import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit
import ifcopenshell.util.unit

CROWN_SLOPE = 0.02   # 2 % normal cross-slope (rise/run)
SUPER_SLOPE = 0.06   # 6 % full superelevation (rise/run)
HALF_WIDTH  = 30.0   # m — half-width of pavement
THICKNESS   = 0.5    # m — slab thickness

scripts_dir  = os.path.dirname(os.path.abspath(__file__))
examples_dir = os.path.join(scripts_dir, "..")

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(
    GlobalId=ifcopenshell.guid.new(),
    Name="Sectioned Solid Horizontal - Crown Superelevation"
)
site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")

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

# Alignment — tangent + circular arc + tangent (metric equivalent of the alignment in
# Build_IfcSectionedSurface_Superelevation.py). Cross-sections 1–2 land in the leading
# tangent, 3–4 in the arc, and 5–6 in the trailing tangent.
start_station = 3000.
alignment = ifcopenshell.api.alignment.create(
    file, "A-Line",
    include_vertical=True,
    start_station=start_station
)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(500., 2500.)),
    StartDirection=math.radians(327.0613),
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=600.,
    PredefinedType="LINE"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
x  = float(end[0, 3]) / unit_scale
y  = float(end[1, 3]) / unit_scale
dx = float(end[0, 0])
dy = float(end[1, 0])
segment2 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((x, y)),
    StartDirection=math.atan2(dy, dx),
    StartRadiusOfCurvature=300.,
    EndRadiusOfCurvature=300.,
    SegmentLength=585.,
    PredefinedType="CIRCULARARC"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment2)

x  = float(end[0, 3]) / unit_scale
y  = float(end[1, 3]) / unit_scale
dx = float(end[0, 0])
dy = float(end[1, 0])
segment3 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((x, y)),
    StartDirection=math.atan2(dy, dx),
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=600.,
    PredefinedType="LINE"
)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment3)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=1800.,
    StartHeight=30.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

directrix = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, directrix)

# Spatial hierarchy.
road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])
road_part = file.createIfcRoadPart(
    GlobalId=ifcopenshell.guid.new(),
    Name="RoadPart1",
    UsageType="LONGITUDINAL"
)
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])


def make_position(dist):
    return file.createIfcAxis2PlacementLinear(
        Location=file.createIfcPointByDistanceExpression(
            DistanceAlong=file.createIfcLengthMeasure(dist),
            BasisCurve=directrix
        )
    )


def make_profile(slope_right, slope_left):
    # Crown cross-section: 60 m wide, 0.5 m thick, no bevels.
    # Profile origin (0, 0) is the crown — the top of the section at the centerline.
    #
    # slope_right: signed fraction (rise/run) at the right shoulder, measured from the crown.
    #              Negative = right shoulder is below the crown.
    # slope_left:  signed fraction (rise/run) at the left shoulder, measured from the crown.
    #              Positive = left shoulder is above the crown.
    #
    # The soffit is offset 0.5 m vertically below each top-surface point.
    # Vertices are wound counterclockwise.
    #
    right_y = HALF_WIDTH * slope_right
    left_y  = HALF_WIDTH * slope_left
    point_list = file.createIfcCartesianPointList2D(
        CoordList=[
            (-HALF_WIDTH, left_y  - THICKNESS),  # 1  bottom left
            (0.,         -THICKNESS),              # 2  bottom center
            (HALF_WIDTH,  right_y - THICKNESS),  # 3  bottom right
            (HALF_WIDTH,  right_y),               # 4  top right shoulder
            (0.,          0.),                     # 5  crown
            (-HALF_WIDTH, left_y),                # 6  top left shoulder
        ]
    )
    poly_curve = file.createIfcIndexedPolyCurve(
        Points=point_list,
        Segments=[file.createIfcLineIndex((1, 2, 3, 4, 5, 6, 1))]
    )
    return file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)


# Six cross-section definitions — (distance from directrix start, slope_right, slope_left).
# Slopes are signed fractions (rise/run) measured from the crown (0, 0): negative = below,
# positive = above. Left and right shoulders vary independently, mirroring the six
# IfcOpenCrossProfileDef instances in Build_IfcSectionedSurface_Superelevation.py.
# Sections 1–2 lie in the leading tangent, 3–4 in the 300 m arc, 5–6 in the trailing tangent.
#
#  dist (m)   slope_right   slope_left   state
#  --------   -----------   ----------   ------------------------------------
#     540       -0.02         -0.02      normal crown
#     580       -0.02         +0.02      adverse crown — transition begins
#     615       -0.06         +0.06      full superelevation begins
#    1163       -0.06         +0.06      full superelevation ends
#    1199       -0.02         +0.02      adverse crown — returning to crown
#    1240       -0.02         -0.02      normal crown restored
#
CS_DEFS = [
    (540.,  -CROWN_SLOPE, -CROWN_SLOPE),
    (580.,  -CROWN_SLOPE, +CROWN_SLOPE),
    (615.,  -SUPER_SLOPE, +SUPER_SLOPE),
    (1163., -SUPER_SLOPE, +SUPER_SLOPE),
    (1199., -CROWN_SLOPE, +CROWN_SLOPE),
    (1240., -CROWN_SLOPE, -CROWN_SLOPE),
]

positions = [make_position(dist)              for dist, _,       _        in CS_DEFS]
profiles  = [make_profile(slope_r, slope_l)   for _,    slope_r, slope_l  in CS_DEFS]

solid = file.createIfcSectionedSolidHorizontal(
    Directrix=directrix,
    CrossSections=profiles,
    CrossSectionPositions=positions
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

output_path = os.path.join(examples_dir, "IfcSectionedSolidHorizontal_Superelevation.ifc")
file.write(output_path)
print("Done!")
