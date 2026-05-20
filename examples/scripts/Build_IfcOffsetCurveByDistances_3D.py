# Author: Richard Brice, PE
# Date: 2026-05-20
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcOffsetCurveByDistances with a 3D basis curve. Offset1 uses the
# IfcGradientCurve directly as its basis curve. Offset2 uses the IfcGradientCurve's
# underlying IfcCompositeCurve (the horizontal-only curve) as its basis curve.
# IfcAlignment states that IfcOffsetCurveByDistances can be 2D or 3D when defined
# relative to an IfcGradientCurve. However, Offset2 fails the validation rule
# IfcShapeRepresentation.CorrectItemsForType because its basis curve is the 2D
# IfcCompositeCurve, making the resulting offset curve 2D rather than 3D.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

file = ifcopenshell.file(schema="IFC4X3_ADD2")
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

alignment = ifcopenshell.api.alignment.create(file,"E-Line",include_vertical=True,start_station=10000.)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

segment = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((0.,0.)),
    StartDirection=0.,
    StartRadiusOfCurvature=1000.,
    EndRadiusOfCurvature=1000.,
    SegmentLength=200.,
    PredefinedType="CIRCULARARC"
)
end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout,
    file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.,
        HorizontalLength=200.,
        StartHeight=0.,
        StartGradient=0.,
        EndGradient=0.,
        PredefinedType="CONSTANTGRADIENT"
    )
)

gradient_curve = ifcopenshell.api.alignment.get_curve(alignment)
composite_curve = gradient_curve.BaseCurve

offsets = [
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.0),OffsetLateral=10.0,BasisCurve=gradient_curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.0),OffsetLateral=20.0,BasisCurve=gradient_curve),
]
offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file,"Offset1",offsets,5000.)


offsets = [
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.0),OffsetLateral=-10.0,BasisCurve=composite_curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(50.0),OffsetLateral=-40.0,BasisCurve=composite_curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(100.0),OffsetLateral=-20.0,BasisCurve=composite_curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(150.0),OffsetLateral=-30.0,BasisCurve=composite_curve),
   file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.0),OffsetLateral=-20.0,BasisCurve=composite_curve),
]
offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file,"Offset2",offsets,5000.)

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcOffsetCurveByDistances_3D.ifc")
file.write(output_path)
print("Done!")
