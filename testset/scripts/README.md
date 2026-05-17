# Testset Scripts

Python scripts that generate the alignment testset from scratch. All output is derived
data — the scripts are the source of truth.

## Overview

The scripts form a four-stage pipeline. Each stage reads from the previous stage's
output:

```
cases_*.py  ──►  generate_{horizontal,vertical,cant}.py  ──►  Alignment-semantic-testset/
                                                                        │
                                          generate_geometry.py  ◄───────┘
                                                   │
                                           Alignment-geometry-testset/
                                                   │
                                          generate_csv.py  ◄────────────┘
                                                   │
                                           Alignment-reference-testset/
                                                   │
                              ┌────────────────────┤
                              ▼                    ▼
                    generate_plots.py    generate_combined_plots.py
                              │                    │
                    SVGs alongside CSVs    Alignment-plots/
                    + Alignment-plots/
                      VerticalAlignment/
```

## Entry point

### `generate_testsets.py`

Runs the complete pipeline in one shot. Deletes all four output directories first so
the result is always a clean regeneration.

```
python scripts/generate_testsets.py
```

Stage order:

1. `generate_horizontal.main()`
2. `generate_vertical.main()`
3. `generate_cant.main()`
4. `generate_geometry.main()`
5. `generate_csv.main()`
6. `generate_plots.main()`
7. `generate_combined_plots.main()`

Each script can also be run standalone in the same order if only part of the pipeline
needs to be re-run.

---

## Case definition files

These files contain no IFC logic — they are pure parameter tables that the semantic IFC
generators consume.

### `cases_horizontal.py`

Defines parameters for horizontal alignment test cases.

| Symbol | Value | Meaning |
|---|---|---|
| `SEGMENT_LENGTH` | 100.0 m | Length of every horizontal segment |

**`TRANSITION_TYPES`** — list of the five non-VienneseBend transition curve IFC
predefined types: `CLOTHOID`, `BLOSSCURVE`, `COSINECURVE`, `HELMERTCURVE`, `SINECURVE`.
VienneseBend is excluded because it requires a separate generator (see
`generate_horizontal.py`).

**`TRANSITION_CASES`** — 8 tuples `(start_r, end_r, start_label, end_label)` covering
entry spirals, exit spirals, and arc-to-arc loosening/tightening for both left-hand
(positive radius) and right-hand (negative radius) curves. `0.0` encodes infinite
radius; labels use `inf` / `-inf`.

**`LINE_CASES`** — 1 tuple: the straight tangent case (radius = ∞ at both ends).

**`CIRCULAR_ARC_CASES`** — 4 tuples: left and right circular arcs at R = 300 m and
R = 1000 m.

---

### `cases_vertical.py`

Defines parameters for vertical alignment test cases.

| Symbol | Value | Meaning |
|---|---|---|
| `SEGMENT_LENGTH` | 100.0 m | Horizontal length of every vertical segment |
| `START_HEIGHT` | 10.0 m | Starting elevation above datum |

Gradients are stored as percentages (e.g. `0.5` = 0.5 %).

**`CONSTANT_GRADIENT_CASES`** — 4 tuples `(start_grad, end_grad, start_label, end_label)`
for flat and sloped tangent grades. Start and end gradient are equal (required by IFC for
`CONSTANTGRADIENT`).

**`VERTICAL_TRANSITION_CASES`** — 12 tuples for `PARABOLICARC` and `CIRCULARARC`,
covering sag and crest curves with same-sign grade pairs (both ascending, both
descending) and opposite-sign grade pairs (ascending-to-descending and vice versa).

---

### `cases_cant.py`

Defines parameters for cant alignment test cases.

| Symbol | Value | Meaning |
|---|---|---|
| `SEGMENT_LENGTH` | 100.0 m | Horizontal length of every cant segment |
| `FULL_CANT` | 0.160 m | Non-zero cant value for all types except VienneseBend |
| `VB_CANT_LO` | 0.030 m | Low-end cant value for VienneseBend |
| `VB_CANT_HI` | 0.100 m | High-end cant value for VienneseBend |

Each case tuple: `(h_start_r, h_end_r, h_start_label, h_end_label, scl, ecl, scr, ecr)`

- `h_start_r / h_end_r` — horizontal radii (same sign convention as horizontal cases)
- `scl / ecl` — start/end cant on the left rail (meters)
- `scr / ecr` — start/end cant on the right rail (meters)

Left curves (positive radius) apply cant to the right rail; right curves (negative
radius) apply cant to the left rail. The non-loaded rail always has zero cant.

**`TRANSITION_CANT_CASES`** — 8 tuples (same geometry cases as horizontal transitions)
using `FULL_CANT` for the non-zero end. Entry transitions ramp 0 → full; exit
transitions ramp full → 0. Arc-to-arc cases treat the tighter radius as the full-cant
end.

**`CONSTANT_CANT_CASES`** — 4 tuples for `CONSTANTCANT` paired with `CIRCULARARC`
horizontal geometry. Both rails start and end at `FULL_CANT`.

**`VIENNESEBEND_CANT_CASES`** — 8 tuples using `VB_CANT_LO` and `VB_CANT_HI`
instead of `FULL_CANT`. Otherwise follows the same entry/exit/arc-to-arc logic.

**`TRANSITION_CANT_TYPES`** — list of `(cant_ptype, h_ptype, folder_name)` triples
pairing each cant predefined type with its matching horizontal type. `LINEARTRANSITION`
pairs with `CLOTHOID`; all others pair with the same-named type.

---

## Semantic IFC generators

These scripts build semantic-only IFC files (no geometry representation). They call
`common.setup()` to create the IFC boilerplate, then attach alignment segments via the
`common.add_*_segment()` helpers.

### `generate_horizontal.py`

Writes to `Alignment-semantic-testset/HorizontalAlignment/`.

**`make_file(curve_type, start_r, end_r, start_label, end_label)`**  
Creates a horizontal-only IFC file (no vertical or cant layout). Used for all types
except VienneseBend.

**`make_viennesebend_file(case)`**  
Creates an IFC file with all three layouts — horizontal, vertical (flat constant
gradient), and cant — using parameters from `cases_cant.VIENNESEBEND_CANT_CASES`.
VienneseBend geometry depends on cant parameters, so the cant layout must be present
for geometry IFC generation to succeed. The vertical layout is a flat `LINE` due
East at 0 % grade.

`main()` processes Line, CircularArc, the five non-VienneseBend transition types, then
VienneseBend as a special case.

---

### `generate_vertical.py`

Writes to `Alignment-semantic-testset/VerticalAlignment/`.

**`make_file(v_type, start_g, end_g, start_label, end_label)`**  
Creates an IFC file with horizontal and vertical layouts. The horizontal layout is
always a straight `LINE` due East (radius = ∞) of the same length as the vertical
segment; it exists only to satisfy the IFC schema requirement that a vertical layout
has an associated horizontal.

`main()` processes `CONSTANTGRADIENT`, `PARABOLICARC`, and `CIRCULARARC`.

---

### `generate_cant.py`

Writes to `Alignment-semantic-testset/CantAlignment/`.

**`make_file(cant_type, h_type, folder_name, case)`**  
Creates an IFC file with all three layouts. The horizontal layout uses the matching
curve type from `TRANSITION_CANT_TYPES`. The vertical layout is always a flat
`CONSTANTGRADIENT` at 0 % grade and elevation 0.0 m.

`main()` first generates `CONSTANTCANT` cases (paired with `CIRCULARARC`), then
iterates `TRANSITION_CANT_TYPES`. For VienneseBend it selects `VIENNESEBEND_CANT_CASES`
instead of `TRANSITION_CANT_CASES`.

---

## Geometry IFC generator

### `generate_geometry.py`

Reads from `Alignment-semantic-testset/`, writes to `Alignment-geometry-testset/`
(same relative path, same filename). Uses `ifcopenshell.api.alignment.create_representation`
to attach `IfcCurveSegment`-based geometric representations to every layout that has
one.

After creating representations, it appends a zero-length terminator `IfcCurveSegment`
to each geometric curve via `add_zero_length_segment`. This sentinel marks the end of
the parametric domain and is excluded from all downstream processing.

Files that fail (e.g. because a layout combination is unsupported) are skipped with
a printed warning; the pipeline continues.

---

## Reference coordinate generator

### `generate_csv.py`

Reads from `Alignment-geometry-testset/`, writes matching `.csv` files to
`Alignment-reference-testset/` (same relative path, `.ifc` → `.csv`).

Evaluates each alignment at every 1 m of horizontal distance using
`ifcopenshell.api.alignment.evaluate_segment`, which returns a 4 × 4 NumPy matrix.
Both the parameter and the returned positions are in meters; the caller divides
positions by `unit_scale` to convert to project units for output.

| Matrix row | Content |
|---|---|
| Row 0 (`m[0, :]`) | RefDirection — forward tangent unit vector |
| Row 2 (`m[2, :]`) | Axis — the "up" vector (banked for cant) |
| Row 3 (`m[3, :]`) | Position |

**Key helpers:**

`get_real_segments(curve)` — filters out the zero-length terminator; returns only
segments with `SegmentLength.wrappedValue != 0.0`. Note that `SegmentLength` is an
`IfcLengthMeasure` entity, not a float, so `.wrappedValue` is required.

`evaluate_at(real_segs, d_m, unit_scale)` — walks segments in order using
`abs(SegmentLength) * unit_scale` as each segment's length in meters, then calls
`evaluate_segment` with the local offset. The boundary condition
`d_m <= cumulative + length` assigns a point exactly at a segment boundary to the
earlier segment. This is significant for Helmert curves, which have two real segments
of equal length (all other types have one real segment).

`horizontal_n_points(alignment, unit_scale)` — returns `(h_curve, n_points)` for the
horizontal layout, where `n_points = int(round(total_m)) + 1`. This is used as
the iteration count for all alignment types so that all CSVs for a given file share
the same distance axis.

**Vertical parameterisation note:** `evaluate_segment` for a gradient curve segment
takes horizontal distance as its parameter, even though `SegmentLength` stores arc
length. The difference is negligible for the small grades in these test cases (≤ 1 %),
and using `n_points` from the horizontal layout ensures the parameter always falls
within the single real vertical segment.

**Dispatch:** the top-level directory name (`HorizontalAlignment`, `VerticalAlignment`,
`CantAlignment`) determines which `write_*_csv` function is called and therefore which
matrix components are extracted.

| File type | Columns | Matrix components |
|---|---|---|
| Horizontal | `dist_along, X, Y, RefDir_dx, RefDir_dy` | `m[3,0]`, `m[3,1]`, `m[0,0]`, `m[0,1]` |
| Vertical | `dist_along, Y, RefDir_dx, RefDir_dy` | `m[3,0]`, `m[3,2]`, `m[0,0]`, `m[0,2]` |
| Cant | `dist_along, Y, RefDir_dx, RefDir_dy, Axis_dy, Axis_dz` | `m[3,1]`, `m[0,0]`, `m[0,1]`, `m[2,1]`, `m[2,2]` |

---

## Plot generators

Both plot scripts use `matplotlib` with the SVG backend (`matplotlib.use('svg')`).
No IFC files are read at this stage; all data comes from the CSV files.

### `generate_plots.py`

Reads `HorizontalAlignment` and `VerticalAlignment` CSVs from
`Alignment-reference-testset/` and writes a matching SVG to the corresponding path
under `Alignment-plots/`. CantAlignment CSVs are skipped — those plots are produced
by `generate_combined_plots.py`.

- **Horizontal** — X vs Y, equal aspect ratio. Output: `Alignment-plots/HorizontalAlignment/{type}/`.
- **Vertical** — distance along vs elevation. Output: `Alignment-plots/VerticalAlignment/{type}/`.

### `generate_combined_plots.py`

Produces two-panel SVGs pairing a cant profile with its matching horizontal plan view.
Output goes to `Alignment-plots/CantAlignment/{CantType}/`, one file per cant CSV.

**Matching logic:** for each cant CSV, `find_horizontal_csv` reconstructs the
corresponding horizontal CSV path using the first four stem tokens (curve type, length,
start radius, end radius) and the `CANT_TO_HORIZ` mapping:

| Cant folder | Horizontal folder |
|---|---|
| `ConstantCant` | `CircularArc` |
| `LinearTransition` | `Clothoid` |
| All others | Same name |

**Panel layout:** top panel — horizontal plan view (X vs Y, equal aspect); bottom
panel — cant centerline elevation (distance along vs Y).

---

## Shared utilities

### `common.py`

Shared IFC construction helpers used by all semantic IFC generators.

**`setup(alignment_name, include_vertical=False, include_cant=False)`**  
Creates an IFC file with project, site, unit assignments (meter, radian), model
context, and an empty `IfcAlignment` with the requested layout types. The alignment is
aggregated to the project and referenced into the site's spatial structure per
CT 4.1.5.1. When `include_cant=True`, sets `RailHeadDistance = 1.5` m on the cant
layout. Returns `(ifc, alignment)`.

**`add_h_segment(ifc, layout, start_r, end_r, length, ptype)`**  
Appends one `IfcAlignmentHorizontalSegment` to the layout. Radius values follow the
IFC convention: `0.0` = infinite radius, positive = left curve, negative = right curve.

**`add_v_segment(ifc, layout, dist_along, h_length, start_height, start_grad, end_grad, ptype)`**  
Appends one `IfcAlignmentVerticalSegment`. Gradients are percentages.

**`add_c_segment(ifc, layout, dist_along, h_length, scl, ecl, scr, ecr, ptype)`**  
Appends one `IfcAlignmentCantSegment` with separate left and right rail cant values.

**`write_ifc(ifc, output_dir, filename)`**  
Creates `output_dir` if needed and writes the IFC file. Returns the destination `Path`.

**`CURVE_FOLDER`** — dict mapping IFC predefined type strings (e.g. `'CLOTHOID'`) to
their output folder names (e.g. `'Clothoid'`).

**`RAIL_HEAD_DISTANCE`** — `1.5` m, applied to all cant layouts.
