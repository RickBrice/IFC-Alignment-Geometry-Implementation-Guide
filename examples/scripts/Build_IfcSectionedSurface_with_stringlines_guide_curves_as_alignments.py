# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Same variable-width stringline surface as v1, but each offset curve is wrapped as a
# separate IfcAlignment to satisfy the IFC rooted-entity validation requirement (IFC105).

import os
import math
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit


def make_angle(slope):
    # from Fig 8.15.3.15.A, X is towards the left, Y is up, and angle is positive CW from +X.
    # this function converts tranditional engineering slopes to angular measure for use in IfcOpenCrossProfileDef
    return math.pi + math.atan(slope)
    

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="Sectioned Surface with Stringlines")
site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(),Name="Site")

length = ifcopenshell.api.unit.add_si_unit(file,unit_type="LENGTHUNIT")
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

ifcopenshell.api.aggregate.assign_object(file,relating_object=project,products=[site,])

start_station = 500.
alignment = ifcopenshell.api.alignment.create(file,"Main-Line",include_vertical=True,start_station=start_station)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=((0.,0.))),
    StartDirection=0.0,
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=200.,
    PredefinedType = "LINE"
)

end = ifcopenshell.api.alignment.create_layout_segment(file,layout,segment1)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)

segment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=200.,
    StartHeight=0.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType = "CONSTANTGRADIENT"
)

end = ifcopenshell.api.alignment.create_layout_segment(file,vlayout,segment1)

basis_curve = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, basis_curve)

road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(),Name="Road1")
ifcopenshell.api.aggregate.assign_object(file,relating_object=site,products=[road,])

road_part = file.createIfcRoadPart(GlobalId=ifcopenshell.guid.new(),Name="RoadPart1",UsageType="LONGITUDINAL")
ifcopenshell.api.aggregate.assign_object(file,relating_object=road,products=[road_part,])

crownslope = 0.2
width = 30.

alignment_a = ifcopenshell.api.alignment.create_as_offset_curve(file,name="A-line",offsets=[
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(0.),OffsetLateral=width,OffsetVertical=-width*crownslope),
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(100.),OffsetLateral=1.5*width,OffsetVertical=-1.5*width*crownslope),
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(200.),OffsetLateral=width,OffsetVertical=-width*crownslope)
                                                        ])
alignment_b = ifcopenshell.api.alignment.create_as_offset_curve(file,name="B-line",offsets=[
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(0.),OffsetLateral=0.,OffsetVertical=0.),
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(100.),OffsetLateral=0.,OffsetVertical=0.),
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(200.),OffsetLateral=0.,OffsetVertical=0.),
                                                        ])
alignment_c = ifcopenshell.api.alignment.create_as_offset_curve(file,name="C-line",offsets=[
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(0.),OffsetLateral=-width,OffsetVertical=-width*crownslope),
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(100.),OffsetLateral=-1.5*width,OffsetVertical=-1.5*width*crownslope),
                                                          file.createIfcPointByDistanceExpression(BasisCurve=basis_curve,DistanceAlong=file.createIfcLengthMeasure(200.),OffsetLateral=-width,OffsetVertical=-width*crownslope),
                                                        ])

offset_curve_a = ifcopenshell.api.alignment.get_curve(alignment_a)
offset_curve_b = ifcopenshell.api.alignment.get_curve(alignment_b)
offset_curve_c = ifcopenshell.api.alignment.get_curve(alignment_c)

offset_curve_a.Tag = "A"
offset_curve_b.Tag = "B"
offset_curve_c.Tag = "C"



cs = file.createIfcOpenCrossProfileDef(
        ProfileType="CURVE",
        HorizontalWidths=True,
        Widths=[width,width],
        Slopes=[make_angle(-crownslope),make_angle(crownslope)],
        Tags=["A","B","C"],
        OffsetPoint=file.createIfcCartesianPoint((width,-width*crownslope))
    )

op1 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(0.),BasisCurve=basis_curve))
op2 = file.createIfcAxis2PlacementLinear(Location=file.createIfcPointByDistanceExpression(DistanceAlong=file.createIfcLengthMeasure(200.),BasisCurve=basis_curve))

surface = file.createIfcSectionedSurface(
    Directrix = basis_curve,
    CrossSectionPositions=[op1,op2],
    CrossSections=[cs,cs]
)


representation = file.createIfcShapeRepresentation(
    ContextOfItems=body, RepresentationIdentifier="Body", RepresentationType="SectionedSurface", Items=[surface])


product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

proxy = file.createIfcBuildingElementProxy(GlobalId=ifcopenshell.guid.new(),Name="Proxy",
        ObjectPlacement=file.createIfcLocalPlacement(
            RelativePlacement=file.createIfcAxis2Placement3D(
                Location=file.createIfcCartesianPoint(Coordinates=((0.0,0.0,0.0)))
            )
        ),
        Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file,relating_structure=road_part,products=[proxy])


output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IfcSectionedSurface_with_stringlines_guide_curves_as_alignments.ifc")
file.write(output_path)
print("Done!")