# Author: Richard Brice, PE
# Date: 2026-07-07
# This script produces an example IFC model for the IFC Alignment Geometry Implementation Guide.
#
# Builds the E-Line alignment from Appendix B of the FHWA Bridge Geometry Manual.
# Horizontal layout: 7 segments (LINE and CIRCULARARC, ~12,337 ft total).
# Vertical layout: 9 segments (CONSTANTGRADIENT and PARABOLICARC).
# Units: international foot. Start station: 100+00.
# Output: testset/real-world-alignments/FHWA_Alignment.ifc
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import common
import FHWA_common

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "real-world-alignments"
OUTPUT_FILE = "FHWA_Alignment.ifc"


def build():
    ifc, alignment = FHWA_common.setup_eline_project()
    FHWA_common.build_eline_layout(ifc, alignment)

    dest = common.write_ifc(ifc, OUTPUT_DIR, OUTPUT_FILE)
    print(f"Written: {dest}")


if __name__ == "__main__":
    build()
