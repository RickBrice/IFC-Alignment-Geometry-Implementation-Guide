"""Generate reference coordinate CSV files from geometry IFC files.

Reads each IFC file from Alignment-geometry-testset/, evaluates the appropriate
alignment curve at 1 m horizontal intervals, and writes a CSV to the
corresponding path under Alignment-reference-testset/.

Columns by file type:
  Horizontal : dist_along, X, Y, RefDir_dx, RefDir_dy
  Vertical   : dist_along, Y, RefDir_dx, RefDir_dy
  Cant       : dist_along, Y, RefDir_dx, RefDir_dy, Axis_dy, Axis_dz

evaluate_segment is called for each real IfcCurveSegment with a local distance
(in metres) measured from the start of that segment.  The zero-length terminator
segment is excluded from all processing.

n_points is based on abs(total horizontal length in metres) so sampling is
always at 1 m intervals.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import ifcopenshell
import ifcopenshell.api.alignment as align_api
import ifcopenshell.util.unit

GEOMETRY_ROOT = Path(__file__).parent.parent / 'Alignment-geometry-testset'
CSV_ROOT      = Path(__file__).parent.parent / 'Alignment-reference-testset'


def get_real_segments(curve):
    """Return curve segments excluding the zero-length terminator."""
    return [s for s in curve.Segments if s.SegmentLength.wrappedValue != 0.0]


def evaluate_at(real_segs, d_m, unit_scale):
    """Evaluate the curve at global distance d_m (metres).

    Walks real_segs in order, accumulating abs(SegmentLength)*unit_scale as the
    boundary of each segment.  The last segment catches any point that falls
    exactly at the curve end.  Returns the 4x4 placement matrix from
    evaluate_segment (positions in metres, directions dimensionless).
    """
    cumulative_m = 0.0
    for i, seg in enumerate(real_segs):
        seg_len_m = abs(seg.SegmentLength.wrappedValue) * unit_scale
        if d_m <= cumulative_m + seg_len_m or i == len(real_segs) - 1:
            return align_api.evaluate_segment(seg, d_m - cumulative_m)
        cumulative_m += seg_len_m


def horizontal_n_points(alignment, unit_scale):
    """Return (h_curve, n_points) for the horizontal layout."""
    h_layout = align_api.get_horizontal_layout(alignment)
    h_curve = align_api.get_layout_curve(h_layout)
    real_segs = get_real_segments(h_curve)
    total_m = sum(abs(s.SegmentLength.wrappedValue) * unit_scale for s in real_segs)
    return h_curve, int(round(total_m)) + 1


def write_csv(dest, header, rows):
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def write_horizontal_csv(alignment, dest, unit_scale):
    h_curve, n_points = horizontal_n_points(alignment, unit_scale)
    real_segs = get_real_segments(h_curve)
    rows = []
    for i in range(n_points):
        d_m = float(i)
        m = evaluate_at(real_segs, d_m, unit_scale)
        dist = d_m / unit_scale
        x    = m[3, 0] / unit_scale
        y    = m[3, 1] / unit_scale
        rows.append([f'{dist:.6f}', f'{x:.6f}', f'{y:.6f}',
                     f'{m[0,0]:.6f}', f'{m[0,1]:.6f}'])
    write_csv(dest, ['dist_along', 'X', 'Y', 'RefDir_dx', 'RefDir_dy'], rows)


def write_vertical_csv(alignment, dest, unit_scale):
    _, n_points = horizontal_n_points(alignment, unit_scale)
    v_layout = align_api.get_vertical_layout(alignment)
    grad_curve = align_api.get_layout_curve(v_layout)
    real_segs = get_real_segments(grad_curve)
    rows = []
    for i in range(n_points):
        d_m = float(i)
        m = evaluate_at(real_segs, d_m, unit_scale)
        dist = m[3, 0] / unit_scale
        y    = m[3, 2] / unit_scale
        rows.append([f'{dist:.6f}', f'{y:.6f}', f'{m[0,0]:.6f}', f'{m[0,2]:.6f}'])
    write_csv(dest, ['dist_along', 'Y', 'RefDir_dx', 'RefDir_dy'], rows)


def write_cant_csv(alignment, dest, unit_scale):
    _, n_points = horizontal_n_points(alignment, unit_scale)
    c_layout = align_api.get_cant_layout(alignment)
    cant_curve = align_api.get_layout_curve(c_layout)
    real_segs = get_real_segments(cant_curve)
    rows = []
    for i in range(n_points):
        d_m = float(i)
        m = evaluate_at(real_segs, d_m, unit_scale)
        dist = d_m / unit_scale
        y    = m[3, 1] / unit_scale
        rows.append([
            f'{dist:.6f}',
            f'{y:.6f}',        # Y  — centreline deviating elevation (project units)
            f'{m[0,0]:.6f}',   # RefDir_dx — RefDirection x (dimensionless)
            f'{m[0,1]:.6f}',   # RefDir_dy — RefDirection y (dimensionless)
            f'{m[2,1]:.6f}',   # Axis_dy — banked Axis y component (dimensionless)
            f'{m[2,2]:.6f}',   # Axis_dz — banked Axis z component (dimensionless)
        ])
    write_csv(dest, ['dist_along', 'Y', 'RefDir_dx', 'RefDir_dy', 'Axis_dy', 'Axis_dz'], rows)


def process_file(src: Path):
    rel  = src.relative_to(GEOMETRY_ROOT)
    csv_name = rel.stem.removeprefix('Generated_') + '.csv'
    dest = CSV_ROOT / rel.parent / csv_name

    ifc = ifcopenshell.open(str(src))
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
    alignment = ifc.by_type('IfcAlignment')[0]

    top_dir = rel.parts[0]  # HorizontalAlignment, VerticalAlignment, CantAlignment

    if top_dir == 'VerticalAlignment':
        write_vertical_csv(alignment, dest, unit_scale)
    elif top_dir == 'CantAlignment':
        write_cant_csv(alignment, dest, unit_scale)
    else:
        write_horizontal_csv(alignment, dest, unit_scale)

    return dest


def main():
    ifc_files = sorted(GEOMETRY_ROOT.rglob('*.ifc'))
    print(f'Processing {len(ifc_files)} files...')
    skipped = []
    written = []
    for src in ifc_files:
        try:
            dest = process_file(src)
            written.append(dest)
            print(f'  {dest.relative_to(CSV_ROOT)}')
        except Exception as e:
            rel = src.relative_to(GEOMETRY_ROOT)
            skipped.append((rel, e))
            print(f'  SKIP {rel}: {e}')
    print(f'\nWritten: {len(written)}  Skipped: {len(skipped)}')
    if skipped:
        for rel, e in skipped:
            print(f'  {rel}: {e}')
    print(f'Done. CSV files written to {CSV_ROOT.name}/')


if __name__ == '__main__':
    main()
