# Author: Richard Brice, PE
# Date: 2026-10-13
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Same variable-width stringline surface geometry as the (now removed) resource-entity and
# placeholder-IfcAlignment examples, but rooted using the technique §10.5.1 and §10.5.2 identify
# as the one the working group actually intended: the three tagged IfcOffsetCurveByDistances guide
# curves are bare resource entities placed in a sibling "Axis"/GeometricCurveSet
# IfcShapeRepresentation alongside the surface's "Body" representation, within the same
# IfcPavement's IfcProductDefinitionShape (§10.6.1.4). This mirrors the wiring already used by
# Build_IfcSectionedSolidHorizontal_with_stringlines_shared_basiscurve.py for the solid
# counterpart (§10.6.2.5).

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


CROWN_SLOPE = 0.2   # 20 % cross-slope
WIDTH       = 30.   # m — nominal half-width

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

# Main alignment — 200 m straight, due East, flat grade.
start_station = 500.
alignment = ifcopenshell.api.alignment.create(file, "Main-Line", include_vertical=True)
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

# Define the stationing now that the horizontal layout has segments, so the starting
# referent is placed on the curve (ifcopenshell.api.alignment.create() no longer does this).
ifcopenshell.api.alignment.add_stationing_referent(
    file,
    name=ifcopenshell.util.alignment.station_as_string(file, start_station),
    alignment=alignment,
    distance_along=0.0,
    station=start_station,
)

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

# Guide curves — three bare IfcOffsetCurveByDistances resource entities, not wrapped in placeholder
# IfcAlignment instances. Rootedness (IFC105) is instead satisfied by placing all three curves in a
# sibling "Axis"/GeometricCurveSet IfcShapeRepresentation alongside the surface's "Body"
# representation, within the same IfcProductDefinitionShape — see §10.5.2 and §10.6.1.4. All three
# BasisCurves are the same basis_curve as the surface Directrix, so tags are scoped to that shared
# parameterization and to this IfcProductDefinitionShape (see §10.5.2).
#
# A: left edge  — widens from 30 m to 45 m at midpoint, returns.
# B: centerline — stays fixed at (0, 0) throughout.
# C: right edge — mirrors A on the right side.
offset_curve_a = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
], Tag="A")
offset_curve_b = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=0., OffsetVertical=0.),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=0., OffsetVertical=0.),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=0., OffsetVertical=0.),
], Tag="B")
offset_curve_c = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=[
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(0.),   OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(100.), OffsetLateral=-1.5*WIDTH, OffsetVertical=-1.5*WIDTH*CROWN_SLOPE),
    file.createIfcPointByDistanceExpression(BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(200.), OffsetLateral=-WIDTH,     OffsetVertical=-WIDTH*CROWN_SLOPE),
], Tag="C")

# Open cross-section — two segments (left shoulder to centerline, centerline to right shoulder),
# three tagged vertices matching the three guide curves above.
cs = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[WIDTH, WIDTH],
    Slopes=[make_angle(-CROWN_SLOPE), make_angle(CROWN_SLOPE)],
    Tags=["A", "B", "C"],
    OffsetPoint=file.createIfcCartesianPoint((WIDTH, -WIDTH*CROWN_SLOPE))
)

op1 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.),   BasisCurve=basis_curve))
op2 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.), BasisCurve=basis_curve))

surface = file.createIfcSectionedSurface(
    Directrix=basis_curve,
    CrossSectionPositions=[op1, op2],
    CrossSections=[cs, cs]
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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSurface_with_stringlines_shared_basiscurve.ifc")
file.write(output_path)
print("Done!")
