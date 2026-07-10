# Author: Richard Brice, PE
# Date: 2026-07-10
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Demonstrates the INTERSECTION referent pattern from Guide Section 9.5 (grounded in ISO 19148
# Section 6.2.12.1): a single crossing is modeled as two independent IfcReferent instances, one per
# alignment, never one referent shared between both. Each referent's ObjectPlacement is an
# IfcLinearPlacement resolved against its own alignment's curve only, its Pset_Stationing.Station is
# expressed in its own alignment's stationing system, and it is linked to its own alignment by its own
# IfcRelPositions (alignment as RelatingPositioningElement, referent as RelatedProducts) -- this is what
# removes the ambiguity of whose stationing system the Station value belongs to. Nothing in the schema
# formally correlates the two referents as "the same crossing"; the correlation is instead recorded with
# an IfcAnnotation (Description records the station equivalence) grouped with both referents via
# IfcGroup / IfcRelAssignsToGroup.
#
# Alignment A starts at (0, 0), heads due east, length 1000 ft, elevation 0 climbing at 3%, stationing
# starts at 1+00. Alignment B starts at (500, -500), heads due north, length 1000 ft, elevation 0
# climbing at 3%, stationing starts at 1+10. They cross in plan at (500, 0) -- 500 ft along each
# alignment from its own start -- and since both climb at the same grade, they meet at the same
# elevation (15 ft): a genuine 3D, at-grade intersection.
#
# See also Build_IntersectionReferent_GradeSeparatedCrossing.py, where flipping Alignment B's grade
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
import ifcopenshell.guid

file = ifcopenshell.file(schema="IFC4X3_ADD2")
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

    ifcopenshell.api.spatial.reference_structure(file, products=[alignment], relating_structure=site)
    return alignment

# Alignment A -- straight tangent from (0, 0) heading due east for 1000 ft, elevation 0 climbing at 3%,
# stationing starting at 1+00 (station 100.0).
gradient_a = 0.03
alignment_a = create_straight_graded_alignment(
    "Alignment A", (0.0, 0.0), (1000.0, 0.0), gradient=gradient_a, start_station=100.0
)

# Alignment B -- straight tangent from (500, -500) heading due north for 1000 ft, elevation 0 climbing
# at 3%, stationing starting at 1+10 (station 110.0). Same grade as Alignment A, so they meet at a true
# 3D intersection.
gradient_b = 0.03
alignment_b = create_straight_graded_alignment(
    "Alignment B", (500.0, -500.0), (500.0, 500.0), gradient=gradient_b, start_station=110.0
)

# Builds one INTERSECTION referent owned by a single alignment, per Section 9.5 / checklist #12:
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

# Alignment A runs along y = 0; Alignment B runs along x = 500. They cross at (500, 0), 500 ft along
# each alignment from its own start. referent_a is owned by Alignment A alone and stationed in A's
# system (1+00 + 500 ft = 6+00); referent_b is a completely separate IfcReferent instance, owned by
# Alignment B alone and stationed in B's system (1+10 + 500 ft = 6+10). Neither referent references the
# other, and neither references the other alignment.
distance_along_a = 500.0
distance_along_b = 500.0

referent_a = create_intersection_referent(alignment_a, distance_along_a)
referent_b = create_intersection_referent(alignment_b, distance_along_b)

# Per Section 9.5.3, nothing in the schema formally links Alignment A's and Alignment B's INTERSECTION
# referents -- the correspondence is a project-specific convention that can be annotated with an
# IfcAnnotation or a custom property, rather than a formal IFC relationship. Here, an IfcAnnotation is
# placed at the crossing and its Description records the station equivalence as text, exactly like the
# station-equivalence notes on a 2D plan sheet. An IfcGroup / IfcRelAssignsToGroup then gathers the
# annotation together with referent_a and referent_b, so the correlation is also discoverable by any
# consumer that can follow group assignments -- without creating an IfcRelPositions (or any other formal
# positioning relationship) between the two referents themselves.
elevation_a = gradient_a * distance_along_a
elevation_b = gradient_b * distance_along_b
crossing_point = (500.0, 0.0, (elevation_a + elevation_b) / 2.0)
correlation_text = f"{alignment_a.Name} Sta. {referent_a.Name} = {alignment_b.Name} Sta. {referent_b.Name} (at-grade crossing)"

annotation = file.createIfcAnnotation(
    GlobalId=ifcopenshell.guid.new(),
    OwnerHistory=None,
    Name="Intersection: Alignment A / Alignment B",
    Description=correlation_text,
    ObjectType=None,
    ObjectPlacement=file.createIfcLocalPlacement(
        PlacementRelTo=None,
        RelativePlacement=file.createIfcAxis2Placement3D(Location=file.createIfcCartesianPoint(crossing_point)),
    ),
    Representation=None,
    PredefinedType=None,
)
# bSI Validation Service requires every IfcAnnotation to be contained in an IfcSpatialStructureElement
# via IfcRelContainedInSpatialStructure.
ifcopenshell.api.spatial.assign_container(file, products=[annotation], relating_structure=site)

crossing_group = file.createIfcGroup(
    GlobalId=ifcopenshell.guid.new(),
    OwnerHistory=None,
    Name="Intersection: Alignment A / Alignment B",
)
file.createIfcRelAssignsToGroup(
    GlobalId=ifcopenshell.guid.new(),
    OwnerHistory=None,
    RelatedObjects=[referent_a, referent_b, annotation],
    RelatedObjectsType=None,
    RelatingGroup=crossing_group,
)

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IntersectionReferent_AtGradeCrossing.ifc")
file.write(output_path)
print("Done!")
