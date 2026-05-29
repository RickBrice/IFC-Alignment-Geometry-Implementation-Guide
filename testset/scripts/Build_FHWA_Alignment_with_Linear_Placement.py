# Author: Richard Brice, PE
# Date: 2026-05-21
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Identical to Build_FHWA_Alignment.py plus one IfcReferent + IfcLinearPlacement per 100 ft
# station (100+00 through 223+00, 124 stations total). Each placement carries a Pset_Stationing
# property set with the station value and a CartesianPosition fallback computed via
# ifcopenshell.api.alignment.update_fallback_position.
# Output: testset/real-world-alignments/FHWA_Alignment_with_Linear_Placement.ifc
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import common
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.util.unit

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "real-world-alignments"
OUTPUT_FILE = "FHWA_Alignment_with_Linear_Placement.ifc"

INTERVAL_FT = 100.0
START_STATION_FT = 10000.0


def _h_next(end, us):
    x = float(end[0, 3]) / us
    y = float(end[1, 3]) / us
    direction = math.atan2(float(end[1, 0]), float(end[0, 0]))
    return (x, y), direction


def _v_next(end, us):
    dist_along = float(end[0, 3]) / us
    start_height = float(end[1, 3]) / us
    start_grad = float(end[1, 0]) / float(end[0, 0])
    return dist_along, start_height, start_grad


def _station_label(dist_ft):
    sta = dist_ft + START_STATION_FT
    hundreds = int(sta // 100)
    remainder = sta % 100
    return f'{hundreds}+{remainder:05.2f}'


def add_linear_placements(ifc, alignment, h_curve, total_ft):
    """Create IfcReferent + IfcLinearPlacement at every INTERVAL_FT."""
    n = int(total_ft / INTERVAL_FT)
    referents = []
    for i in range(n + 1):
        dist_ft = float(i) * INTERVAL_FT
        if dist_ft > total_ft:
            break
        label = _station_label(dist_ft)
        pde = ifc.createIfcPointByDistanceExpression(
            DistanceAlong=ifc.createIfcLengthMeasure(dist_ft),
            BasisCurve=h_curve,
        )
        ax = ifc.create_entity('IfcAxis2PlacementLinear', Location=pde)
        lp = ifc.create_entity('IfcLinearPlacement', RelativePlacement=ax)
        ifcopenshell.api.alignment.update_fallback_position(ifc, lp)

        referent = ifcopenshell.api.root.create_entity(ifc, ifc_class='IfcReferent', name=label)
        referent.ObjectPlacement = lp
        referent.PredefinedType = 'STATION'

        prop = ifc.create_entity(
            'IfcPropertySingleValue',
            Name='Station',
            NominalValue=ifc.createIfcLengthMeasure(dist_ft + START_STATION_FT),
        )
        pset = ifc.create_entity(
            'IfcPropertySet',
            GlobalId=ifcopenshell.guid.new(),
            Name='Pset_Stationing',
            HasProperties=[prop],
        )
        ifc.create_entity(
            'IfcRelDefinesByProperties',
            GlobalId=ifcopenshell.guid.new(),
            RelatedObjects=[referent],
            RelatingPropertyDefinition=pset,
        )
        ifc.create_entity(
            'IfcRelPositions',
            GlobalId=ifcopenshell.guid.new(),
            RelatingPositioningElement=referent,
            RelatedProducts=[alignment],
        )
        referents.append(referent)

    ifc.create_entity(
        'IfcRelNests',
        GlobalId=ifcopenshell.guid.new(),
        RelatingObject=alignment,
        RelatedObjects=referents,
    )


def build():
    ifc = ifcopenshell.file(schema="IFC4X3_ADD2")
    ifc.header.file_description.description = ["ViewDefinition [Alignment-basedView]"]

    ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="FHWA Alignment")
    length = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")
    radian = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="PLANEANGLEUNIT")
    ifcopenshell.api.unit.assign_unit(ifc, units=[length, radian])

    model_context = ifcopenshell.api.context.add_context(ifc, context_type="Model")
    ifcopenshell.api.context.add_context(
        ifc,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=model_context,
    )

    site = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcSite", name="Site")
    project = ifc.by_type("IfcProject")[0]
    ifcopenshell.api.aggregate.assign_object(ifc, products=[site], relating_object=project)

    alignment = ifcopenshell.api.alignment.create(
        ifc, "E-Line", include_vertical=True, include_geometry=False, start_station=10000.
    )
    ifcopenshell.api.spatial.reference_structure(ifc, products=[alignment], relating_structure=site)

    us = ifcopenshell.util.unit.calculate_unit_scale(ifc)

    # --- Horizontal layout ---
    hlayout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    end = common.add_h_segment(ifc, hlayout, 0., 0., 1956.785654, "LINE",
                               start_point=(500., 2500.), start_direction=math.radians(327.0613))
    sp, sd = _h_next(end, us)
    end = common.add_h_segment(ifc, hlayout, 1000., 1000., 1919.222667, "CIRCULARARC",
                               start_point=sp, start_direction=sd)
    sp, sd = _h_next(end, us)
    end = common.add_h_segment(ifc, hlayout, 0., 0., 1886.905454, "LINE",
                               start_point=sp, start_direction=sd)
    sp, sd = _h_next(end, us)
    end = common.add_h_segment(ifc, hlayout, -1250., -1250., 1848.115835, "CIRCULARARC",
                               start_point=sp, start_direction=sd)
    sp, sd = _h_next(end, us)
    end = common.add_h_segment(ifc, hlayout, 0., 0., 1564.635765, "LINE",
                               start_point=sp, start_direction=sd)
    sp, sd = _h_next(end, us)
    end = common.add_h_segment(ifc, hlayout, -950., -950., 1049.119737, "CIRCULARARC",
                               start_point=sp, start_direction=sd)
    sp, sd = _h_next(end, us)
    common.add_h_segment(ifc, hlayout, 0., 0., 2112.285084, "LINE",
                         start_point=sp, start_direction=sd)

    # --- Vertical layout ---
    vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)

    end = common.add_v_segment(ifc, vlayout, 0., 1200., 100., 1.75/100., 1.75/100., "CONSTANTGRADIENT")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 1600., sh, sg, -1./100., "PARABOLICARC")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 1600., sh, sg, -1./100., "CONSTANTGRADIENT")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 1200., sh, sg, 2./100., "PARABOLICARC")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 800., sh, sg, 2./100., "CONSTANTGRADIENT")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 2000., sh, sg, -2./100., "PARABOLICARC")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 1000., sh, sg, -2./100., "CONSTANTGRADIENT")
    da, sh, sg = _v_next(end, us)
    end = common.add_v_segment(ifc, vlayout, da, 800., sh, sg, -0.5/100., "PARABOLICARC")
    da, sh, sg = _v_next(end, us)
    common.add_v_segment(ifc, vlayout, da, 2600., sh, sg, -0.5/100., "CONSTANTGRADIENT")

    ifcopenshell.api.alignment.create_representation(ifc, alignment)
    gradient_curve = ifcopenshell.api.alignment.get_curve(alignment)
    ifcopenshell.api.alignment.update_end_point(ifc, gradient_curve)

    # --- Linear placements every 100 ft ---
    h_curve = ifcopenshell.api.alignment.get_layout_curve(hlayout)
    total_ft = sum(
        abs(s.SegmentLength.wrappedValue)
        for s in h_curve.Segments
        if abs(s.SegmentLength.wrappedValue) > 0.0
    )
    add_linear_placements(ifc, alignment, h_curve, total_ft)

    dest = common.write_ifc(ifc, OUTPUT_DIR, OUTPUT_FILE)
    print(f"Written: {dest}")


if __name__ == "__main__":
    build()
