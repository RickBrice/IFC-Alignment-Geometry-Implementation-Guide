# Headfake Models

This folder contains IFC models and the Python scripts that build them, created solely to produce publication figures for the *IFC Alignment Geometry Implementation Guide*.

## Why these models exist

The stringline examples in §10.6.1.4–§10.6.1.6 contain correct IFC structure — valid `IfcSectionedSurface` instances with tagged guide curves — but no IFC viewer is currently known to resolve `IfcOffsetCurveByDistances` guide curves when rendering a sectioned surface. Those files therefore cannot be rendered to show the expected output geometry.

The headfake models work around this limitation by achieving the correct *visual* result through dense template-based cross-sections rather than guide curve resolution. They are not valid demonstrations of the stringline mechanism; they are rendering props used to illustrate what a correctly-implemented viewer would produce.

Figures sourced from these models carry the caption note: *"This rendering has been synthesised to illustrate the correct geometry; no viewer capable of resolving stringline guide curves has been found at the time of writing."*

## Files

| IFC file | Script | Figure | Method |
|---|---|---|---|
| `IfcSectionedSurface_with_stringlines_guide_curves_as_alignments_headfake.ifc` | `Build_IfcSectionedSurface_with_stringlines_guide_curves_as_alignments_headfake.py` | Figure 10.6.1.4-1 | Three explicit cross-sections placed at 0 m, 100 m (peak width), and 200 m to define the variable-width shape directly |
| `IfcSectionedSurface_with_stringlines_headfake.ifc` | `Build_IfcSectionedSurface_with_stringlines_headfake.py` | Figure 10.6.1.6-2 | Cross-section widths computed analytically from the arc geometry at 1 cm spacing, producing a near-smooth surface edge |

## Important

Do not use these files as reference implementations of `IfcSectionedSurface` with guide curves. The corresponding reference implementations are in the parent `examples/` folder:

- `IfcSectionedSurface_with_stringlines_as_resource_entities.ifc` (§10.6.1.4)
- `IfcSectionedSurface_with_stringlines_guide_curves_as_alignments.ifc` (§10.6.1.5)
- `IfcSectionedSurface_with_stringlines_independent_edge_alignments.ifc` (§10.6.1.6)
