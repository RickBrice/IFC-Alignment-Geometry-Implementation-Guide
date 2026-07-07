# Author: Richard Brice, PE
# Date: 2026-07-07
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Generates the reference CSV for FHWA_Alignment_LinearPlacement_VerticalOffset.ifc.
#
# Unlike generate_3d_csv.py's LINEAR_PLACEMENT_FILES handling (which only reads DistanceAlong
# and re-evaluates the bare basis curve, ignoring offsets), this script evaluates each
# IfcLinearPlacement's fully resolved placement -- including OffsetVertical and, for the
# PlacementRelTo variants, the nested local placement -- via
# ifcopenshell.util.placement.get_local_placement(). That function recurses through
# PlacementRelTo and, for an IfcPointByDistanceExpression Location, delegates to the geometry
# kernel with convert-back-units=True, so the returned matrix is already in project units.
#
# Long format: one row per IfcReferent (four rows per station -- OffsetVertical+2.5,
# OffsetVertical-2.5, PlacementRelTo+2.5, PlacementRelTo-2.5), identified by a Variant column.
# Columns match generate_3d_csv.py's 13-column layout (DistAlong, X, Y, Z, RefDir_dx/dy/dz,
# Y_dx/dy/dz, Axis_dx/dy/dz) with Variant inserted after DistAlong.
# Output: testset/real-world-alignments/FHWA_Alignment_LinearPlacement_VerticalOffset.csv
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import ifcopenshell
import ifcopenshell.util.placement

IFC_PATH = Path(__file__).resolve().parent.parent / "real-world-alignments" / "FHWA_Alignment_LinearPlacement_VerticalOffset.ifc"
CSV_PATH = IFC_PATH.with_suffix(".csv")

HEADER = [
    "DistAlong", "Variant",
    "X", "Y", "Z",
    "RefDir_dx", "RefDir_dy", "RefDir_dz",
    "Y_dx", "Y_dy", "Y_dz",
    "Axis_dx", "Axis_dy", "Axis_dz",
]


def main():
    ifc = ifcopenshell.open(str(IFC_PATH))

    rows = []
    for referent in ifc.by_type("IfcReferent"):
        if " " not in referent.Name:
            # Skip the single start-station referent auto-created by
            # ifcopenshell.api.alignment.create(start_station=...); it has no variant suffix.
            continue
        label, variant = referent.Name.split(" ", 1)
        lp = referent.ObjectPlacement
        dist_along = lp.RelativePlacement.Location.DistanceAlong.wrappedValue

        m = ifcopenshell.util.placement.get_local_placement(lp)

        rows.append([
            f"{dist_along:.6f}", variant,
            f"{m[0, 3]:.6f}", f"{m[1, 3]:.6f}", f"{m[2, 3]:.6f}",
            f"{m[0, 0]:.6f}", f"{m[1, 0]:.6f}", f"{m[2, 0]:.6f}",
            f"{m[0, 1]:.6f}", f"{m[1, 1]:.6f}", f"{m[2, 1]:.6f}",
            f"{m[0, 2]:.6f}", f"{m[1, 2]:.6f}", f"{m[2, 2]:.6f}",
        ])

    with CSV_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print(f"Written: {CSV_PATH}  ({len(rows)} rows)")


if __name__ == "__main__":
    main()
