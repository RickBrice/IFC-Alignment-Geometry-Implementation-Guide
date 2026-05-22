# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates a complete highway superelevation transition — normal crown, runoff, full
# superelevation, and return — using IfcReferent superelevation events paired with
# IfcOpenCrossProfileDef cross-sections and an IfcSectionedSurface.

import os
import math
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit


def add_superelevation(file, name, alignment, station, start_station, side, slope):
    curve = ifcopenshell.api.alignment.get_curve(alignment)
    referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=name + " (" + ifcopenshell.util.alignment.station_as_string(file, station) + ")",
        Description=None,
        ObjectType=None,
        ObjectPlacement=file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(station - start_station),
                    BasisCurve=curve
                )
            )
        ),
        Representation=None,
        PredefinedType="SUPERELEVATIONEVENT",
    )
    ifcopenshell.api.alignment.update_fallback_position(file, referent.ObjectPlacement)

    pset_superelevation = ifcopenshell.api.pset.add_pset(file, product=referent, name="Pset_Superelevation")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_superelevation, properties={
        "Side": [side],
        "Superelevation": slope,
        "TransitionSuperelevation": ["LINEAR"]
    })

    nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    nest.RelatedObjects += (referent,)
    return referent


def make_angle(slope):
    # from Fig 8.15.3.15.A, X is towards the left, Y is up, and angle is positive CW from +X.
    # this function converts traditional engineering slopes to angular measure for use in IfcOpenCrossProfileDef
    return math.pi - math.atan(slope)


file = ifcopenshell.file(schema="IFC4X3_ADD2")
project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Superelevation Example")
site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")

length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
angle = ifcopenshell.api.unit.add_si_unit(file, unit_type="PLANEANGLEUNIT")
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
    parent=geometric_representation_context)

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site,])

start_station = 10000.
alignment = ifcopenshell.api.alignment.create(file, "A-Line", include_vertical=True, start_station=start_station)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=((500., 2500.))),
    StartDirection=math.radians(327.0613),
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=1956.785654,
    PredefinedType="LINE"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

x = float(end[0, 3]) / unit_scale
y = float(end[1, 3]) / unit_scale
dx = float(end[0, 0])
dy = float(end[1, 0])
dir = math.atan2(dy, dx)
segment2 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((x, y)),
    StartDirection=dir,
    StartRadiusOfCurvature=1000.,
    EndRadiusOfCurvature=1000.,
    SegmentLength=1919.222667,
    PredefinedType="CIRCULARARC"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment2)

x = float(end[0, 3]) / unit_scale
y = float(end[1, 3]) / unit_scale
dx = float(end[0, 0])
dy = float(end[1, 0])
dir = math.atan2(dy, dx)
segment3 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((x, y)),
    StartDirection=dir,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=1886.905454,
    PredefinedType="LINE"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment3)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)

vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=5000.,
    StartHeight=100.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

r1 = add_superelevation(file, "Start Transition",       alignment, 11776.79,       start_station, "BOTH",  -0.02)
add_superelevation(file, "Start Runoff Left",            alignment, 11836.79,       start_station, "LEFT",   0.00)
add_superelevation(file, "Start Runoff Right",           alignment, 11836.79,       start_station, "RIGHT",  0.02)
r2 = add_superelevation(file, "Start Full Super Left",  alignment, 11836.79 + 60., start_station, "LEFT",  -0.02)
add_superelevation(file, "Start Full Super Right",       alignment, 11836.79 + 60., start_station, "RIGHT",  0.02)
r3 = add_superelevation(file, "Start Max Super Left",   alignment, 12016.79,       start_station, "LEFT",  -0.06)
add_superelevation(file, "Start Max Super Right",        alignment, 12016.79,       start_station, "RIGHT",  0.06)
r4 = add_superelevation(file, "End Max Super Left",     alignment, 13816.01,       start_station, "LEFT",  -0.06)
add_superelevation(file, "End Max Super Right",          alignment, 13816.01,       start_station, "RIGHT",  0.06)
r5 = add_superelevation(file, "End Full Super Left",    alignment, 13996.01 - 60., start_station, "LEFT",  -0.02)
add_superelevation(file, "End Full Super Right",         alignment, 13996.01 - 60., start_station, "RIGHT",  0.02)
add_superelevation(file, "End Runoff Left",              alignment, 13996.01,       start_station, "RIGHT",  0.00)
add_superelevation(file, "End Runoff Right",             alignment, 13996.01,       start_station, "RIGHT",  0.02)
r6 = add_superelevation(file, "End Transition",         alignment, 14046.01,       start_station, "BOTH",  -0.02)

curve = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, curve)

road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road,])

road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(), Name="RoadPart1", UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part,])

crown_slope = 0.02
superelevation = 0.06
width = 100.0

normal_offset_point = file.createIfcCartesianPoint((width, -width * crown_slope))
super_offset_point = file.createIfcCartesianPoint((width, -width * superelevation))

cs1 = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[width, width],
    Slopes=[make_angle(crown_slope), make_angle(-crown_slope)],
    OffsetPoint=normal_offset_point
)
cs2 = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[width, width],
    Slopes=[make_angle(crown_slope), make_angle(crown_slope)],
    OffsetPoint=normal_offset_point
)
cs3 = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[width, width],
    Slopes=[make_angle(superelevation), make_angle(superelevation)],
    OffsetPoint=super_offset_point
)
cs4 = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[width, width],
    Slopes=[make_angle(superelevation), make_angle(superelevation)],
    OffsetPoint=super_offset_point
)
cs5 = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[width, width],
    Slopes=[make_angle(crown_slope), make_angle(crown_slope)],
    OffsetPoint=normal_offset_point
)
cs6 = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[width, width],
    Slopes=[make_angle(crown_slope), make_angle(-crown_slope)],
    OffsetPoint=normal_offset_point
)

file.createIfcRelAssociatesProfileDef(GlobalId=ifcopenshell.guid.new(), RelatedObjects=(r1,), RelatingProfileDef=cs1)
file.createIfcRelAssociatesProfileDef(GlobalId=ifcopenshell.guid.new(), RelatedObjects=(r2,), RelatingProfileDef=cs2)
file.createIfcRelAssociatesProfileDef(GlobalId=ifcopenshell.guid.new(), RelatedObjects=(r3,), RelatingProfileDef=cs3)
file.createIfcRelAssociatesProfileDef(GlobalId=ifcopenshell.guid.new(), RelatedObjects=(r4,), RelatingProfileDef=cs4)
file.createIfcRelAssociatesProfileDef(GlobalId=ifcopenshell.guid.new(), RelatedObjects=(r5,), RelatingProfileDef=cs5)
file.createIfcRelAssociatesProfileDef(GlobalId=ifcopenshell.guid.new(), RelatedObjects=(r6,), RelatingProfileDef=cs6)

surface = file.createIfcSectionedSurface(
    Directrix=curve,
    CrossSectionPositions=[
        r1.ObjectPlacement.RelativePlacement,
        r2.ObjectPlacement.RelativePlacement,
        r3.ObjectPlacement.RelativePlacement,
        r4.ObjectPlacement.RelativePlacement,
        r5.ObjectPlacement.RelativePlacement,
        r6.ObjectPlacement.RelativePlacement,
    ],
    CrossSections=[cs1, cs2, cs3, cs4, cs5, cs6]
)

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="SectionedSurface", Items=[surface])

product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

pavement = file.createIfcPavement(
    GlobalId=ifcopenshell.guid.new(),
    Name="Pavement",
    ObjectPlacement=file.createIfcLocalPlacement(
        RelativePlacement=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0, 0.0)))
        )
    ),
    Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=road_part, products=[pavement,])

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSurface_Superelevation.ifc")
file.write(output_path)
print("Done!")
