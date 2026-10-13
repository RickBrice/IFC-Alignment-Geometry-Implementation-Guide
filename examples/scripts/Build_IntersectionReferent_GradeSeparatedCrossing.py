# Author: Richard Brice, PE
# Date: 2026-10-13
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Companion to Build_IntersectionReferent_AtGradeCrossing.py. Same plan geometry, same INTERSECTION
# referent pattern from Guide Section 9.5.1 -- two independent IfcReferent instances, one per alignment,
# each placed on and owned by its own alignment -- but First Avenue's grade is flipped to -3% (it
# descends instead of climbing). Both still start at z=0:
#  - Washington Street climbs from (0,0,0) to (1000,0,30) -- unchanged.
#  - First Avenue now descends from (500,-500,0) to (500,500,-30).
#
# In plan view, the two alignments still cross at (500, 0) -- 500 ft along each from its own start. But
# at that station, Washington Street is at elevation +15 ft and First Avenue is at -15 ft: a 30 ft
# vertical separation. This is a grade separation -- e.g. a road passing over another road -- not a
# physical meeting point.
#
# Per Guide Section 9.5.2, this is exactly the case where a directional InterferenceType earns its keep:
# the crossing is recorded with a single IfcRelInterferesElements relating the Washington Street and
# First Avenue IfcRoad facilities (the facilities each alignment lays out -- IfcAlignment itself cannot
# be a party to IfcRelInterferesElements, since IfcInterferenceSelect only accepts IfcElement or
# IfcSpatialElement, and IfcAlignment is a IfcPositioningElement -- each alignment is referenced by its
# own IfcRoad via IfcRelReferencedInSpatialStructure, not aggregated under it; see the comment above the
# IfcRoad creation below for why). InterferenceType = "PassesOver" and
# ImpliedOrder = TRUE record that Washington Street (RelatingElement) is the one physically above, First
# Avenue (RelatedElement) the one below -- information that neither INTERSECTION referent carries, since
# both alignments' referents use the identical PredefinedType regardless of whether the crossing is
# at-grade or grade-separated.
#
# Stationing is chosen so the crossing lands on the same illustrative station values used in the
# at-grade companion script and in Figure 9.5-1 (Sta. 10+00 on Washington Street, Sta. 12+00 on First
# Avenue).

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.aggregate
import ifcopenshell.api.spatial
import ifcopenshell.api.pset
import ifcopenshell.util.alignment
import ifcopenshell.guid

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Intersection Referents: Grade-Separated Crossing")

length_unit = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
ifcopenshell.api.unit.assign_unit(file, units=[length_unit])

geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
    file,
    context_type="Model",
    context_identifier="Axis",
    target_view="MODEL_VIEW",
    parent=geometric_representation_context,
)

site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="Site")
ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])

# Both alignments are a single straight, constant-grade run, so hpoints/vpoints only need a start and
# end point with no interior PIs. create_by_pi_method() can't be used here: it only creates a vertical
# layout when both vpoints and lengths are truthy, and an empty lengths list (no vertical curves, just
# one gradient) is falsy -- so a straight-grade-only vertical layout would silently be dropped. Instead,
# create() is called directly with include_vertical=True, then the horizontal and vertical PI-method
# layout functions are called on it explicitly. A negative gradient produces a descending grade.
def create_straight_graded_alignment(name, start_point, end_point, gradient, start_station):
    length = ((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2) ** 0.5
    alignment = ifcopenshell.api.alignment.create(file, name, include_vertical=True)

    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
        file, horizontal_layout, [start_point, end_point], []
    )

    vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(
        file, vertical_layout, [(0.0, 0.0), (length, gradient * length)], []
    )

    # Define the stationing now that the horizontal layout has segments, so the starting
    # referent is placed on the curve (ifcopenshell.api.alignment.create() no longer does this).
    ifcopenshell.api.alignment.add_stationing_referent(
        file,
        name=ifcopenshell.util.alignment.station_as_string(file, start_station),
        alignment=alignment,
        distance_along=0.0,
        station=start_station,
    )

    return alignment

# Washington Street -- straight tangent from (0, 0) heading due east for 1000 ft, elevation 0 climbing
# at 3%, stationing starting at 5+00 (station 500.0). Unchanged from the at-grade companion script.
gradient_washington = 0.03
alignment_washington = create_straight_graded_alignment(
    "Washington Street", (0.0, 0.0), (1000.0, 0.0), gradient=gradient_washington, start_station=500.0
)

# First Avenue -- straight tangent from (500, -500) heading due north for 1000 ft, elevation 0,
# stationing starting at 7+00 (station 700.0) -- same plan geometry and stationing as the companion
# script, but now descending at 3% (gradient=-0.03) instead of climbing, so it no longer meets
# Washington Street in 3D.
gradient_first_avenue = -0.03
alignment_first_avenue = create_straight_graded_alignment(
    "First Avenue", (500.0, -500.0), (500.0, 500.0), gradient=gradient_first_avenue, start_station=700.0
)

# Each alignment lays out one facility. Per Guide Section 9.5.2, IfcRoad -- not IfcAlignment -- is what
# IfcRelInterferesElements is later related through, since IfcAlignment is not eligible as an
# IfcInterferenceSelect party. The two IfcRoad instances are aggregated under Site (IfcRelAggregates),
# alongside the ordinary Project -> Site -> Road spatial breakdown.
#
# IfcAlignment stays where alignment.create() put it -- aggregated directly under IfcProject
# (IFC 4.1.4.1.1 Alignment Aggregation To Project) -- rather than being re-parented under its IfcRoad.
# The bSI Validation Service's SPS002 (Correct spatial breakdown) rule restricts what IfcRelAggregates
# may nest under an IfcRoad to other IfcFacility / IfcFacilityPartCommon / IfcRoadPart / IfcSpace
# instances; IfcAlignment is not in that list, so aggregating it under IfcRoad fails validation.
# reference_structure() instead creates an IfcRelReferencedInSpatialStructure -- a non-hierarchical
# relationship, not a decomposition -- linking each IfcRoad (RelatingStructure) to its IfcAlignment
# (RelatedElements). That relationship is what IfcRoad -> IfcAlignment actually is here.
road_washington = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="Washington Street")
road_first_avenue = file.createIfcRoad(GlobalId=ifcopenshell.guid.new(), Name="First Avenue")
ifcopenshell.api.aggregate.assign_object(file, relating_object=site, products=[road_washington, road_first_avenue])
ifcopenshell.api.spatial.reference_structure(file, products=[alignment_washington], relating_structure=road_washington)
ifcopenshell.api.spatial.reference_structure(file, products=[alignment_first_avenue], relating_structure=road_first_avenue)

# Identical to the companion script: builds one INTERSECTION referent owned by a single alignment, per
# Section 9.5.1 / checklist #14 -- ObjectPlacement against that alignment's own curve, Pset_Stationing.
# Station in that alignment's own stationing, and an IfcRelPositions with the alignment as
# RelatingPositioningElement and the referent as RelatedProducts. Not nested via IfcRelNests (that's
# reserved for STATION referents that define the stationing system itself).
def create_intersection_referent(alignment, distance_along):
    curve = ifcopenshell.api.alignment.get_curve(alignment)
    station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment) + distance_along
    name = ifcopenshell.util.alignment.station_as_string(file, station)

    object_placement = file.createIfcLinearPlacement(
        RelativePlacement=file.createIfcAxis2PlacementLinear(
            Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(distance_along),
                OffsetLateral=None,
                OffsetVertical=None,
                OffsetLongitudinal=None,
                BasisCurve=curve,
            )
        ),
    )
    ifcopenshell.api.alignment.update_fallback_position(file, object_placement)

    referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=name,
        Description=None,
        ObjectType=None,
        ObjectPlacement=object_placement,
        Representation=None,
        PredefinedType="INTERSECTION",
    )

    pset_stationing = ifcopenshell.api.pset.add_pset(file, product=referent, name="Pset_Stationing")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_stationing, properties={"Station": station})

    file.createIfcRelPositions(
        GlobalId=ifcopenshell.guid.new(),
        RelatingPositioningElement=alignment,
        RelatedProducts=[referent],
    )

    return referent

# referent_washington is owned by Washington Street alone and stationed in its own system (5+00 + 500 ft
# = 10+00); referent_first_avenue is a completely separate IfcReferent, owned by First Avenue alone and
# stationed in its own system (7+00 + 500 ft = 12+00) -- identical station values to the at-grade
# companion script. As in that script, neither referent references the other or the other alignment --
# the only thing that changes here is where each one physically resolves to.
distance_along_washington = 500.0
distance_along_first_avenue = 500.0

referent_washington = create_intersection_referent(alignment_washington, distance_along_washington)
referent_first_avenue = create_intersection_referent(alignment_first_avenue, distance_along_first_avenue)

# Per Guide Section 9.5.2, the crossing itself -- as a fact about the two facilities, independent of
# either INTERSECTION referent -- is recorded with a single IfcRelInterferesElements relating the
# Washington Street and First Avenue IfcRoad instances. Unlike the at-grade companion script, this
# crossing has a direction: Washington Street is physically above First Avenue at the crossing, so
# InterferenceType = "PassesOver" and ImpliedOrder = TRUE, meaning RelatingElement (Washington Street) is
# the source (the one passing over) and RelatedElement (First Avenue) is the target (the one passed
# under). InterferenceType remains an IfcIdentifier -- free text, not a restricted enumeration -- so
# "PassesOver" is a project convention, not a fixed schema value.
elevation_washington = gradient_washington * distance_along_washington
elevation_first_avenue = gradient_first_avenue * distance_along_first_avenue
delta_z = abs(elevation_washington - elevation_first_avenue)

# InterferenceGeometry is modeled as an IfcConnectionPointEccentricity, reusing the same
# IfcPointByDistanceExpression instances already built for each INTERSECTION referent's own
# ObjectPlacement (§9.5.1) rather than introducing new IfcCartesianPoint literals -- the referents and
# the interference geometry describe the same two points, so they share the same point entities. The
# two points share the same plan-view (X, Y) but no longer coincide in Z, so a plain
# IfcConnectionPointGeometry (as used in the at-grade companion script) can't represent the separation;
# IfcConnectionPointEccentricity adds EccentricityInX/Y/Z, which record the offset from
# PointOnRelatingElement (Washington Street, above) to PointOnRelatedElement (First Avenue, below).
interference_geometry = file.createIfcConnectionPointEccentricity(
    PointOnRelatingElement=referent_washington.ObjectPlacement.RelativePlacement.Location,
    PointOnRelatedElement=referent_first_avenue.ObjectPlacement.RelativePlacement.Location,
    EccentricityInX=0.0,
    EccentricityInY=0.0,
    EccentricityInZ=elevation_first_avenue - elevation_washington,
)

interference_description = (
    f"{road_washington.Name} passes over {road_first_avenue.Name} "
    f"({alignment_washington.Name} Sta. {referent_washington.Name} / "
    f"{alignment_first_avenue.Name} Sta. {referent_first_avenue.Name}, dZ = {delta_z:.2f} ft)"
)
file.create_entity(
    "IfcRelInterferesElements",
    GlobalId=ifcopenshell.guid.new(),
    OwnerHistory=None,
    Name="Washington Street / First Avenue Crossing",
    Description=interference_description,
    RelatingElement=road_washington,
    RelatedElement=road_first_avenue,
    InterferenceGeometry=interference_geometry,
    InterferenceType="PassesOver",
    ImpliedOrder=True,
    InterferenceSpace=None,
)

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IntersectionReferent_GradeSeparatedCrossing.ifc")
file.write(output_path)
print("Done!")
