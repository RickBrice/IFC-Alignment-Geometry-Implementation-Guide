# Author: Richard Brice, PE
# Date: 2026-05-22
#
# Headfake model — produces Figure 10.6.1.6-2 in the IFC Alignment Geometry Implementation Guide.
#
# This model synthetically illustrates the expected geometry of IfcSectionedSurface with
# independent edge alignments (§10.6.1.6). Because no IFC viewer is currently known to
# resolve IfcOffsetCurveByDistances guide curves when rendering a sectioned surface, the
# correct visual result is approximated here by computing cross-section widths analytically
# from the circular arc edge geometry at 1 cm spacing (SECTION_SPACING), producing a
# near-smooth surface edge that represents what a stringline-capable viewer would render.
#
# This is NOT a reference implementation of the stringline mechanism. The actual example
# with correct IFC structure is IfcSectionedSurface_with_stringlines_independent_guide_curves.ifc.

import os
import math
import numpy as np
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

# --- Adjust this to control section spacing (in metres) ---
SECTION_SPACING = 0.01   # 1 cm
# ----------------------------------------------------------


def make_angle(slope):
    return math.pi + math.atan(slope)


file = ifcopenshell.file(schema="IFC4X3_ADD2")
# ViewDefinition is NotAssigned because IfcOffsetCurveByDistances (used as a stringline guide
# curve) is not part of any standardized MVD schema subset or implementation level.
file.header.file_description.description = ("ViewDefinition [NotAssigned]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Surface with Stringlines")
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
    parent=geometric_representation_context,
)

ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

crownslope = 0.2
width = 30.

radius = 300.
arc_length = 150.
sweep_angle = arc_length / radius
horizontal_length = radius * math.sin(sweep_angle)
cx = 0.
cy = width + radius

start_station = 500.
alignment = ifcopenshell.api.alignment.create(file, "Main-Line", include_vertical=True, start_station=start_station)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=((0., 0.))),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=horizontal_length,
    PredefinedType="LINE"
)

layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=horizontal_length,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

left_alignment = ifcopenshell.api.alignment.create(file, "Left_Edge", include_vertical=True)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=((0., width))),
    StartDirection=0.0,
    StartRadiusOfCurvature=radius,
    EndRadiusOfCurvature=radius,
    SegmentLength=arc_length,
    PredefinedType="CIRCULARARC"
)

layout = ifcopenshell.api.alignment.get_horizontal_layout(left_alignment)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=arc_length,
    StartHeight=0,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(left_alignment)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

right_alignment = ifcopenshell.api.alignment.create(file, "Right_Edge", include_vertical=True)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=((0., -width))),
    StartDirection=0.0,
    StartRadiusOfCurvature=-radius,
    EndRadiusOfCurvature=-radius,
    SegmentLength=arc_length,
    PredefinedType="CIRCULARARC"
)

layout = ifcopenshell.api.alignment.get_horizontal_layout(right_alignment)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(right_alignment)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

basis_curve = ifcopenshell.api.alignment.get_curve(alignment)
left_curve = ifcopenshell.api.alignment.get_curve(left_alignment)
right_curve = ifcopenshell.api.alignment.get_curve(right_alignment)
ifcopenshell.api.alignment.update_end_point(file, basis_curve)
ifcopenshell.api.alignment.update_end_point(file, left_curve)
ifcopenshell.api.alignment.update_end_point(file, right_curve)

road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])

road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(), Name="RoadPart1", UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])

n_sections = max(2, round(horizontal_length / SECTION_SPACING) + 1)
print(f"Generating {n_sections} sections at {SECTION_SPACING*100:.1f} cm spacing "
      f"over {horizontal_length:.3f} m ...")

positions = []
sections = []
vertical_edge_offsets = []

for dist in np.linspace(0, horizontal_length, n_sections):
    d = float(dist)
    w = cy - math.sqrt(radius**2 - (d - cx)**2)
    pos = file.createIfcPointByDistanceExpression(
        BasisCurve=basis_curve, DistanceAlong=file.createIfcLengthMeasure(d))
    positions.append(file.createIfcAxis2PlacementLinear(Location=pos))
    sections.append(file.createIfcOpenCrossProfileDef(
        ProfileType="CURVE",
        HorizontalWidths=True,
        Widths=[w, w],
        Slopes=[make_angle(-crownslope), make_angle(crownslope)],
        Tags=["A", "B", "C"],
        OffsetPoint=file.createIfcCartesianPoint((w, -w * crownslope))
    ))
    vertical_edge_offsets.append(file.createIfcPointByDistanceExpression(
        BasisCurve=left_curve,
        DistanceAlong=file.createIfcLengthMeasure(d),
        OffsetLateral=0.,
        OffsetVertical=-w * crownslope,
    ))

surface = file.createIfcSectionedSurface(
    Directrix=basis_curve,
    CrossSectionPositions=positions,
    CrossSections=sections,
)

alignment_a = ifcopenshell.api.alignment.create_as_offset_curve(file, name="Left Edge Offset", offsets=vertical_edge_offsets)
alignment_b = ifcopenshell.api.alignment.create_as_offset_curve(file, name="Main Line Offset", offsets=[
    file.createIfcPointByDistanceExpression(
        BasisCurve=basis_curve,
        DistanceAlong=file.createIfcLengthMeasure(0.),
        OffsetLateral=0.,
        OffsetVertical=0.,
    )
])
alignment_c = ifcopenshell.api.alignment.create_as_offset_curve(file, name="Right Edge Offset", offsets=vertical_edge_offsets)

offset_curve_a = ifcopenshell.api.alignment.get_curve(alignment_a)
offset_curve_b = ifcopenshell.api.alignment.get_curve(alignment_b)
offset_curve_c = ifcopenshell.api.alignment.get_curve(alignment_c)

offset_curve_a.Tag = "A"
offset_curve_b.Tag = "B"
offset_curve_c.Tag = "C"

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body,
    RepresentationIdentifier="Body",
    RepresentationType="SectionedSurface",
    Items=[surface],
)

product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

pavement = file.createIfcPavement(
    GlobalId=ifcopenshell.guid.new(),
    Name="Pavement",
    ObjectPlacement=file.createIfcLocalPlacement(
        RelativePlacement=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0, 0.0)))
        )
    ),
    Representation=product_rep,
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=road_part, products=[pavement])

output_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "IfcSectionedSurface_with_stringlines_headfake.ifc",
)
file.write(output_path)
print(f"Done! Written to: {output_path}")
