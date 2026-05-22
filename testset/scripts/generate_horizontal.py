"""Generate semantic-only IFC files for horizontal alignment test cases.

Each test case is generated in three unit systems: Meter, SurveyFoot, and IntlFoot.
Numeric labels in filenames (length, radii) are the metre-based case identifiers;
only the unit token at the end of the filename changes. All dimensional values
written to each IFC file are converted to the file's declared project unit.

VienneseBend horizontal files include vertical and cant layouts (identical structure
to the cant VienneseBend files) because VienneseBend geometry requires cant parameters.
This ensures geometry generation, CSV extraction, and plots all work uniformly.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import common
import cases_horizontal as cases
import cases_cant as cant_cases
import ifcopenshell.api.alignment as align_api

OUTPUT_ROOT = Path(__file__).parent.parent / 'Alignment-semantic-testset' / 'HorizontalAlignment'
L = cases.SEGMENT_LENGTH


def make_file(curve_type, start_r, end_r, start_label, end_label, unit_system):
    scale  = common.UNIT_SYSTEMS[unit_system]
    folder = common.CURVE_FOLDER[curve_type]
    filename = f"Horizontal_{folder}_{L:.1f}_{start_label}_{end_label}_{unit_system}.ifc"
    ifc, alignment = common.setup(filename[:-4], unit_system=unit_system)
    h_layout = align_api.get_horizontal_layout(alignment)
    common.add_h_segment(ifc, h_layout, start_r * scale, end_r * scale, L * scale, curve_type)
    dest = common.write_ifc(ifc, OUTPUT_ROOT / folder, filename)
    print(f"  {dest.name}")


def make_viennesebend_file(case, unit_system):
    """VienneseBend requires cant parameters for geometry; include all three layouts."""
    scale = common.UNIT_SYSTEMS[unit_system]
    h_sr, h_er, h_sl, h_el, scl, ecl, scr, ecr = case
    filename = f"Horizontal_VienneseBend_{L:.1f}_{h_sl}_{h_el}_{unit_system}.ifc"
    ifc, alignment = common.setup(filename[:-4], include_vertical=True, include_cant=True,
                                  unit_system=unit_system)
    h_layout = align_api.get_horizontal_layout(alignment)
    v_layout = align_api.get_vertical_layout(alignment)
    c_layout = align_api.get_cant_layout(alignment)
    common.add_c_segment(ifc, c_layout, 0.0, L * scale,
                         scl * scale, ecl * scale, scr * scale, ecr * scale, 'VIENNESEBEND')
    common.add_v_segment(ifc, v_layout, 0.0, L * scale, 0.0, 0.0, 0.0, 'CONSTANTGRADIENT')
    common.add_h_segment(ifc, h_layout, h_sr * scale, h_er * scale, L * scale, 'VIENNESEBEND')
    dest = common.write_ifc(ifc, OUTPUT_ROOT / 'VienneseBend', filename)
    print(f"  {dest.name}")


def main():
    for unit_system in common.UNIT_SYSTEMS:
        print(f"\nHorizontal [{unit_system}]: Line")
        for start_r, end_r, sl, el in cases.LINE_CASES:
            make_file('LINE', start_r, end_r, sl, el, unit_system)

        print(f"Horizontal [{unit_system}]: CircularArc")
        for start_r, end_r, sl, el in cases.CIRCULAR_ARC_CASES:
            make_file('CIRCULARARC', start_r, end_r, sl, el, unit_system)

        for curve_type in cases.TRANSITION_TYPES:
            print(f"Horizontal [{unit_system}]: {common.CURVE_FOLDER[curve_type]}")
            for start_r, end_r, sl, el in cases.TRANSITION_CASES:
                make_file(curve_type, start_r, end_r, sl, el, unit_system)

        print(f"Horizontal [{unit_system}]: VienneseBend")
        for case in cant_cases.VIENNESEBEND_CANT_CASES:
            make_viennesebend_file(case, unit_system)


if __name__ == '__main__':
    main()
