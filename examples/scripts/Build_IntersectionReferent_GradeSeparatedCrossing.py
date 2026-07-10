# Author: Richard Brice, PE
# Date: 2026-07-10
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Companion to Build_IntersectionReferent_AtGradeCrossing.py. Same plan geometry, same INTERSECTION
# referent pattern from Guide Section 9.5 -- two independent IfcReferent instances, one per alignment,
# each placed on and owned by its own alignment -- but Alignment B's grade is flipped to -3% (it
# descends instead of climbing). Both still start at z=0:
#  - Alignment A climbs from (0,0,0) to (1000,0,30) -- unchanged.
#  - Alignment B now descends from (500,-500,0) to (500,500,-30).
#
# In plan view, A and B still cross at (500, 0) -- 500 ft along each from its own start -- the kind of
# crossing that would be flagged as an intersection point on a traditional 2D civil plan sheet. But at
# that station, Alignment A is at elevation +15 ft and Alignment B is at -15 ft: a 30 ft vertical
# separation. This is a grade separation -- e.g. a road passing under a railway or over another road --
# not a physical meeting point.
#
# Per Section 9.5.3, this is exactly the case where the schema's silence about correlating the two
# referents matters: at an at-grade crossing, a consumer could at least discover the correspondence by
# noticing the two referents' ObjectPlacement results coincide (as in the companion script). Here that
# geometric coincidence doesn't exist either -- the two referents share only their plan-view (X, Y)
# location. Nothing in the file states that referent_a and referent_b describe the same crossing, and
# nothing distinguishes this grade-separated crossing from an at-grade one -- both use the identical
# PredefinedType = INTERSECTION.

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
# stationing starting at 1+00 (station 100.0). Unchanged from the at-grade companion script.
gradient_a = 0.03
alignment_a = create_straight_graded_alignment(
    "Alignment A", (0.0, 0.0), (1000.0, 0.0), gradient=gradient_a, start_station=100.0
)

# Alignment B -- straight tangent from (500, -500) heading due north for 1000 ft, elevation 0,
# stationing starting at 1+10 (station 110.0) -- same plan geometry as the companion script, but now
# descending at 3% (gradient=-0.03) instead of climbing, so it no longer meets Alignment A in 3D.
gradient_b = -0.03
alignment_b = create_straight_graded_alignment(
    "Alignment B", (500.0, -500.0), (500.0, 500.0), gradient=gradient_b, start_station=110.0
)

# Identical to the companion script: builds one INTERSECTION referent owned by a single alignment, per
# Section 9.5 / checklist #12 -- ObjectPlacement against that alignment's own curve, Pset_Stationing.
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

# referent_a is owned by Alignment A alone and stationed in A's system (1+00 + 500 ft = 6+00);
# referent_b is a completely separate IfcReferent, owned by Alignment B alone and stationed in B's
# system (1+10 + 500 ft = 6+10). As in the companion script, neither referent references the other or
# the other alignment -- the only thing that changes here is where each one physically resolves to.
distance_along_a = 500.0
distance_along_b = 500.0

referent_a = create_intersection_referent(alignment_a, distance_along_a)
referent_b = create_intersection_referent(alignment_b, distance_along_b)

# Per Section 9.5.3, nothing in the schema formally links Alignment A's and Alignment B's INTERSECTION
# referents -- the correspondence is a project-specific convention that can be annotated with an
# IfcAnnotation or a custom property, rather than a formal IFC relationship. This matters more here than
# in the at-grade companion script, since the referents' ObjectPlacement results no longer coincide at
# all -- there's no geometric fallback for discovering the correlation. An IfcAnnotation is placed at
# the midpoint between the two referents ((500, 0, 0) -- halfway between A's +15 ft and B's -15 ft) and
# its Description records the station equivalence and the vertical separation as text. An IfcGroup /
# IfcRelAssignsToGroup then gathers the annotation together with referent_a and referent_b, so the
# correlation is also discoverable by any consumer that can follow group assignments -- without creating
# an IfcRelPositions (or any other formal positioning relationship) between the two referents themselves.
elevation_a = gradient_a * distance_along_a
elevation_b = gradient_b * distance_along_b
crossing_point = (500.0, 0.0, (elevation_a + elevation_b) / 2.0)
delta_z = abs(elevation_a - elevation_b)
correlation_text = (
    f"{alignment_a.Name} Sta. {referent_a.Name} crosses {alignment_b.Name} Sta. {referent_b.Name} "
    f"in plan view only -- grade-separated, dZ = {delta_z:.2f} ft"
)

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

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "IntersectionReferent_GradeSeparatedCrossing.ifc")
file.write(output_path)
print("Done!")
