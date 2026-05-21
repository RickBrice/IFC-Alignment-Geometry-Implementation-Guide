# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates the minimal definition of IfcSectionedSolidHorizontal: a uniform trapezoidal
# cross-section swept along a 3D alignment comprising a Bloss horizontal transition, flat
# vertical grade, and Bloss cant segment. No profile rotation, superelevation, or guide
# curves are used. See §10.6.7 of the guide.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid Horizontal - Minimal")
site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")

length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
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

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

start_station = 0.
alignment = ifcopenshell.api.alignment.create(
    file, "Alignment",
    include_vertical=True,
    include_cant=True,
    start_station=start_station
)

# Horizontal layout — Bloss transition from infinite radius to 300 m, curving left.
# StartRadiusOfCurvature = 0 encodes infinite radius (tangent entry).
# Positive EndRadiusOfCurvature = curve to the left.
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
h_segment = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=300.,
    SegmentLength=100.,
    PredefinedType="BLOSSCURVE"
)
ifcopenshell.api.alignment.create_layout_segment(file, layout, h_segment)

# Vertical layout — flat grade.
vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
v_segment = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=100.,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, v_segment)

# Cant layout — Bloss transition from 0 to 500 mm, right rail elevated.
# For a left-curving alignment the right rail carries the superelevation.
clayout = ifcopenshell.api.alignment.get_cant_layout(alignment)
c_segment = file.createIfcAlignmentCantSegment(
    StartDistAlong=0.,
    HorizontalLength=100.,
    StartCantLeft=0.,
    EndCantLeft=0.,
    StartCantRight=0.,
    EndCantRight=0.16,
    PredefinedType="BLOSSCURVE"
)
ifcopenshell.api.alignment.create_layout_segment(file, clayout, c_segment)

# Railway containment hierarchy.
railway = file.createIfcRailway(GlobalId=ifcopenshell.guid.new(), Name="Railway1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[railway])

railway_part = file.createIfcRailwayPart(
    GlobalId=ifcopenshell.guid.new(),
    Name="Track",
    PredefinedType="TRACK",
    UsageType="LONGITUDINAL"
)
ifcopenshell.api.aggregate.assign_object(file, relating_object=railway, products=[railway_part])

# Cross-section profile — trapezoid, counter-clockwise winding.
# Indices are 1-based; the closing 1 at the end makes the polycurve closed.
#
#   (-29.5, 0.5) -------- (29.5, 0.5)
#      /                        \
#  (-30, 0) -------------- (30, 0)
#
point_list = file.createIfcCartesianPointList2D(
    CoordList=[(-30., 0.), (30., 0.), (29.5, 0.5), (-29.5, 0.5)]
)
poly_curve = file.createIfcIndexedPolyCurve(
    Points=point_list,
    Segments=[file.createIfcLineIndex((1, 2, 3, 4, 1))]
)
profile = file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)

# Directrix is IfcSegmentedReferenceCurve — horizontal + vertical + cant combined.
directrix = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, directrix.BaseCurve)
ifcopenshell.api.alignment.update_end_point(file, directrix)

pos_start = file.createIfcAxis2PlacementLinear(
    Location=file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(0.),
        BasisCurve=directrix
    )
)
pos_end = file.createIfcAxis2PlacementLinear(
    Location=file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(100.),
        BasisCurve=directrix
    )
)

solid = file.createIfcSectionedSolidHorizontal(
    Directrix=directrix,
    CrossSections=[profile, profile],
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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSolidHorizontal.ifc")
file.write(output_path)
print("Done!")
