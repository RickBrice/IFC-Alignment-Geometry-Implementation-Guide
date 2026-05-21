# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcSectionedSolidHorizontal with single superelevation expressed via
# IfcDerivedProfileDef. The trapezoidal ballast-bed profile from §10.6.7 is the parent
# profile; each cross-section position wraps it in an IfcDerivedProfileDef whose 2D
# transformation operator rotates the profile about the track centerline by the
# superelevation angle at that station. The alignment is a 50 m straight, due East,
# at zero grade with no cant. See §10.6.9 of the guide.

import math
import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

# Superelevation parameter — change this value to adjust the cross-slope at the end station.
# SUPERELEVATION_RATE is the cross-slope (rise/run) at station 50 m; start is always 0.
# Positive values raise the right side of the profile (left-curving convention).
SUPERELEVATION_RATE = 0.10   # 10 % cross-slope

scripts_dir = os.path.dirname(os.path.abspath(__file__))
examples_dir = os.path.join(scripts_dir, "..")

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid Horizontal - Single Superelevation")
site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")

length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
angle = ifcopenshell.api.unit.add_si_unit(file, unit_type="PLANEANGLEUNIT")
ifcopenshell.api.unit.assign_unit(file, units=[length, angle])

geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
body = ifcopenshell.api.context.add_context(
    file,
    context_type="Model",
    context_identifier="Body",
    target_view="MODEL_VIEW",
    parent=geometric_representation_context)

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

# Alignment — straight, due East (StartDirection=0), zero grade, 50 m. No cant.
alignment = ifcopenshell.api.alignment.create(
    file, "Alignment",
    include_vertical=True,
    include_cant=False,
    start_station=0.
)

layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
h_segment = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=50.,
    PredefinedType="LINE"
)
ifcopenshell.api.alignment.create_layout_segment(file, layout, h_segment)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
v_segment = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=50.,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, v_segment)

# Railway spatial hierarchy.
railway = file.createIfcRailway(GlobalId=ifcopenshell.guid.new(), Name="Railway")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[railway])

railway_part = file.createIfcRailwayPart(
    GlobalId=ifcopenshell.guid.new(),
    Name="Track",
    PredefinedType="TRACK",
    UsageType="LONGITUDINAL"
)
ifcopenshell.api.aggregate.assign_object(file, relating_object=railway, products=[railway_part])

# Base cross-section profile — same trapezoid as §10.6.7, counter-clockwise winding.
#
#   (-29.5, 0.5) -------- (29.5, 0.5)
#      /                        \
#   (-30, 0) -------------- (30, 0)
#
point_list = file.createIfcCartesianPointList2D(
    CoordList=[(-30., 0.), (30., 0.), (29.5, 0.5), (-29.5, 0.5)]
)
poly_curve = file.createIfcIndexedPolyCurve(
    Points=point_list,
    Segments=[file.createIfcLineIndex((1, 2, 3, 4, 1))]
)
base_profile = file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)


def make_derived_profile(rate):
    # Rotate base_profile by arctan(rate) about the cross-section origin (track centerline).
    # The 2D rotation is expressed via IfcCartesianTransformationOperator2D; Axis1 defines
    # the direction of the rotated X-axis in the parent coordinate system.
    theta = math.atan(rate)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    operator = file.createIfcCartesianTransformationOperator2D(
        Axis1=file.createIfcDirection(DirectionRatios=(cos_t, sin_t)),
        LocalOrigin=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
        Scale=1.0
    )
    return file.createIfcDerivedProfileDef(
        ProfileType="AREA",
        ParentProfile=base_profile,
        Operator=operator
    )


profile_start = make_derived_profile(0.0)                  # 0 % at station 0 m
profile_end   = make_derived_profile(SUPERELEVATION_RATE)  # 10 % at station 50 m

# Directrix — IfcGradientCurve (no cant means get_curve returns IfcGradientCurve, not
# IfcSegmentedReferenceCurve; update_end_point is called once, not on BaseCurve).
directrix = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, directrix)

pos_start = file.createIfcAxis2PlacementLinear(
    Location=file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(0.),
        BasisCurve=directrix
    )
)
pos_end = file.createIfcAxis2PlacementLinear(
    Location=file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(50.),
        BasisCurve=directrix
    )
)

solid = file.createIfcSectionedSolidHorizontal(
    Directrix=directrix,
    CrossSections=[profile_start, profile_end],
    CrossSectionPositions=[pos_start, pos_end]
)

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body,
    RepresentationIdentifier="Body",
    RepresentationType="SolidModel",
    Items=[solid]
)

product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

course = file.createIfcCourse(
    GlobalId=ifcopenshell.guid.new(),
    Name="Ballast Bed",
    PredefinedType="BALLASTBED",
    ObjectPlacement=file.createIfcLocalPlacement(
        RelativePlacement=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint(Coordinates=(0., 0., 0.))
        )
    ),
    Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=railway_part, products=[course])

output_path = os.path.join(examples_dir, "IfcSectionedSolidHorizontal_single_superelevation.ifc")
file.write(output_path)
print("Done!")
