# Author: Richard Brice, PE
# Date: 2026-05-22
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Surface counterpart to Build_IfcSectionedSolidHorizontal.py.
# Demonstrates IfcSectionedSurface with IfcSegmentedReferenceCurve as the Directrix, so the
# cross-section profile rotates with cant. The alignment, flat vertical grade, and Bloss cant
# transition (0 to 160 mm, right rail elevated) are identical to the solid example. The open
# profile represents the flat top surface of the ballast bed — 29.5 m half-width each side,
# zero slope. Cant rotation is carried entirely by the IfcSegmentedReferenceCurve directrix,
# not by non-zero profile slopes. See §10.6.1.1 of the guide.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(
    GlobalId=ifcopenshell.guid.new(),
    Name="Sectioned Surface - SegmentedReferenceCurve Directrix"
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

segment_length = 50.
start_station = 0.
alignment = ifcopenshell.api.alignment.create(
    file, "Alignment",
    include_vertical=True,
    include_cant=True,
    start_station=start_station,
    #include_geometry=False
)

# Horizontal layout — Bloss transition from infinite radius to 300 m, curving left.
# StartRadiusOfCurvature = 0 encodes infinite radius (tangent entry).
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
h_segment = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(0., 0.)),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=100.,
    SegmentLength=segment_length,
    PredefinedType="BLOSSCURVE"
)
ifcopenshell.api.alignment.create_layout_segment(file, layout, h_segment)

# Vertical layout — flat grade.
vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
v_segment = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=segment_length,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, v_segment)

# Cant layout — Bloss transition from 0 to 160 mm, right rail elevated.
# For a left-curving alignment the right rail carries the superelevation.
clayout = ifcopenshell.api.alignment.get_cant_layout(alignment)
clayout.RailHeadDistance = 1.5
c_segment = file.createIfcAlignmentCantSegment(
    StartDistAlong=0.,
    HorizontalLength=segment_length,
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
    PredefinedType="TRACK",
    UsageType="LONGITUDINAL"
)
ifcopenshell.api.aggregate.assign_object(file, relating_object=railway, products=[railway_part])

# Open cross-section profile — flat top surface of the ballast bed, 29.5 m half-width each side.
# Slopes are zero: the top surface is flat and the banking is provided entirely by the
# IfcSegmentedReferenceCurve directrix rotating the profile frame with the cant.
profile = file.createIfcOpenCrossProfileDef(
    ProfileType="CURVE",
    HorizontalWidths=True,
    Widths=[clayout.RailHeadDistance],
    Slopes=[0.],
    OffsetPoint=file.createIfcCartesianPoint((clayout.RailHeadDistance/2,0.0))
)

# Directrix is IfcSegmentedReferenceCurve — horizontal + vertical + cant combined.
ifcopenshell.api.alignment.create_representation(file,alignment)
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
        DistanceAlong=file.createIfcLengthMeasure(segment_length),
        BasisCurve=directrix
    )
)

surface = file.createIfcSectionedSurface(
    Directrix=directrix,
    CrossSections=[profile, profile],
    CrossSectionPositions=[pos_start, pos_end]
)

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body,
    RepresentationIdentifier="Body",
    RepresentationType="SectionedSurface",
    Items=[surface]
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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSurface.ifc")
file.write(output_path)
print("Done!")
