"""Generate SVG plots from reference coordinate CSV files.

Reads each CSV from Alignment-reference-testset/ and writes a matching SVG plot
to Alignment-plots/, mirroring the subdirectory structure.

  Horizontal : X vs Y  (equal aspect — curve shape is geometrically accurate)
  Vertical   : dist_along vs Y  (elevation profile)
  Cant       : dist_along vs Y  (centreline elevation from cant)
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt

CSV_ROOT   = Path(__file__).parent.parent / 'Alignment-reference-testset'
PLOTS_ROOT = Path(__file__).parent.parent / 'Alignment-plots'

# Unit token at end of filename stem → axis unit label
UNIT_LABELS = {
    'Meter':      'm',
    'SurveyFoot': 'survey ft',
    'IntlFoot':       'ft',
}


def _unit_label(stem: str) -> str:
    for token, label in UNIT_LABELS.items():
        if stem.endswith(f'_{token}'):
            return label
    return 'm'


def _axis_labels(top_dir: str, unit: str):
    if top_dir == 'HorizontalAlignment':
        return (f'X ({unit})', f'Y ({unit})')
    if top_dir == 'VerticalAlignment':
        return (f'Distance Along ({unit})', f'Elevation ({unit})')
    return (f'Distance Along ({unit})', f'Centreline Elevation ({unit})')


def plot_csv(src: Path):
    top_dir = src.relative_to(CSV_ROOT).parts[0]
    unit = _unit_label(src.stem)
    xlabel, ylabel = _axis_labels(top_dir, unit)

    with src.open(newline='') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if top_dir == 'HorizontalAlignment':
        x = [float(r['X']) for r in rows]
        y = [float(r['Y']) for r in rows]
    else:
        x = [float(r['dist_along']) for r in rows]
        y = [float(r['Y']) for r in rows]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(x, y, linewidth=1.5)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(src.stem, fontsize=9)
    ax.grid(True, linestyle='--', alpha=0.5)

    if top_dir == 'HorizontalAlignment':
        ax.set_aspect('equal', adjustable='datalim')

    rel = src.relative_to(CSV_ROOT)
    dest = PLOTS_ROOT / rel.with_suffix('.svg')
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(str(dest), format='svg', bbox_inches='tight')
    plt.close(fig)
    return dest


def main():
    csv_files = sorted(CSV_ROOT.rglob('*.csv'))
    # CantAlignment plots are handled by generate_combined_plots.py (two-panel)
    csv_files = [f for f in csv_files
                 if f.relative_to(CSV_ROOT).parts[0] != 'CantAlignment']
    print(f'Plotting {len(csv_files)} files...')
    skipped = []
    written = []
    for src in csv_files:
        try:
            dest = plot_csv(src)
            written.append(dest)
            root = CSV_ROOT if dest.is_relative_to(CSV_ROOT) else PLOTS_ROOT
            print(f'  {dest.relative_to(root)}')
        except Exception as e:
            rel = src.relative_to(CSV_ROOT)
            skipped.append((rel, e))
            print(f'  SKIP {rel}: {e}')
    print(f'\nWritten: {len(written)}  Skipped: {len(skipped)}')
    if skipped:
        for rel, e in skipped:
            print(f'  {rel}: {e}')
    print(f'Done.')


if __name__ == '__main__':
    main()
