# Author: Richard Brice, PE
# Date: 2026-05-20
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcSectionedSolidHorizontal swept along a complete 3D alignment comprising:
#   - 100 m Bloss horizontal transition (infinite to 300 m radius, curving left)
#   - 100 m flat vertical alignment
#   - 100 m Bloss cant segment (0 to 500 mm, right rail elevated)
# The trapezoidal cross-section is defined as an IfcArbitraryClosedProfileDef using
# IfcIndexedPolyCurve. The solid is contained in an IfcRailwayPart.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid Horizontal - Bloss Cant")
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
    file, "Bloss-Alignment",
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
    EndCantRight=0.5,
    PredefinedType="BLOSSCURVE"
)
ifcopenshell.api.alignment.create_layout_segment(file, clayout, c_segment)

# Railway containment hierarchy.
railway = file.createIfcRailway(GlobalId=ifcopenshell.guid.new(), Name="Railway1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[railway])

railway_part = file.createIfcRailwayPart(
    GlobalId=ifcopenshell.guid.new(),
    Name="Track",
    PredefinedType="TRACK"
)
ifcopenshell.api.aggregate.assign_object(file, relating_object=railway, products=[railway_part])

# Cross-section profile — trapezoid, counter-clockwise winding.
# Indices are 1-based; the closing 1 at the end makes the polycurve closed.
#
#   (-28, 0.5) -------- (28, 0.5)
#      /                        \
#  (-30, 0) -------------- (30, 0)
#
point_list = file.createIfcCartesianPointList2D(
    CoordList=[(-30., 0.), (30., 0.), (28., 0.5), (-28., 0.5)]
)
poly_curve = file.createIfcIndexedPolyCurve(
    Points=point_list,
    Segments=[file.createIfcLineIndex((1, 2, 3, 4, 1))]
)
profile = file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)

# Directrix is IfcSegmentedReferenceCurve — horizontal + vertical + cant combined.
directrix = ifcopenshell.api.alignment.get_curve(alignment)

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

proxy = file.createIfcBuildingElementProxy(
    GlobalId=ifcopenshell.guid.new(),
    Name="Track Body",
    ObjectPlacement=file.createIfcLocalPlacement(
        RelativePlacement=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint(Coordinates=(0., 0., 0.))
        )
    ),
    Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=railway_part, products=[proxy])

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSolidHorizontal_bloss_cant.ifc")
file.write(output_path)
print("Done!")
