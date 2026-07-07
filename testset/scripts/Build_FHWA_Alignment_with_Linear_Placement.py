# Author: Richard Brice, PE
# Date: 2026-07-07
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Identical to Build_FHWA_Alignment.py plus one IfcReferent + IfcLinearPlacement per 100 ft
# station (100+00 through 223+00, 124 stations total). Each placement carries a Pset_Stationing
# property set with the station value and a CartesianPosition fallback computed via
# ifcopenshell.api.alignment.update_fallback_position. IfcPointByDistanceExpression.BasisCurve
# is the alignment's IfcGradientCurve (not the 2D horizontal composite curve), so evaluated
# positions carry the true 3D (graded) elevation.
# Output: testset/real-world-alignments/FHWA_Alignment_with_Linear_Placement.ifc
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import common
import FHWA_common
import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.root
import ifcopenshell.guid

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "real-world-alignments"
OUTPUT_FILE = "FHWA_Alignment_with_Linear_Placement.ifc"

INTERVAL_FT = 100.0
START_STATION_FT = FHWA_common.START_STATION_FT


def _station_label(dist_ft):
    sta = dist_ft + START_STATION_FT
    hundreds = int(sta // 100)
    remainder = sta % 100
    return f'{hundreds}+{remainder:05.2f}'


def add_linear_placements(ifc, alignment, basis_curve, total_ft):
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
            BasisCurve=basis_curve,
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
    ifc, alignment = FHWA_common.setup_eline_project()
    FHWA_common.build_eline_layout(ifc, alignment)

    # --- Linear placements every 100 ft ---
    # BasisCurve is the 3D alignment curve (IfcGradientCurve), per Chapter 8 section 8.2.1:
    # DistanceAlong is measured along its horizontal projection, so IfcPointByDistanceExpression
    # locates the point using the curve's horizontal projection for distance and its true 3D
    # geometry (including grade) for the resulting position -- unlike a 2D horizontal composite
    # curve, which cannot carry any elevation.
    hlayout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    h_curve = ifcopenshell.api.alignment.get_layout_curve(hlayout)
    gradient_curve = ifcopenshell.api.alignment.get_curve(alignment)
    total_ft = sum(
        abs(s.SegmentLength.wrappedValue)
        for s in h_curve.Segments
        if abs(s.SegmentLength.wrappedValue) > 0.0
    )
    add_linear_placements(ifc, alignment, gradient_curve, total_ft)

    dest = common.write_ifc(ifc, OUTPUT_DIR, OUTPUT_FILE)
    print(f"Written: {dest}")


if __name__ == "__main__":
    build()
