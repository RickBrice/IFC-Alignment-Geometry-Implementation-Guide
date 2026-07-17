# Author: Richard Brice, PE
# Date: 2026-05-20
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcOffsetCurveByDistances using two offset alignments: one with a simple
# two-point linearly varying offset and one with a multi-point irregular offset profile.
# This example fails the validation service check for Entity Rule - IfcShapeReprsentation.CorrectItemsForType 
# because the resulting IfcOffsetCurveByDistances are 2D and thus cannot be used directly in a 3D geometric item definition.
# However, IfcAlignment explicity states that IfcOffsetCurveByDistances can be a 2D representation.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

file = ifcopenshell.file(schema="IFC4X3_ADD2")
# ViewDefinition is NotAssigned because IfcOffsetCurveByDistances is not part of any
# standardized MVD schema subset or implementation level.
file.header.file_description.description = ("ViewDefinition [NotAssigned]",)
project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="Alignment")
length = ifcopenshell.api.unit.add_conversion_based_unit(file,name="foot")
angle = ifcopenshell.api.unit.add_si_unit(file,unit_type="PLANEANGLEUNIT")
ifcopenshell.api.unit.assign_unit(file,units=[length,angle])
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

alignment = ifcopenshell.api.alignment.create(file,"E-Line",start_station=10000.)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
curve = ifcopenshell.api.alignment.get_curve(alignment)

segment = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((0.,0.)),
    StartDirection=0.,
    StartRadiusOfCurvature=1000.,
    EndRadiusOfCurvature=1000.,
    SegmentLength=200.,
    PredefinedType="CIRCULARARC"
)
end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment)


offsets = [
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.0),OffsetLateral=10.0,BasisCurve=curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.0),OffsetLateral=20.0,BasisCurve=curve),
]
offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file,"Offset1",offsets,5000.)


offsets = [
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.0),OffsetLateral=-10.0,BasisCurve=curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(50.0),OffsetLateral=-40.0,BasisCurve=curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(100.0),OffsetLateral=-20.0,BasisCurve=curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(150.0),OffsetLateral=-30.0,BasisCurve=curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.0),OffsetLateral=-20.0,BasisCurve=curve),
]
offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file,"Offset2",offsets,5000.)

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcOffsetCurveByDistances_2D.ifc")
file.write(output_path)
print("Done!")