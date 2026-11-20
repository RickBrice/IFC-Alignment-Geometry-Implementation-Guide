# figures

This folder contains source IFC files and generation scripts for figures in the guide. These IFC files have been hand-edited to produce specific visual results and are not general-purpose alignment examples.

Generated SVG figures are written to the repository's `images/` directory.

## Structure

- `*.ifc` — Source IFC files used as input to the generation scripts
- `scripts/` — Python scripts that read the IFC files and produce SVG figures via matplotlib

## Scripts

| Script | Output figure |
|--------|--------------|
| `scripts/Figure_2.7.2-1_Helmert_Parent_Curves.py` | `images/Figure_2.7.2-1_Helmert_Parent_Curves.svg` |
| `scripts/Figure_2.7.2-2_Helmert_Parent_Curves_Placed.py` | `images/Figure_2.7.2-2_Helmert_Parent_Curves_Placed.svg` |
| `scripts/Figure_2.7.2-3_Helmert_Curve_Segments.py` | `images/Figure_2.7.2-3_Helmert_Curve_Segments.svg` |

## Dependencies

- [ifcopenshell](https://ifcopenshell.org/)
- [matplotlib](https://matplotlib.org/)
