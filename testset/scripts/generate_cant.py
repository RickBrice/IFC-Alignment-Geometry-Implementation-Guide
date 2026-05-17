"""Generate semantic-only IFC files for cant alignment test cases.

Each test case is generated in three unit systems: Meter, SurveyFoot, and IntlFoot.
Numeric labels in filenames are the metre-based case identifiers; only the unit
token changes. All dimensional values written to each IFC file are converted to
the file's declared project unit.

Every file contains three layouts:
  - Horizontal : matching curve type (see TRANSITION_CANT_TYPES)
  - Vertical   : single CONSTANTGRADIENT at 0 % grade, elevation 0.0 m
  - Cant       : the cant type under test

Note on VienneseBend: when generating geometry, cant segments must be created
before horizontal segments because horizontal geometry depends on cant parameters.
For semantic-only files (include_geometry=False), order is irrelevant.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import common
import cases_cant as cases
import ifcopenshell.api.alignment as align_api

OUTPUT_ROOT = Path(__file__).parent.parent / 'Alignment-semantic-testset' / 'CantAlignment'
L = cases.SEGMENT_LENGTH


def make_file(cant_type, h_type, folder_name, case, unit_system):
    scale = common.UNIT_SYSTEMS[unit_system]
    h_sr, h_er, h_sl, h_el, scl, ecl, scr, ecr = case
    filename = f"Cant_{folder_name}_{L:.1f}_{h_sl}_{h_el}_1_{unit_system}.ifc"
    ifc, alignment = common.setup(filename[:-4], include_vertical=True, include_cant=True,
                                  unit_system=unit_system)
    h_layout = align_api.get_horizontal_layout(alignment)
    v_layout = align_api.get_vertical_layout(alignment)
    c_layout = align_api.get_cant_layout(alignment)
    common.add_h_segment(ifc, h_layout, h_sr * scale, h_er * scale, L * scale, h_type)
    common.add_v_segment(ifc, v_layout, 0.0, L * scale, 0.0, 0.0, 0.0, 'CONSTANTGRADIENT')
    common.add_c_segment(ifc, c_layout, 0.0, L * scale,
                         scl * scale, ecl * scale, scr * scale, ecr * scale, cant_type)
    dest = common.write_ifc(ifc, OUTPUT_ROOT / folder_name, filename)
    print(f"  {dest.name}")


def main():
    for unit_system in common.UNIT_SYSTEMS:
        print(f"\nCant [{unit_system}]: ConstantCant")
        for case in cases.CONSTANT_CANT_CASES:
            make_file('CONSTANTCANT', 'CIRCULARARC', 'ConstantCant', case, unit_system)

        for cant_type, h_type, folder_name in cases.TRANSITION_CANT_TYPES:
            print(f"Cant [{unit_system}]: {folder_name}")
            case_list = (cases.VIENNESEBEND_CANT_CASES if cant_type == 'VIENNESEBEND'
                         else cases.TRANSITION_CANT_CASES)
            for case in case_list:
                make_file(cant_type, h_type, folder_name, case, unit_system)


if __name__ == '__main__':
    main()
