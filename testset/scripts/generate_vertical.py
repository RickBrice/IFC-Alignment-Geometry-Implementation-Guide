"""Generate semantic-only IFC files for vertical alignment test cases.

Each test case is generated in three unit systems: Meter, SurveyFoot, and IntlFoot.
Numeric labels in filenames are the metre-based case identifiers; only the unit
token changes. All dimensional values written to each IFC file are converted to
the file's declared project unit.

Gradients are dimensionless percentage values and are not converted.

The horizontal layout for every vertical test is a straight LINE due East,
with the same length as the vertical segment.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import common
import cases_vertical as cases
import ifcopenshell.api.alignment as align_api

OUTPUT_ROOT = Path(__file__).parent.parent / 'Alignment-semantic-testset' / 'VerticalAlignment'
L  = cases.SEGMENT_LENGTH
H0 = cases.START_HEIGHT


def make_file(v_type, start_g, end_g, start_label, end_label, unit_system):
    scale  = common.UNIT_SYSTEMS[unit_system]
    folder = common.CURVE_FOLDER[v_type]
    filename = f"Vertical_{folder}_{L:.1f}_{H0:.1f}_{start_label}_{end_label}_{unit_system}.ifc"
    ifc, alignment = common.setup(filename[:-4], include_vertical=True,
                                  unit_system=unit_system)
    h_layout = align_api.get_horizontal_layout(alignment)
    v_layout = align_api.get_vertical_layout(alignment)
    common.add_h_segment(ifc, h_layout, 0.0, 0.0, L * scale, 'LINE')
    # start_g / end_g are percentage gradients — dimensionless, not scaled
    common.add_v_segment(ifc, v_layout, 0.0, L * scale, H0 * scale,
                         start_g / 100.0, end_g / 100.0, v_type)
    dest = common.write_ifc(ifc, OUTPUT_ROOT / folder, filename)
    print(f"  {dest.name}")


def main():
    for unit_system in common.UNIT_SYSTEMS:
        print(f"\nVertical [{unit_system}]: ConstantGradient")
        for sg, eg, sl, el in cases.CONSTANT_GRADIENT_CASES:
            make_file('CONSTANTGRADIENT', sg, eg, sl, el, unit_system)

        for v_type in ('PARABOLICARC', 'CIRCULARARC'):
            print(f"Vertical [{unit_system}]: {common.CURVE_FOLDER[v_type]}")
            for sg, eg, sl, el in cases.VERTICAL_TRANSITION_CASES:
                make_file(v_type, sg, eg, sl, el, unit_system)


if __name__ == '__main__':
    main()
