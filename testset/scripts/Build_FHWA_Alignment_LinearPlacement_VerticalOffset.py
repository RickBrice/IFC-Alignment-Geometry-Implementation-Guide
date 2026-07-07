# Author: Richard Brice, PE
# Date: 2026-07-07
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Same E-Line alignment as Build_FHWA_Alignment_with_Linear_Placement.py, at the same 124
# 100 ft stations, but instead of a single plain placement per station, each station gets four
# IfcReferent + IfcLinearPlacement variants that all target the same intended vertical shift
# (+/-2.5 project units) via the two mechanisms contrasted in Chapter 8, section 8.3.3:
#   - OffsetVertical = +2.5   (perpendicular to the curve's tangent -- NOT a pure elevation shift)
#   - OffsetVertical = -2.5
#   - PlacementRelTo -> shared IfcLocalPlacement at z=+2.5, OffsetVertical omitted (true elevation shift)
#   - PlacementRelTo -> shared IfcLocalPlacement at z=-2.5, OffsetVertical omitted
# CartesianPosition fallback is populated via update_fallback_position for all four variants.
# update_fallback_position resolves the full placement chain (including PlacementRelTo), so
# the fallback for the PlacementRelTo variants matches their fully resolved placement. This
# file was originally built while that function ignored PlacementRelTo, to serve as a
# regression check for the fix; it continues to serve that purpose.
# Output: testset/real-world-alignments/FHWA_Alignment_LinearPlacement_VerticalOffset.ifc
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
OUTPUT_FILE = "FHWA_Alignment_LinearPlacement_VerticalOffset.ifc"

INTERVAL_FT = 100.0
START_STATION_FT = FHWA_common.START_STATION_FT
VERTICAL_OFFSET = 2.5  # project units (ft); matches the worked example in Chapter 8 section 8.3.3


def _station_label(dist_ft):
    sta = dist_ft + START_STATION_FT
    hundreds = int(sta // 100)
    remainder = sta % 100
    return f'{hundreds}+{remainder:05.2f}'


def _make_local_placement(ifc, z):
    """A shared IfcLocalPlacement offset by z (project units) along global Z, reused by every
    PlacementRelTo variant so all stations shift relative to the same frame (mirrors the
    #5139-series entities in the Chapter 8 section 8.3.3 example)."""
    point = ifc.create_entity('IfcCartesianPoint', Coordinates=(0., 0., z))
    axis = ifc.create_entity('IfcDirection', DirectionRatios=(0., 0., 1.))
    ref_direction = ifc.create_entity('IfcDirection', DirectionRatios=(1., 0., 0.))
    placement3d = ifc.create_entity(
        'IfcAxis2Placement3D', Location=point, Axis=axis, RefDirection=ref_direction
    )
    return ifc.create_entity('IfcLocalPlacement', RelativePlacement=placement3d)


def _add_referent(ifc, alignment, dist_ft, label, lp, referents):
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


def add_test_placements(ifc, alignment, basis_curve, total_ft):
    """Create the 4 OffsetVertical/PlacementRelTo variants at every INTERVAL_FT."""
    prt_pos = _make_local_placement(ifc, VERTICAL_OFFSET)
    prt_neg = _make_local_placement(ifc, -VERTICAL_OFFSET)

    n = int(total_ft / INTERVAL_FT)
    referents = []
    for i in range(n + 1):
        dist_ft = float(i) * INTERVAL_FT
        if dist_ft > total_ft:
            break
        label = _station_label(dist_ft)

        pde = ifc.createIfcPointByDistanceExpression(
            DistanceAlong=ifc.createIfcLengthMeasure(dist_ft),
            OffsetVertical=VERTICAL_OFFSET,
            BasisCurve=basis_curve,
        )
        ax = ifc.create_entity('IfcAxis2PlacementLinear', Location=pde)
        lp = ifc.create_entity('IfcLinearPlacement', RelativePlacement=ax)
        ifcopenshell.api.alignment.update_fallback_position(ifc, lp)
        _add_referent(ifc, alignment, dist_ft, f'{label} OffsetVertical+2.5', lp, referents)

        pde = ifc.createIfcPointByDistanceExpression(
            DistanceAlong=ifc.createIfcLengthMeasure(dist_ft),
            OffsetVertical=-VERTICAL_OFFSET,
            BasisCurve=basis_curve,
        )
        ax = ifc.create_entity('IfcAxis2PlacementLinear', Location=pde)
        lp = ifc.create_entity('IfcLinearPlacement', RelativePlacement=ax)
        ifcopenshell.api.alignment.update_fallback_position(ifc, lp)
        _add_referent(ifc, alignment, dist_ft, f'{label} OffsetVertical-2.5', lp, referents)

        pde = ifc.createIfcPointByDistanceExpression(
            DistanceAlong=ifc.createIfcLengthMeasure(dist_ft),
            BasisCurve=basis_curve,
        )
        ax = ifc.create_entity('IfcAxis2PlacementLinear', Location=pde)
        lp = ifc.create_entity('IfcLinearPlacement', PlacementRelTo=prt_pos, RelativePlacement=ax)
        ifcopenshell.api.alignment.update_fallback_position(ifc, lp)
        _add_referent(ifc, alignment, dist_ft, f'{label} PlacementRelTo+2.5', lp, referents)

        pde = ifc.createIfcPointByDistanceExpression(
            DistanceAlong=ifc.createIfcLengthMeasure(dist_ft),
            BasisCurve=basis_curve,
        )
        ax = ifc.create_entity('IfcAxis2PlacementLinear', Location=pde)
        lp = ifc.create_entity('IfcLinearPlacement', PlacementRelTo=prt_neg, RelativePlacement=ax)
        ifcopenshell.api.alignment.update_fallback_position(ifc, lp)
        _add_referent(ifc, alignment, dist_ft, f'{label} PlacementRelTo-2.5', lp, referents)

    ifc.create_entity(
        'IfcRelNests',
        GlobalId=ifcopenshell.guid.new(),
        RelatingObject=alignment,
        RelatedObjects=referents,
    )


def build():
    ifc, alignment = FHWA_common.setup_eline_project()
    FHWA_common.build_eline_layout(ifc, alignment)

    # BasisCurve is the 3D alignment curve (IfcGradientCurve), per Chapter 8 section 8.2.1 --
    # DistanceAlong is measured along its horizontal projection, but evaluating a point on it
    # (and hence OffsetVertical) reflects the true 3D (graded) tangent, unlike the 2D horizontal
    # composite curve alone.
    hlayout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    h_curve = ifcopenshell.api.alignment.get_layout_curve(hlayout)
    gradient_curve = ifcopenshell.api.alignment.get_curve(alignment)
    total_ft = sum(
        abs(s.SegmentLength.wrappedValue)
        for s in h_curve.Segments
        if abs(s.SegmentLength.wrappedValue) > 0.0
    )
    add_test_placements(ifc, alignment, gradient_curve, total_ft)

    dest = common.write_ifc(ifc, OUTPUT_DIR, OUTPUT_FILE)
    print(f"Written: {dest}")


if __name__ == "__main__":
    build()
