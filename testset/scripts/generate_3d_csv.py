"""Generate 3D alignment reference coordinate CSV files.

Two modes, selected by flag:

Default (no flag) — real-world alignments:
  Reads each IFC file from testset/real-world-alignments/, evaluates the 3D
  alignment curve, and writes a CSV alongside the IFC file.

  The evaluated curve is IfcSegmentedReferenceCurve when a cant layout is
  present, otherwise IfcGradientCurve.

  Default sampling (files without IfcLinearPlacement entities):
    function-step-type  = 1  (step-param is the minimum number of steps)
    function-step-param = 100  (100 intervals → 101 evenly-spaced points)
    evaluation_points() on the evaluator returns the sample distances.

  Linear-placement sampling (files in LINEAR_PLACEMENT_FILES):
    The CSV is evaluated only at the distances encoded in the
    IfcPointByDistanceExpression of each IfcLinearPlacement entity.

--testset flag — synthetic testset (VerticalAlignment and CantAlignment only):
  Reads each IFC file from Alignment-geometry-testset/VerticalAlignment/ and
  …/CantAlignment/, evaluates the appropriate 3D curve, and writes a 3D CSV
  to Alignment-reference-testset/{AlignmentType}/{CurveType}/3D/.

  Sampling matches generate_csv.py: 101 points at 0, 1, 2 … 100 m (SI),
  converted to project units in the output.  The sample count is derived from
  the horizontal layout length so the script is robust to non-100 m cases.

Columns (all length values in project units; directions are dimensionless):
  DistAlong     — distance along the curve from the start
  X, Y, Z       — position
  RefDir_dx/dy/dz  — forward tangent unit vector  (matrix row 0)
  Y_dx/dy/dz    — cross-track unit vector           (matrix row 1)
  Axis_dx/dy/dz — "up" axis unit vector             (matrix row 2)

Usage:
    python generate_3d_csv.py              # real-world alignments
    python generate_3d_csv.py --testset    # synthetic testset
"""
import argparse
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

IFC_ROOT      = Path(__file__).parent.parent / 'real-world-alignments'
GEOMETRY_ROOT = Path(__file__).parent.parent / 'Alignment-geometry-testset'
REFERENCE_ROOT = Path(__file__).parent.parent / 'Alignment-reference-testset'

# Per-file alignment name overrides for real-world alignments.
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

# Files whose CSV should be evaluated only at IfcLinearPlacement distances
# rather than the default uniform sampling.
LINEAR_PLACEMENT_FILES = {
    'FHWA_Alignment_with_Linear_Placement',
}


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


def _make_evaluator(curve):
    s = ifcopenshell.geom.settings()
    s.set('function-step-type', 1)
    s.set('function-step-param', 100.0)
    fi = ifcopenshell_wrapper.map_shape(s, curve.wrapped_data)
    ev = ifcopenshell_wrapper.function_item_evaluator(s, fi)
    return ev


def _eval_row(ev, d_m, unit_scale):
    """Evaluate at d_m (SI metres) and return a formatted CSV row."""
    raw = ev.evaluate(d_m)
    m = np.array(raw).reshape(4, 4).T
    dist = d_m / unit_scale
    x, y, z = m[3, 0] / unit_scale, m[3, 1] / unit_scale, m[3, 2] / unit_scale
    return [
        f'{dist:.6f}',
        f'{x:.6f}', f'{y:.6f}', f'{z:.6f}',
        f'{m[0,0]:.6f}', f'{m[0,1]:.6f}', f'{m[0,2]:.6f}',
        f'{m[1,0]:.6f}', f'{m[1,1]:.6f}', f'{m[1,2]:.6f}',
        f'{m[2,0]:.6f}', f'{m[2,1]:.6f}', f'{m[2,2]:.6f}',
    ]


def _write_csv(dest: Path, rows: list) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(rows)


def _linear_placement_distances_m(ifc, unit_scale):
    """Return sorted, deduplicated SI distances from all IfcLinearPlacement entities."""
    distances = set()
    for lp in ifc.by_type('IfcLinearPlacement'):
        try:
            pde = lp.RelativePlacement.Location
            distances.add(pde.DistanceAlong.wrappedValue * unit_scale)
        except AttributeError:
            continue
    return sorted(distances)


def process_realworld_file(src: Path):
    """Process a real-world alignment IFC file; write CSV alongside it."""
    ifc = ifcopenshell.open(str(src))
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)

    name = ALIGNMENT_NAME.get(src.stem)
    if name is not None:
        alignment = next(a for a in ifc.by_type('IfcAlignment') if a.Name == name)
    else:
        alignment = ifc.by_type('IfcAlignment')[0]

    ev = _make_evaluator(get_3d_curve(alignment))

    if src.stem in LINEAR_PLACEMENT_FILES:
        pts = _linear_placement_distances_m(ifc, unit_scale)
    else:
        pts = ev.evaluation_points()

    rows = [_eval_row(ev, d_m, unit_scale) for d_m in pts]

    dest = src.with_suffix('.csv')
    _write_csv(dest, rows)
    return dest, len(rows)


def process_testset_file(src: Path):
    """Process a synthetic testset IFC file; write 3D CSV to Alignment-reference-testset/.../3D/."""
    ifc = ifcopenshell.open(str(src))
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
    alignment = ifc.by_type('IfcAlignment')[0]

    ev = _make_evaluator(get_3d_curve(alignment))

    # Derive sample count from horizontal layout length (100 m → 101 points).
    h_layout = align_api.get_horizontal_layout(alignment)
    h_curve = align_api.get_layout_curve(h_layout)
    real_segs = [s for s in h_curve.Segments if s.SegmentLength.wrappedValue != 0.0]
    total_m = sum(abs(s.SegmentLength.wrappedValue) * unit_scale for s in real_segs)
    n_points = int(round(total_m)) + 1

    rows = [_eval_row(ev, float(i), unit_scale) for i in range(n_points)]

    rel = src.relative_to(GEOMETRY_ROOT)
    csv_name = rel.stem.removeprefix('Generated_') + '.csv'
    dest = REFERENCE_ROOT / rel.parent / '3D' / csv_name
    _write_csv(dest, rows)
    return dest, len(rows)


def _run(ifc_files, process_fn, label):
    print(f'Processing {len(ifc_files)} {label} files...')
    written, skipped = [], []
    for src in ifc_files:
        try:
            dest, n = process_fn(src)
            written.append(dest)
            print(f'  {dest.name}  ({n} rows)')
        except Exception as e:
            print(f'  SKIP {src.name}: {e}')
            skipped.append((src.name, e))
    print(f'\nWritten: {len(written)}  Skipped: {len(skipped)}')
    if skipped:
        for name, e in skipped:
            print(f'  {name}: {e}')
    print('Done.')


def main():
    parser = argparse.ArgumentParser(
        description='Generate 3D alignment reference coordinate CSV files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--testset', action='store_true',
        help=(
            'Generate 3D CSVs for the synthetic VerticalAlignment and CantAlignment '
            'testset files.  Output goes to Alignment-reference-testset/.../3D/. '
            'Default (no flag) processes real-world-alignments/ instead.'
        ),
    )
    args = parser.parse_args()

    if args.testset:
        ifc_files = sorted(
            f
            for sub in ('VerticalAlignment', 'CantAlignment')
            for f in (GEOMETRY_ROOT / sub).rglob('*.ifc')
        )
        _run(ifc_files, process_testset_file, 'synthetic testset')
    else:
        _run(sorted(IFC_ROOT.rglob('*.ifc')), process_realworld_file, 'real-world alignment')


if __name__ == '__main__':
    main()
