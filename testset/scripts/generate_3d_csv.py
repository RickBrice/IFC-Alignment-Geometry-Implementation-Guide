"""Generate 3D alignment reference coordinate CSV files.

For each IFC file in testset/3D/, evaluates the 3D alignment curve at
50-project-unit intervals and writes a CSV alongside the IFC file.

The evaluated curve is IfcSegmentedReferenceCurve when a cant layout is
present, otherwise IfcGradientCurve.

ifcopenshell's function-step settings control the sample spacing:
  function-step-type  = 1  (step-param is the minimum number of steps)
  function-step-param = 100  (100 intervals → 101 evenly-spaced evaluation points)

evaluation_points() on the evaluator returns the list of sample distances
in metres; each is passed to evaluate() to obtain the 4x4 placement matrix.

Columns (all length values in project units; directions are dimensionless):
  DistAlong   — distance along the curve from the start
  X, Y, Z     — position
  RefDir_dx/dy/dz — forward tangent unit vector  (matrix row 0)
  Y_dx/dy/dz  — cross-track unit vector           (matrix row 1)
  Axis_dx/dy/dz — "up" axis unit vector           (matrix row 2)
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import ifcopenshell
import ifcopenshell.geom
from ifcopenshell import ifcopenshell_wrapper
import ifcopenshell.api.alignment as align_api
import ifcopenshell.util.unit

IFC_ROOT = Path(__file__).parent.parent / 'RealWorldAlignments'

# Per-file alignment name overrides.  Maps stem → alignment Name attribute.
# Files with a single alignment do not need an entry here.
ALIGNMENT_NAME = {
    'BPaimio-Kupittaa_GK23_N2000_2020': '001',
}

HEADER = [
    'DistAlong',
    'X', 'Y', 'Z',
    'RefDir_dx', 'RefDir_dy', 'RefDir_dz',
    'Y_dx', 'Y_dy', 'Y_dz',
    'Axis_dx', 'Axis_dy', 'Axis_dz',
]


def get_3d_curve(alignment):
    """Return the best available 3D curve for this alignment.

    Prefers IfcSegmentedReferenceCurve (horizontal + vertical + cant) when a
    cant layout is present; falls back to IfcGradientCurve (horizontal +
    vertical) otherwise.
    """
    cant_layout = align_api.get_cant_layout(alignment)
    if cant_layout is not None:
        return align_api.get_layout_curve(cant_layout)
    v_layout = align_api.get_vertical_layout(alignment)
    return align_api.get_layout_curve(v_layout)


def process_file(src: Path):
    ifc = ifcopenshell.open(str(src))
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)

    name = ALIGNMENT_NAME.get(src.stem)
    if name is not None:
        alignment = next(a for a in ifc.by_type('IfcAlignment') if a.Name == name)
    else:
        alignment = ifc.by_type('IfcAlignment')[0]

    curve = get_3d_curve(alignment)

    s = ifcopenshell.geom.settings()
    s.set('function-step-type', 1)   # 1 = minimum number of steps
    s.set('function-step-param', 100.0)

    fi = ifcopenshell_wrapper.map_shape(s, curve.wrapped_data)
    ev = ifcopenshell_wrapper.function_item_evaluator(s, fi)

    pts = ev.evaluation_points()

    rows = []
    for d_m in pts:
        raw = ev.evaluate(d_m)
        m = np.array(raw).reshape(4, 4).T
        dist = d_m / unit_scale
        x, y, z = m[3, 0] / unit_scale, m[3, 1] / unit_scale, m[3, 2] / unit_scale
        rows.append([
            f'{dist:.6f}',
            f'{x:.6f}', f'{y:.6f}', f'{z:.6f}',
            f'{m[0,0]:.6f}', f'{m[0,1]:.6f}', f'{m[0,2]:.6f}',
            f'{m[1,0]:.6f}', f'{m[1,1]:.6f}', f'{m[1,2]:.6f}',
            f'{m[2,0]:.6f}', f'{m[2,1]:.6f}', f'{m[2,2]:.6f}',
        ])

    dest = src.with_suffix('.csv')
    with dest.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)

    return dest, len(rows)


def main():
    ifc_files = sorted(IFC_ROOT.rglob('*.ifc'))
    print(f'Processing {len(ifc_files)} files...')
    for src in ifc_files:
        try:
            dest, n = process_file(src)
            print(f'  {dest.name}  ({n} rows)')
        except Exception as e:
            print(f'  SKIP {src.name}: {e}')
    print('Done.')


if __name__ == '__main__':
    main()
