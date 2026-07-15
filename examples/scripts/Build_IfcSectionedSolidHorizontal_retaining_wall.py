# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces two IFC models for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcSectionedSolidHorizontal with a transforming cross-section: a retaining
# wall profile whose stem height and footing width vary along a 50 m straight grade at
# 10% due East. Two variants are produced to illustrate the effect of the Axis direction
# in IfcAxis2PlacementLinear (see §10.5 and §10.6.2.3 of the guide):
#   - implicit_axis: Axis omitted (implementation-defined default)
#   - explicit_axis: Axis = (0,0,1) supplied explicitly (plumb cross-sections)

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit

# Retaining wall geometry parameters.
FOOTING_WIDTH = 2.0   # total bottom width of the footing
TOE           = 0.5   # distance from the rightmost footing edge to the face of the wall
WALL_WIDTH    = 0.5   # thickness of the wall stem
FOOTING_DEPTH = 0.5   # depth of the footing below grade

scripts_dir = os.path.dirname(os.path.abspath(__file__))
examples_dir = os.path.join(scripts_dir, "..")


def build_model(explicit_axis):
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Sectioned Solid Horizontal - Retaining Wall")
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

    # Alignment — straight, due East (StartDirection=0), 10% grade, 50 m.
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
        StartGradient=0.10,
        EndGradient=0.10,
        PredefinedType="CONSTANTGRADIENT"
    )
    ifcopenshell.api.alignment.create_layout_segment(file, vlayout, v_segment)

    # Road spatial hierarchy.
    road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road")
    ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])

    road_part = file.createIfcRoadPart(
        GlobalId=ifcopenshell.guid.new(),
        Name="Shoulder",
        PredefinedType="SHOULDER",
        UsageType="LONGITUDINAL"
    )
    ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])

    # Cross-section profile — retaining wall with footing, counter-clockwise winding.
    # h is the stem height; all other dimensions are drawn from the module-level constants.
    #
    #   (-WALL_WIDTH, h) ----------- (0, h)
    #          |                         |
    #   (-WALL_WIDTH, 0)             (0, 0)
    #          |                         |
    #   (TOE-FOOTING_WIDTH, 0)      (TOE, 0)
    #          |                         |
    #   (TOE-FOOTING_WIDTH, -FOOTING_DEPTH) -- (TOE, -FOOTING_DEPTH)
    #
    def make_profile(h, footing_width=FOOTING_WIDTH, toe=TOE,
                     wall_width=WALL_WIDTH, footing_depth=FOOTING_DEPTH):
        coords = [
            (0.,                  0.),
            (0.,                  h),
            (-wall_width,         h),
            (-wall_width,         0.),
            (toe - footing_width, 0.),
            (toe - footing_width, -footing_depth),
            (toe,                -footing_depth),
            (toe,                 0.),
        ]
        point_list = file.createIfcCartesianPointList2D(CoordList=coords)
        poly_curve = file.createIfcIndexedPolyCurve(
            Points=point_list,
            Segments=[file.createIfcLineIndex((1, 2, 3, 4, 5, 6, 7, 8, 1))]
        )
        return file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)

    profile_start = make_profile(h=2.00)
    profile_mid   = make_profile(h=3.00, footing_width=2.5)
    profile_end   = make_profile(h=1.50)

    # Directrix is IfcGradientCurve — horizontal + vertical combined.
    directrix = ifcopenshell.api.alignment.get_curve(alignment)
    ifcopenshell.api.alignment.update_end_point(file, directrix)

    def make_placement(dist):
        kwargs = dict(
            Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(dist),
                BasisCurve=directrix
            )
        )
        if explicit_axis:
            kwargs['Axis'] = file.createIfcDirection(DirectionRatios=(0., 0., 1.))
        return file.createIfcAxis2PlacementLinear(**kwargs)

    solid = file.createIfcSectionedSolidHorizontal(
        Directrix=directrix,
        CrossSections=[profile_start, profile_mid, profile_end],
        CrossSectionPositions=[make_placement(0.), make_placement(25.), make_placement(50.)]
    )

    representation = file.createIfcShapeRepresentation(
        ContextOfItems=body,
        RepresentationIdentifier="Body",
        RepresentationType="SolidModel",
        Items=[solid]
    )

    product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

    wall = file.createIfcWall(
        GlobalId=ifcopenshell.guid.new(),
        Name="Retaining Wall",
        PredefinedType="RETAININGWALL",
        ObjectPlacement=file.createIfcLocalPlacement(
            RelativePlacement=file.createIfcAxis2Placement3D(
                Location=file.createIfcCartesianPoint(Coordinates=(0., 0., 0.))
            )
        ),
        Representation=product_rep
    )

    ifcopenshell.api.spatial.assign_container(file, relating_structure=road_part, products=[wall])

    return file


# Implicit axis — Axis omitted; result depends on implementation default (Figure 10.5.5-2).
model = build_model(explicit_axis=False)
model.write(os.path.join(examples_dir, "IfcSectionedSolidHorizontal_retaining_wall_implicit_axis.ifc"))
print("Written: IfcSectionedSolidHorizontal_retaining_wall_implicit_axis.ifc")

# Explicit axis — Axis = (0,0,1); cross-section faces are plumb (Figure 10.5.5-1).
model = build_model(explicit_axis=True)
model.write(os.path.join(examples_dir, "IfcSectionedSolidHorizontal_retaining_wall_explicit_axis.ifc"))
print("Written: IfcSectionedSolidHorizontal_retaining_wall_explicit_axis.ifc")
