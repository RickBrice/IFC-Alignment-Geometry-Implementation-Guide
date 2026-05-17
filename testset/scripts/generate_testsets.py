"""Generate all alignment testset outputs from scratch.

Deletes and recreates all four output directories, then runs each generation
stage in order:

  Semantic IFC   — semantic-only IFC files   (generate_horizontal/vertical/cant)
  Geometry IFC   — geometry IFC files        (generate_geometry)
  Reference CSVs — coordinate samples        (generate_csv)
  Plots   — SVG plots                 (generate_plots, generate_combined_plots)
"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import generate_horizontal
import generate_vertical
import generate_cant
import generate_geometry
import generate_csv
import generate_plots
import generate_combined_plots

TESTSET_ROOT = Path(__file__).parent.parent

OUTPUT_DIRS = [
    TESTSET_ROOT / 'Alignment-semantic-testset',
    TESTSET_ROOT / 'Alignment-geometry-testset',
    TESTSET_ROOT / 'Alignment-reference-testset',
    TESTSET_ROOT / 'Alignment-plots',
]


def clean():
    for d in OUTPUT_DIRS:
        if d.exists():
            shutil.rmtree(d)
            print(f"  Deleted {d.name}/")


def section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():
    section("Cleaning output directories")
    clean()

    section("Semantic IFC")
    generate_horizontal.main()
    generate_vertical.main()
    generate_cant.main()

    section("Geometry IFC")
    generate_geometry.main()

    section("Reference CSVs")
    generate_csv.main()

    section("Plots")
    generate_plots.main()
    generate_combined_plots.main()

    print()
    print("=" * 60)
    print("Done.")
    print("=" * 60)


if __name__ == '__main__':
    main()
