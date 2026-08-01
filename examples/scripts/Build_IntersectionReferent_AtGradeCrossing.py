# Author: Richard Brice, PE
# Date: 2026-07-13
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates the INTERSECTION referent pattern from Guide Section 9.5.1 (grounded in ISO 19148
# Section 6.2.12.1): a single crossing is modeled as two independent IfcReferent instances, one per
# alignment, never one referent shared between both. Each referent's ObjectPlacement is an
# IfcLinearPlacement resolved against its own alignment's curve only, its Pset_Stationing.Station is
# expressed in its own alignment's stationing system, and it is linked to its own alignment by its own
# IfcRelPositions (alignment as RelatingPositioningElement, referent as RelatedProducts) -- this is what
# removes the ambiguity of whose stationing system the Station value belongs to.
#
# The referents only ever name a station on their own alignment -- they assert nothing about whether the
# two alignments actually cross. That fact is recorded separately and independently, per Guide Section
# 9.5.2, with a single IfcRelInterferesElements relating the two IfcRoad facilities that the alignments
# lay out. IfcRelInterferesElements.RelatingElement/RelatedElement are typed IfcInterferenceSelect, which
# only accepts IfcElement or IfcSpatialElement -- IfcAlignment is a subtype of IfcPositioningElement, a
# sibling branch, so it cannot be a party to that relationship directly. Each alignment is therefore
# referenced by its own IfcRoad (IfcRelReferencedInSpatialStructure), and it is the two IfcRoad instances
# that the interference relates.
#
# This is the same Washington Street / First Avenue crossing used as the running example in Guide
# Section 9.5, with stationing chosen so the crossing lands exactly on the illustrative station values
# used in Figure 9.5-1 and Figure 9.5.2-1 (Sta. 10+00 on Washington Street, Sta. 12+00 on First Avenue).
#
# Washington Street starts at (0, 0), heads due east, length 1000 ft, elevation 0 climbing at 3%,
# stationing starts at 5+00 (station 500.0). First Avenue starts at (500, -500), heads due north, length
# 1000 ft, elevation 0 climbing at 3%, stationing starts at 7+00 (station 700.0). They cross in plan at
# (500, 0) -- 500 ft along each alignment from its own start, i.e. Sta. 10+00 on Washington Street and
# Sta. 12+00 on First Avenue -- and since both climb at the same grade, they meet at the same elevation
# (15 ft): a genuine 3D, at-grade intersection.
#
# See also Build_IntersectionReferent_GradeSeparatedCrossing.py, where flipping First Avenue's grade
# breaks the 3D coincidence while the plan-view crossing stays identical.

import os
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.aggregate
import ifcopenshell.api.spatial
import ifcopenshell.api.pset
import ifcopenshell.util.alignment
import ifcopenshell.util.element
import ifcopenshell.guid

file = ifcopenshell.file(schema="IFC4X3_ADD2")
file.header.file_description.description = ("ViewDefinition [Alignment-basedView]",)

project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Intersection Referents: At-Grade Crossing")

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
# layout functions are called on it explicitly.
def create_straight_graded_alignment(name, start_point, end_point, gradient, start_station):
    length = ((end_point[0] - start_point[0]) ** 2 + (end_point[1] - start_point[1]) ** 2) ** 0.5
    alignment = ifcopenshell.api.alignment.create(file, name, include_vertical=True, start_station=start_station)

    horizontal_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    ifcopenshell.api.alignment.layout_horizontal_alignment_by_pi_method(
        file, horizontal_layout, [start_point, end_point], []
    )

    vertical_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    ifcopenshell.api.alignment.layout_vertical_alignment_by_pi_method(
        file, vertical_layout, [(0.0, 0.0), (length, gradient * length)], []
    )

    fix_starting_referent_placement(alignment)

    return alignment

# create() (called above) builds the alignment's starting STATION referent -- via
# add_stationing_referent() -- before the horizontal layout has any segments. At that point
# get_basis_curve(alignment) returns an empty IfcCompositeCurve, so add_stationing_referent() falls back
# to IfcLocalPlacement at the alignment's own local origin (0.0, 0.0) with PlacementRelTo=None. That
# fallback is never revisited once real geometry exists, so every alignment's starting referent ends up
# placed at literal world (0, 0, 0) regardless of where that alignment's curve actually starts -- e.g.
# First Avenue's Sta. 7+00 referent would resolve to the same point as Washington Street's Sta. 5+00
# referent, even though First Avenue starts at (500, -500), not (0, 0). This rebuilds that referent's
# ObjectPlacement as a proper IfcLinearPlacement / IfcPointByDistanceExpression at DistanceAlong = 0.0
# against the now-populated basis curve, the same construction add_stationing_referent() would have used
# had the curve existed when it ran.
def fix_starting_referent_placement(alignment):
    nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    referent = nest.RelatedObjects[0]
    old_placement = referent.ObjectPlacement

    curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    object_placement = file.createIfcLinearPlacement(
        RelativePlacement=file.createIfcAxis2PlacementLinear(
            Location=file.createIfcPointByDistanceExpression(
                DistanceAlong=file.createIfcLengthMeasure(0.0),
                OffsetLateral=None,
                OffsetVertical=None,
                OffsetLongitudinal=None,
                BasisCurve=curve,
            )
        ),
    )
    ifcopenshell.api.alignment.update_fallback_position(file, object_placement)
    referent.ObjectPlacement = object_placement
    ifcopenshell.util.element.remove_deep2(file, old_placement)

# Washington Street -- straight tangent from (0, 0) heading due east for 1000 ft, elevation 0 climbing
# at 3%, stationing starting at 5+00 (station 500.0), chosen so the crossing 500 ft in lands on Sta.
# 10+00, matching Figure 9.5-1 and Figure 9.5.2-1.
gradient_washington = 0.03
alignment_washington = create_straight_graded_alignment(
    "Washington Street", (0.0, 0.0), (1000.0, 0.0), gradient=gradient_washington, start_station=500.0
)

# First Avenue -- straight tangent from (500, -500) heading due north for 1000 ft, elevation 0 climbing
# at 3%, stationing starting at 7+00 (station 700.0), chosen so the crossing 500 ft in lands on Sta.
# 12+00. Same grade as Washington Street, so they meet at a true 3D intersection.
gradient_first_avenue = 0.03
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

# Builds one INTERSECTION referent owned by a single alignment, per Section 9.5.1 / checklist #14:
#  - ObjectPlacement -- IfcLinearPlacement / IfcPointByDistanceExpression against get_curve(alignment)
#    (the alignment's actual curve -- its IfcGradientCurve when a vertical layout exists -- not just the
#    plan-view IfcCompositeCurve).
#  - Pset_Stationing.Station -- the alignment's own starting station plus distance_along.
#  - IfcRelPositions -- RelatingPositioningElement = alignment, RelatedProducts = [referent]. This is the
#    reverse direction from the IfcRelPositions that a POSITION referent uses to label a product like a
#    bridge pier (referent as relating element, product as related) -- here the alignment is doing the
#    relating, because the relationship's purpose is to declare ownership of the referent's stationing,
#    not to have the referent label some other product's position.
# The referent is not nested under the alignment via IfcRelNests -- that relationship is reserved for
# STATION referents that define the alignment's stationing system itself (Section 9.3.1); an
# INTERSECTION referent, like a POSITION referent, only consumes that system.
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

# Washington Street runs along y = 0; First Avenue runs along x = 500. They cross at (500, 0), 500 ft
# along each alignment from its own start. referent_washington is owned by Washington Street alone and
# stationed in its own system (5+00 + 500 ft = 10+00); referent_first_avenue is a completely separate
# IfcReferent instance, owned by First Avenue alone and stationed in its own system (7+00 + 500 ft =
# 12+00) -- matching the Pset_Stationing values shown in Figure 9.5-1. Neither referent references the
# other, and neither references the other alignment.
distance_along_washington = 500.0
distance_along_first_avenue = 500.0

referent_washington = create_intersection_referent(alignment_washington, distance_along_washington)
referent_first_avenue = create_intersection_referent(alignment_first_avenue, distance_along_first_avenue)

# Per Guide Section 9.5.2, the crossing itself -- as a fact about the two facilities, independent of
# either INTERSECTION referent -- is recorded with a single IfcRelInterferesElements relating the
# Washington Street and First Avenue IfcRoad instances, matching Figure 9.5.2-1. InterferenceType is an
# IfcIdentifier (free text, not a restricted enumeration); "Crosses" is used here as a project
# convention. ImpliedOrder is FALSE because an at-grade crossing has no source/target direction --
# neither road passes over the other.
#
# InterferenceGeometry is modeled as an IfcConnectionPointGeometry, reusing the same
# IfcPointByDistanceExpression instances already built for each INTERSECTION referent's own
# ObjectPlacement (§9.5.1) rather than introducing new IfcCartesianPoint literals -- the referents and
# the interference geometry describe the same two points, so they share the same point entities.
# PointOnRelatingElement/PointOnRelatedElement are still two distinct entities (one per alignment's own
# BasisCurve), even though they resolve to the same (500, 0, 15) in this true at-grade crossing.
interference_geometry = file.createIfcConnectionPointGeometry(
    PointOnRelatingElement=referent_washington.ObjectPlacement.RelativePlacement.Location,
    PointOnRelatedElement=referent_first_avenue.ObjectPlacement.RelativePlacement.Location,
)

interference_description = (
    f"{road_washington.Name} crosses {road_first_avenue.Name} at grade "
    f"({alignment_washington.Name} Sta. {referent_washington.Name} = "
    f"{alignment_first_avenue.Name} Sta. {referent_first_avenue.Name})"
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
    InterferenceType="Crosses",
    ImpliedOrder=False,
    InterferenceSpace=None,
)

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IntersectionReferent_AtGradeCrossing.ifc")
file.write(output_path)
print("Done!")
