"""Generate combined horizontal + cant SVG plots.

For each cant CSV, finds the matching horizontal CSV by curve type and radius
labels, then produces a three-panel SVG:
  Top    — Horizontal plan view (X vs Y, equal aspect)
  Middle — Cant centerline elevation profile (dist_along vs Y)
  Bottom — Cross-slope angle phi = atan2(Axis_dz, Axis_dy) in radians

phi is the angle of the banked Axis vector measured from the cross-track
horizontal (Axis_dy axis).  When cant is zero the Axis points straight up and
phi = pi/2.  Increasing cant tilts the Axis toward positive Axis_dy, reducing
phi below pi/2.  Because the IFC cant representation always stores Axis_dy >= 0
regardless of curve hand, phi ranges between ~1.46 rad (full cant at 0.16 m /
1.5 m railhead distance) and pi/2 for every case.

Output goes to Alignment-plots/CantAlignment/{CantType}/.
"""
import csv
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt

CSV_ROOT    = Path(__file__).parent.parent / 'Alignment-reference-testset'
OUTPUT_ROOT = Path(__file__).parent.parent / 'Alignment-plots'

UNIT_LABEL = {
    'Meter':      'm',
    'SurveyFoot': 'US survey ft',
    'IntlFoot':   'ft',
}

# Map cant folder name → horizontal folder name
CANT_TO_HORIZ = {
    'ConstantCant':     'CircularArc',
    'LinearTransition': 'Clothoid',
    'BlossCurve':       'BlossCurve',
    'CosineCurve':      'CosineCurve',
    'HelmertCurve':     'HelmertCurve',
    'SineCurve':        'SineCurve',
    'VienneseBend':     'VienneseBend',
}


def read_csv(path: Path, *cols):
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    return tuple([float(r[c]) for r in rows] for c in cols)


def find_horizontal_csv(cant_csv: Path) -> Path:
    parts = cant_csv.stem.split('_')
    # stem: Cant_{CurveType}_{Length}_{StartR}_{EndR}_{Unit}
    cant_type  = parts[1]          # e.g. BlossCurve
    length     = parts[2]          # e.g. 100.0
    start_r    = parts[3]          # e.g. inf or -300
    end_r      = parts[4]          # e.g. 300 or -inf
    horiz_type = CANT_TO_HORIZ[cant_type]
    unit = parts[-1]
    stem = f'Horizontal_{horiz_type}_{length}_{start_r}_{end_r}_{unit}'
    return CSV_ROOT / 'HorizontalAlignment' / horiz_type / f'{stem}.csv'


def make_combined_plot(cant_csv: Path, horiz_csv: Path, dest: Path):
    horiz_x, horiz_y = read_csv(horiz_csv, 'X', 'Y')
    cant_d, cant_y, axis_dy, axis_dz = read_csv(
        cant_csv, 'dist_along', 'Y', 'Axis_dy', 'Axis_dz'
    )

    phi = [math.atan2(dz, dy) for dz, dy in zip(axis_dz, axis_dy)]

    cant_type  = cant_csv.parts[-2]
    horiz_type = horiz_csv.parts[-2]
    unit = UNIT_LABEL.get(cant_csv.stem.split('_')[-1], 'm')

    fig, (ax_h, ax_c, ax_p) = plt.subplots(3, 1, figsize=(8, 14))
    try:
        ax_h.plot(horiz_x, horiz_y, linewidth=1.5)
        ax_h.set_xlabel(f'X ({unit})')
        ax_h.set_ylabel(f'Y ({unit})')
        ax_h.set_title(f'Horizontal — {horiz_type}\n{horiz_csv.stem}', fontsize=8)
        ax_h.set_aspect('equal', adjustable='datalim')
        ax_h.grid(True, linestyle='--', alpha=0.5)

        ax_c.plot(cant_d, cant_y, linewidth=1.5, color='tab:orange')
        ax_c.set_xlabel(f'Distance Along ({unit})')
        ax_c.set_ylabel(f'Centerline Deviating Elevation ({unit})')
        ax_c.set_title(f'Cant — {cant_type}\n{cant_csv.stem}', fontsize=8)
        ax_c.grid(True, linestyle='--', alpha=0.5)

        ax_p.plot(cant_d, phi, linewidth=1.5, color='tab:green')
        ax_p.set_xlabel(f'Distance Along ({unit})')
        ax_p.set_ylabel('φ (rad)')
        ax_p.set_title(f'Cross-slope angle — {cant_type}\n{cant_csv.stem}', fontsize=8)
        ax_p.grid(True, linestyle='--', alpha=0.5)
        _to_deg = lambda x: x * (180.0 / math.pi)   # noqa: E731
        _to_rad = lambda x: x * (math.pi / 180.0)   # noqa: E731
        ax_p_deg = ax_p.secondary_yaxis('right', functions=(_to_deg, _to_rad))
        ax_p_deg.set_ylabel('φ (deg)')

        fig.tight_layout()
        dest.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(str(dest), format='svg', bbox_inches='tight')
    finally:
        plt.close(fig)


def main():
    cant_csvs = sorted(f for f in (CSV_ROOT / 'CantAlignment').rglob('*.csv')
                       if '3D' not in f.parts)
    print(f'Processing {len(cant_csvs)} cant files...')
    skipped = []
    written = []
    for cant_csv in cant_csvs:
        try:
            horiz_csv = find_horizontal_csv(cant_csv)
            if not horiz_csv.exists():
                raise FileNotFoundError(f'No matching horizontal CSV: {horiz_csv.name}')
            cant_type = cant_csv.parts[-2]
            dest = OUTPUT_ROOT / 'CantAlignment' / cant_type / cant_csv.with_suffix('.svg').name
            make_combined_plot(cant_csv, horiz_csv, dest)
            written.append(dest)
            print(f'  {dest.relative_to(OUTPUT_ROOT)}')
        except Exception as e:
            skipped.append((cant_csv.name, e))
            print(f'  SKIP {cant_csv.name}: {e}')
    print(f'\nWritten: {len(written)}  Skipped: {len(skipped)}')
    if skipped:
        for name, e in skipped:
            print(f'  {name}: {e}')
    print(f'Done. Plots written to {OUTPUT_ROOT.name}/')


if __name__ == '__main__':
    main()
