# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates the edge case where IfcOffsetCurveByDistances.BasisCurve and
# IfcPointByDistanceExpression.BasisCurve reference different curves.
# IFC4x3 does not explicitly prohibit this configuration (see §5.0).

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

file = ifcopenshell.file(schema="IFC4X3_ADD2")
# ViewDefinition is NotAssigned because IfcOffsetCurveByDistances is not part of any
# standardized MVD schema subset or implementation level.
file.header.file_description.description = ("ViewDefinition [NotAssigned]",)
project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Alignment")
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

# --- E-Line: 200-ft circular arc (used as IfcOffsetCurveByDistances.BasisCurve) ---
alignment_1 = ifcopenshell.api.alignment.create(file, "E-Line", include_vertical=True, start_station=10000.)
layout_1 = ifcopenshell.api.alignment.get_horizontal_layout(alignment_1)

ifcopenshell.api.alignment.create_layout_segment(file, layout_1,
    file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0., 0.)),
        StartDirection=0.,
        StartRadiusOfCurvature=1000.,
        EndRadiusOfCurvature=1000.,
        SegmentLength=200.,
        PredefinedType="CIRCULARARC"
    )
)

vlayout_1 = ifcopenshell.api.alignment.get_vertical_layout(alignment_1)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout_1,
    file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.,
        HorizontalLength=200.,
        StartHeight=0.,
        StartGradient=0.,
        EndGradient=0.,
        PredefinedType="CONSTANTGRADIENT"
    )
)

curve_1 = ifcopenshell.api.alignment.get_curve(alignment_1)
ifcopenshell.api.alignment.update_end_point(file, curve_1)

# --- Reference-Line: 200-ft straight line offset 10 ft north (used as IfcPointByDistanceExpression.BasisCurve) ---
alignment_2 = ifcopenshell.api.alignment.create(file, "Reference-Line", include_vertical=True, start_station=10000.)
layout_2 = ifcopenshell.api.alignment.get_horizontal_layout(alignment_2)

ifcopenshell.api.alignment.create_layout_segment(file, layout_2,
    file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0., 10.)),
        StartDirection=0.,
        StartRadiusOfCurvature=0.,
        EndRadiusOfCurvature=0.,
        SegmentLength=200.,
        PredefinedType="LINE"
    )
)

vlayout_2 = ifcopenshell.api.alignment.get_vertical_layout(alignment_2)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout_2,
    file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.,
        HorizontalLength=200.,
        StartHeight=0.,
        StartGradient=0.,
        EndGradient=0.,
        PredefinedType="CONSTANTGRADIENT"
    )
)

curve_2 = ifcopenshell.api.alignment.get_curve(alignment_2)
ifcopenshell.api.alignment.update_end_point(file, curve_2)

# OffsetValues reference curve_2 (Reference-Line).
# IfcOffsetCurveByDistances.BasisCurve will be reassigned to curve_1 (E-Line) below.
offsets = [
    file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(0.0),
        OffsetLateral=5.0,
        BasisCurve=curve_2,
    ),
    file.createIfcPointByDistanceExpression(
        DistanceAlong=file.createIfcLengthMeasure(200.0),
        OffsetLateral=5.0,
        BasisCurve=curve_2,
    ),
]

# create_as_offset_curve infers IfcOffsetCurveByDistances.BasisCurve from the offsets,
# so it is initially set to curve_2. Reassign it to curve_1 to produce the split-basis configuration.
offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file, "Offset1", offsets, 5000.)

for rep in offset_alignment.Representation.Representations:
    for item in rep.Items:
        if item.is_a("IfcOffsetCurveByDistances"):
            item.BasisCurve = curve_1

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcOffsetCurveByDistances_split_basis.ifc")
file.write(output_path)
print("Done!")
