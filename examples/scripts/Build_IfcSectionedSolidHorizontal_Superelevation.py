# Author: Richard Brice, PE
# Date: 2026-08-03
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates IfcSectionedSolidHorizontal with a crowned pavement cross-section swept along a
# three-segment highway alignment (tangent–arc–tangent). Six distinct IfcArbitraryClosedProfileDef
# instances — one per cross-section position — directly encode the cross-slope geometry at each
# station. The left and right shoulders vary independently, matching the superelevation progression
# of Build_IfcSectionedSurface_Superelevation.py: normal crown → adverse crown → full
# superelevation → full superelevation → adverse crown → normal crown. No rotation operators,
# tags, or guide curves are used. See §10.6.2.2 of the guide.
#
# The alignment also carries the same 14 SUPERELEVATIONEVENT IfcReferent instances (by name and
# Pset_Superelevation content) as Build_IfcSectionedSurface_Superelevation.py, nested to
# IfcAlignment via their own IfcRelNests, separate from the STATION stationing nest. Six of them
# (the LEFT/BOTH event at each cross-section station) double as this solid's CrossSectionPositions;
# the other eight are markers only, matching the surface script's structure.

import math
import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.pset
import ifcopenshell.api.unit
import ifcopenshell.util.alignment
import ifcopenshell.util.element
import ifcopenshell.util.unit

CROWN_SLOPE = 0.02   # 2 % normal cross-slope (rise/run)
SUPER_SLOPE = 0.06   # 6 % full superelevation (rise/run)
HALF_WIDTH  = 30.0   # m — half-width of pavement
THICKNESS   = 0.5    # m — slab thickness

scripts_dir  = os.path.dirname(os.path.abspath(__file__))
examples_dir = os.path.join(scripts_dir, "..")

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(
    GlobalId=ifcopenshell.guid.new(),
    Name="Sectioned Solid Horizontal - Crown Superelevation"
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

# Alignment — tangent + circular arc + tangent (metric equivalent of the alignment in
# Build_IfcSectionedSurface_Superelevation.py). Cross-sections 1–2 land in the leading
# tangent, 3–4 in the arc, and 5–6 in the trailing tangent.
start_station = 3000.
alignment = ifcopenshell.api.alignment.create(
    file, "A-Line",
    include_vertical=True,
    start_station=start_station
)
layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

segment1 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint(Coordinates=(500., 2500.)),
    StartDirection=math.radians(327.0613),
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=600.,
    PredefinedType="LINE"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
x  = float(end[0, 3]) / unit_scale
y  = float(end[1, 3]) / unit_scale
dx = float(end[0, 0])
dy = float(end[1, 0])
segment2 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((x, y)),
    StartDirection=math.atan2(dy, dx),
    StartRadiusOfCurvature=300.,
    EndRadiusOfCurvature=300.,
    SegmentLength=585.,
    PredefinedType="CIRCULARARC"
)
end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment2)

x  = float(end[0, 3]) / unit_scale
y  = float(end[1, 3]) / unit_scale
dx = float(end[0, 0])
dy = float(end[1, 0])
segment3 = file.createIfcAlignmentHorizontalSegment(
    StartPoint=file.createIfcCartesianPoint((x, y)),
    StartDirection=math.atan2(dy, dx),
    StartRadiusOfCurvature=0.0,
    EndRadiusOfCurvature=0.0,
    SegmentLength=600.,
    PredefinedType="LINE"
)
ifcopenshell.api.alignment.create_layout_segment(file, layout, segment3)

vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
vsegment1 = file.createIfcAlignmentVerticalSegment(
    StartDistAlong=0.,
    HorizontalLength=1800.,
    StartHeight=30.,
    StartGradient=0.,
    EndGradient=0.,
    PredefinedType="CONSTANTGRADIENT"
)
ifcopenshell.api.alignment.create_layout_segment(file, vlayout, vsegment1)

directrix = ifcopenshell.api.alignment.get_curve(alignment)
ifcopenshell.api.alignment.update_end_point(file, directrix)

# Spatial hierarchy.
road = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Road1")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road])
road_part = file.createIfcRoadPart(
    GlobalId=ifcopenshell.guid.new(),
    Name="RoadPart1",
    UsageType="LONGITUDINAL"
)
ifcopenshell.api.aggregate.assign_object(file, relating_object=road, products=[road_part])


def fix_stationing_referent_placement(file, alignment):
    # ifcopenshell.api.alignment.create() creates the starting-station referent before any
    # horizontal segments exist, so add_stationing_referent's curve-has-segments check fails and
    # it falls back to an IfcLocalPlacement copied from IfcAlignment's own placeholder placement
    # at (0, 0) -- the "semantic-only alignment" case (§9.3.3). Now that the horizontal layout has
    # real segments, rebuild the referent's placement as the IfcLinearPlacement /
    # IfcPointByDistanceExpression at DistanceAlong = 0.0 that add_stationing_referent would have
    # produced had the curve existed at creation time.
    nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    referent = nest.RelatedObjects[0]
    old_placement = referent.ObjectPlacement
    only_referenced_by_referent = file.get_total_inverses(old_placement) == 1
    curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    referent.ObjectPlacement = file.createIfcLinearPlacement(
        RelativePlacement=file.createIfcAxis2PlacementLinear(
            Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(0.0),
                BasisCurve=curve
            )
        )
    )
    ifcopenshell.api.alignment.update_fallback_position(file, referent.ObjectPlacement)
    if only_referenced_by_referent:
        ifcopenshell.util.element.remove_deep2(file, old_placement)


def get_superelevation_event_nest(alignment):
    # Distinct from ifcopenshell.api.alignment.get_stationing_nest, which is scoped to the
    # STATION referent(s) that establish the alignment's stationing system. SUPERELEVATIONEVENT
    # referents must not share that nest (§9.3.2/§9.3.4) — they get their own IfcRelNests, also
    # nested to IfcAlignment.
    for nest in alignment.IsNestedBy:
        for related_object in nest.RelatedObjects:
            if related_object.is_a("IfcReferent") and related_object.PredefinedType == "SUPERELEVATIONEVENT":
                return nest
    return None


def add_superelevation(file, name, alignment, curve, distance_along, start_station, side, slope):
    station = start_station + distance_along
    referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=name + " (" + ifcopenshell.util.alignment.station_as_string(file, station) + ")",
        Description=None,
        ObjectType=None,
        ObjectPlacement=file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(distance_along),
                    BasisCurve=curve
                )
            )
        ),
        Representation=None,
        PredefinedType="SUPERELEVATIONEVENT",
    )
    ifcopenshell.api.alignment.update_fallback_position(file, referent.ObjectPlacement)

    pset_superelevation = ifcopenshell.api.pset.add_pset(file, product=referent, name="Pset_Superelevation")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_superelevation, properties={
        "Side": [side],
        "Superelevation": slope,
        "TransitionSuperelevation": ["LINEAR"]
    })

    nest = get_superelevation_event_nest(alignment)
    if nest is None:
        nest = file.createIfcRelNests(
            GlobalId=ifcopenshell.guid.new(), RelatingObject=alignment, RelatedObjects=(referent,)
        )
    else:
        nest.RelatedObjects += (referent,)
    return referent


def make_profile(slope_right, slope_left):
    # Crown cross-section: 60 m wide, 0.5 m thick, no bevels.
    # Profile origin (0, 0) is the crown — the top of the section at the centerline.
    #
    # slope_right: signed fraction (rise/run) at the right shoulder, measured from the crown.
    #              Negative = right shoulder is below the crown.
    # slope_left:  signed fraction (rise/run) at the left shoulder, measured from the crown.
    #              Positive = left shoulder is above the crown.
    #
    # The soffit is offset 0.5 m vertically below each top-surface point.
    # Vertices are wound counterclockwise.
    #
    right_y = HALF_WIDTH * slope_right
    left_y  = HALF_WIDTH * slope_left
    point_list = file.createIfcCartesianPointList2D(
        CoordList=[
            (-HALF_WIDTH, left_y  - THICKNESS),  # 1  bottom left
            (0.,         -THICKNESS),              # 2  bottom center
            (HALF_WIDTH,  right_y - THICKNESS),  # 3  bottom right
            (HALF_WIDTH,  right_y),               # 4  top right shoulder
            (0.,          0.),                     # 5  crown
            (-HALF_WIDTH, left_y),                # 6  top left shoulder
        ]
    )
    poly_curve = file.createIfcIndexedPolyCurve(
        Points=point_list,
        Segments=[file.createIfcLineIndex((1, 2, 3, 4, 5, 6, 1))]
    )
    return file.createIfcArbitraryClosedProfileDef(ProfileType="AREA", OuterCurve=poly_curve)


# Six cross-section stations — (distance from directrix start, slope_right, slope_left).
# Slopes are signed fractions (rise/run) measured from the crown (0, 0): negative = below,
# positive = above. Left and right shoulders vary independently, mirroring the six
# IfcOpenCrossProfileDef instances in Build_IfcSectionedSurface_Superelevation.py. These six
# stations are also the six anchor SUPERELEVATIONEVENT referents below (Start Transition, Start
# Full Super Left, Start Max Super Left, End Max Super Left, End Full Super Left, End Transition).
# Sections 1–2 lie in the leading tangent, 3–4 in the 300 m arc, 5–6 in the trailing tangent.
#
#  dist (m)   slope_right   slope_left   state
#  --------   -----------   ----------   ------------------------------------
#     540       -0.02         -0.02      normal crown
#     580       -0.02         +0.02      adverse crown — transition begins
#     615       -0.06         +0.06      full superelevation begins
#    1163       -0.06         +0.06      full superelevation ends
#    1199       -0.02         +0.02      adverse crown — returning to crown
#    1240       -0.02         -0.02      normal crown restored
#
# The eight remaining SUPERELEVATIONEVENT referents (Start/End Runoff Left/Right, and the Right-
# side counterpart of each anchor above) are markers only — they are not among CrossSectionPositions
# below. Start/End Runoff sit at the distance where the moving shoulder's slope crosses zero
# between the flanking anchors; their slope values are the exact linear interpolation this unguided
# (no string-line) solid geometry already implies at that distance, not independently authored.
fix_stationing_referent_placement(file, alignment)

r1 = add_superelevation(file, "Start Transition",       alignment, directrix, 540.0,   start_station, "BOTH",  -CROWN_SLOPE)
add_superelevation(file, "Start Runoff Left",            alignment, directrix, 560.0,   start_station, "LEFT",   0.0)
add_superelevation(file, "Start Runoff Right",           alignment, directrix, 560.0,   start_station, "RIGHT", -CROWN_SLOPE)
r2 = add_superelevation(file, "Start Full Super Left",  alignment, directrix, 580.0,   start_station, "LEFT",  +CROWN_SLOPE)
add_superelevation(file, "Start Full Super Right",       alignment, directrix, 580.0,   start_station, "RIGHT", -CROWN_SLOPE)
r3 = add_superelevation(file, "Start Max Super Left",   alignment, directrix, 615.0,   start_station, "LEFT",  +SUPER_SLOPE)
add_superelevation(file, "Start Max Super Right",        alignment, directrix, 615.0,   start_station, "RIGHT", -SUPER_SLOPE)
r4 = add_superelevation(file, "End Max Super Left",     alignment, directrix, 1163.0,  start_station, "LEFT",  +SUPER_SLOPE)
add_superelevation(file, "End Max Super Right",          alignment, directrix, 1163.0,  start_station, "RIGHT", -SUPER_SLOPE)
r5 = add_superelevation(file, "End Full Super Left",    alignment, directrix, 1199.0,  start_station, "LEFT",  +CROWN_SLOPE)
add_superelevation(file, "End Full Super Right",         alignment, directrix, 1199.0,  start_station, "RIGHT", -CROWN_SLOPE)
add_superelevation(file, "End Runoff Left",              alignment, directrix, 1219.5,  start_station, "LEFT",   0.0)
add_superelevation(file, "End Runoff Right",             alignment, directrix, 1219.5,  start_station, "RIGHT", -CROWN_SLOPE)
r6 = add_superelevation(file, "End Transition",         alignment, directrix, 1240.0,  start_station, "BOTH",  -CROWN_SLOPE)

CS_ANCHORS = [
    (r1, -CROWN_SLOPE, -CROWN_SLOPE),
    (r2, -CROWN_SLOPE, +CROWN_SLOPE),
    (r3, -SUPER_SLOPE, +SUPER_SLOPE),
    (r4, -SUPER_SLOPE, +SUPER_SLOPE),
    (r5, -CROWN_SLOPE, +CROWN_SLOPE),
    (r6, -CROWN_SLOPE, -CROWN_SLOPE),
]

positions = [referent.ObjectPlacement.RelativePlacement  for referent, _,       _        in CS_ANCHORS]
profiles  = [make_profile(slope_r, slope_l)               for _,        slope_r, slope_l  in CS_ANCHORS]

for referent, profile in zip((r1, r2, r3, r4, r5, r6), profiles):
    file.createIfcRelAssociatesProfileDef(
        GlobalId=ifcopenshell.guid.new(), RelatedObjects=(referent,), RelatingProfileDef=profile
    )

solid = file.createIfcSectionedSolidHorizontal(
    Directrix=directrix,
    CrossSections=profiles,
    CrossSectionPositions=positions
)

representation = file.createIfcShapeRepresentation(
    ContextOfItems=body,
    RepresentationIdentifier="Body",
    RepresentationType="SolidModel",
    Items=[solid]
)
product_rep = file.createIfcProductDefinitionShape(Representations=[representation])

pavement = file.createIfcPavement(
    GlobalId=ifcopenshell.guid.new(),
    Name="Pavement",
    ObjectPlacement=file.createIfcLocalPlacement(
        RelativePlacement=file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint(Coordinates=(0., 0., 0.))
        )
    ),
    Representation=product_rep
)

ifcopenshell.api.spatial.assign_container(file, relating_structure=road_part, products=[pavement])

output_path = os.path.join(examples_dir, "IfcSectionedSolidHorizontal_superelevation.ifc")
file.write(output_path)
print("Done!")
