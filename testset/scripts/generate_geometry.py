"""Generate geometry IFC files by adding geometric representations to semantic IFC files.

Reads every IFC file under Alignment-semantic-testset/, adds geometry via
ifcopenshell.api.alignment.create_representation, and writes to the
corresponding path under Alignment-geometry-testset/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import ifcopenshell
import ifcopenshell.api.alignment as align_api

SEMANTIC_ROOT = Path(__file__).parent.parent / 'Alignment-semantic-testset'
GEOMETRY_ROOT = Path(__file__).parent.parent / 'Alignment-geometry-testset'


def process_file(src: Path):
    rel = src.relative_to(SEMANTIC_ROOT)
    dest = GEOMETRY_ROOT / rel.parent / f'Generated_{rel.name}'
    dest.parent.mkdir(parents=True, exist_ok=True)

    ifc = ifcopenshell.open(str(src))
    alignment = ifc.by_type('IfcAlignment')[0]

    align_api.create_representation(ifc, alignment)
    #align_api.util.print_composite_curve(align_api.get_basis_curve(alignment))

    ifc.write(str(dest))
    return dest


def main():
    ifc_files = sorted(SEMANTIC_ROOT.rglob('*.ifc'))
    total = len(ifc_files)
    skipped = []
    written = []
    print(f"Processing {total} files...")
    for src in ifc_files:
        try:
            dest = process_file(src)
            written.append(dest)
            print(f"  {dest.relative_to(GEOMETRY_ROOT)}")
        except Exception as e:
            rel = src.relative_to(SEMANTIC_ROOT)
            skipped.append((rel, e))
            print(f"  SKIP {rel}: {e}")
    print(f"\nWritten: {len(written)}  Skipped: {len(skipped)}")
    if skipped:
        print("Skipped files:")
        for rel, e in skipped:
            print(f"  {rel}: {e}")
    print(f"Done. Geometry files written to {GEOMETRY_ROOT.name}/")


if __name__ == '__main__':
    main()
