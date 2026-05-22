# IFC Alignment Testset

Reference test cases for IFC4X3_ADD2 alignment geometry. Each test case covers a
single alignment segment type at a fixed 100 m length and is provided in three
complementary forms — semantic IFC, geometry IFC, and sampled reference coordinates —
together with plots for visual verification.

## Folder structure

```
testset/
├── Alignment-semantic-testset/    # Semantic IFC files (no geometry)
├── Alignment-geometry-testset/    # IFC files with geometric representations
├── Alignment-reference-testset/   # Reference coordinates sampled at 1 m intervals
├── Alignment-plots/               # Plots for visual inspection
└── scripts/                       # Python generation scripts
```

Each data folder is further divided by alignment type and then by curve type:

```
{folder}/
├── HorizontalAlignment/
│   ├── Line/
│   ├── CircularArc/
│   ├── Clothoid/
│   ├── BlossCurve/
│   ├── CosineCurve/
│   ├── HelmertCurve/
│   ├── SineCurve/
│   └── VienneseBend/
├── VerticalAlignment/
│   ├── ConstantGradient/
│   ├── ParabolicArc/
│   └── CircularArc/
└── CantAlignment/
    ├── ConstantCant/
    ├── LinearTransition/
    ├── BlossCurve/
    ├── CosineCurve/
    ├── HelmertCurve/
    ├── SineCurve/
    └── VienneseBend/
```

## Test cases

### Horizontal alignment

All transition segments are 100 m long. Radii use the IFC sign convention: positive
radius curves to the left, negative radius curves to the right, and `inf` denotes an
infinite radius (straight tangent).

| Curve type | Cases | Description |
|---|---|---|
| Line | 1 | Straight tangent (inf → inf) |
| CircularArc | 4 | Left/right arcs at R = 300 m and R = 1000 m |
| Clothoid | 8 | Entry/exit spirals and arc-to-arc transitions, left and right |
| BlossCurve | 8 | Same 8 cases as Clothoid |
| CosineCurve | 8 | Same 8 cases as Clothoid |
| HelmertCurve | 8 | Same 8 cases as Clothoid |
| SineCurve | 8 | Same 8 cases as Clothoid |
| VienneseBend | 8 | Same 8 cases as Clothoid (see note below) |

The 8 transition cases cover:

| Start R | End R | Description |
|---|---|---|
| inf | 300 | Entry spiral — straight to tight left arc |
| 300 | inf | Exit spiral — tight left arc to straight |
| inf | −300 | Entry spiral — straight to tight right arc |
| −300 | inf | Exit spiral — tight right arc to straight |
| 300 | 1000 | Arc-to-arc — tighter left to looser left |
| 1000 | 300 | Arc-to-arc — looser left to tighter left |
| −300 | −1000 | Arc-to-arc — tighter right to looser right |
| −1000 | −300 | Arc-to-arc — looser right to tighter right |

**VienneseBend note:** VienneseBend horizontal geometry requires cant parameters. The
VienneseBend files in `HorizontalAlignment/VienneseBend/` therefore include all three
layouts (horizontal + vertical + cant), identical in structure to the corresponding
`CantAlignment/VienneseBend/` files. The horizontal CSV and plots extract only the
plan-view X, Y coordinates.

### Vertical alignment

All segments are 100 m horizontal length starting at an elevation of 10.0 m. Gradients
are in percent (e.g. `0.5` = 0.5 %).

| Curve type | Cases | Description |
|---|---|---|
| ConstantGradient | 5 | Flat (0 %), ±0.5 %, ±1.0 % |
| ParabolicArc | 12 | Sag and crest curves — see table below |
| CircularArc | 12 | Same 12 cases as ParabolicArc |

The 12 transition cases cover:

| Start grade | End grade | Type |
|---|---|---|
| 0.0 % | +0.5 % | Sag — flat to ascending |
| +0.5 % | 0.0 % | Crest — ascending to flat |
| 0.0 % | −0.5 % | Crest — flat to descending |
| −0.5 % | 0.0 % | Sag — descending to flat |
| +0.5 % | +1.0 % | Sag — both ascending |
| +1.0 % | +0.5 % | Crest — both ascending |
| −0.5 % | −1.0 % | Crest — both descending |
| −1.0 % | −0.5 % | Sag — both descending |
| +0.5 % | −1.0 % | Crest — ascending to descending |
| −0.5 % | +1.0 % | Sag — descending to ascending |
| +1.0 % | −0.5 % | Crest — ascending to descending |
| −1.0 % | +0.5 % | Sag — descending to ascending |

### Cant alignment

All cant segments are 100 m long with a rail head distance of 1.5 m. Cant values are
in meters. Left curves (positive radius) apply cant to the right rail; right curves
(negative radius) apply cant to the left rail.

All transition types use the same 8 geometry cases as horizontal transitions.

| Cant type | Pairs with | Cases | Cant values |
|---|---|---|---|
| ConstantCant | CircularArc | 4 | 0.16 m constant at R = ±300 m and R = ±1000 m |
| LinearTransition | Clothoid | 8 | 0.0 ↔ 0.16 m |
| BlossCurve | BlossCurve | 8 | 0.0 ↔ 0.16 m |
| CosineCurve | CosineCurve | 8 | 0.0 ↔ 0.16 m |
| HelmertCurve | HelmertCurve | 8 | 0.0 ↔ 0.16 m |
| SineCurve | SineCurve | 8 | 0.0 ↔ 0.16 m |
| VienneseBend | VienneseBend | 8 | 0.03 ↔ 0.10 m |

Entry transitions ramp from the low value to the high value; exit transitions ramp from
high to low. Arc-to-arc cases treat the tighter radius (smaller absolute value) as the
full-cant end.

## File naming

Each file carries a prefix that identifies both the alignment type and whether the file
is a raw semantic definition or a generated geometry file.

### Semantic IFC files (`Alignment-semantic-testset/`)

#### Horizontal and cant

```
Horizontal_{CurveType}_{Length}_{StartRadius}_{EndRadius}_{Unit}.ifc
Cant_{CurveType}_{Length}_{StartRadius}_{EndRadius}_{Unit}.ifc
```

Examples:
- `Horizontal_Clothoid_100.0_inf_300_Meter.ifc` — Clothoid entry spiral, R = ∞ → 300 m
- `Horizontal_BlossCurve_100.0_-300_-1000_Meter.ifc` — Bloss arc-to-arc, R = −300 → −1000 m
- `Cant_BlossCurve_100.0_-300_-1000_Meter.ifc` — Bloss cant arc-to-arc, R = −300 → −1000 m

`inf` and `-inf` denote infinite radius (straight tangent). Positive radii curve left,
negative radii curve right.

#### Vertical

```
Vertical_{CurveType}_{Length}_{StartHeight}_{StartGrade}_{EndGrade}_{Unit}.ifc
```

Example:
- `Vertical_ParabolicArc_100.0_10.0_0.5_-1.0_Meter.ifc` — parabolic crest, start grade
  +0.5 %, end grade −1.0 %, starting at elevation 10.0 m.

### Geometry IFC files (`Alignment-geometry-testset/`)

Geometry files carry a `Generated_` prefix in addition to the alignment type prefix,
making it unambiguous which files were produced by the pipeline versus hand-authored.

```
Generated_Horizontal_{CurveType}_{Length}_{StartRadius}_{EndRadius}_{Unit}.ifc
Generated_Vertical_{CurveType}_{Length}_{StartHeight}_{StartGrade}_{EndGrade}_{Unit}.ifc
Generated_Cant_{CurveType}_{Length}_{StartRadius}_{EndRadius}_{Unit}.ifc
```

### Reference CSV files (`Alignment-reference-testset/`)

CSV files use the same name as the corresponding semantic IFC file, with the `.ifc`
extension replaced by `.csv`:

```
Horizontal_{CurveType}_{Length}_{StartRadius}_{EndRadius}_{Unit}.csv
Vertical_{CurveType}_{Length}_{StartHeight}_{StartGrade}_{EndGrade}_{Unit}.csv
Cant_{CurveType}_{Length}_{StartRadius}_{EndRadius}_{Unit}.csv
```

## CSV columns

Coordinates are sampled at every 1 m of horizontal distance along the alignment,
giving 101 rows per file (distance 0.0 through 100.0).

### Horizontal (`HorizontalAlignment/**/*.csv`)

| Column | Description |
|---|---|
| `dist_along` | Distance along the alignment from the segment start (m) |
| `X` | Easting coordinate in the alignment plane (m) |
| `Y` | Northing coordinate in the alignment plane (m) |
| `RefDir_dx` | X component of the forward tangent unit vector (RefDirection) |
| `RefDir_dy` | Y component of the forward tangent unit vector (RefDirection) |

### Vertical (`VerticalAlignment/**/*.csv`)

| Column | Description |
|---|---|
| `dist_along` | Horizontal distance from the segment start (m) |
| `Y` | Elevation (m) |
| `RefDir_dx` | X component of the tangent direction (= cos of grade angle) |
| `RefDir_dy` | Y component of the tangent direction (= sin of grade angle) |

### Cant (`CantAlignment/**/*.csv`)

| Column | Description |
|---|---|
| `dist_along` | Distance along the horizontal alignment (m) |
| `Y` | Track centerline deviating elevation due to cant (m) |
| `RefDir_dx` | X component of the forward tangent (RefDirection) |
| `RefDir_dy` | Y component of the forward tangent (RefDirection) |
| `Axis_dy` | Y component of the banked "up" axis vector |
| `Axis_dz` | Z component of the banked "up" axis vector |

The banked axis (`Axis_dy`, `Axis_dz`) is the cross-track "up" direction after applying
the cant rotation. Its X component is always 0.0 for a planar track.

## Plots

`Alignment-plots/` mirrors the three alignment-type subfolders:

**Horizontal plan views** (`Alignment-plots/HorizontalAlignment/{type}/`)  
One plan-view plot per horizontal CSV (X vs Y, equal aspect ratio).

**Vertical elevation profiles** (`Alignment-plots/VerticalAlignment/{type}/`)  
One elevation profile plot per vertical CSV (distance along vs elevation).

**Combined horizontal + cant** (`Alignment-plots/CantAlignment/{type}/`)  
One two-panel plot per cant CSV pairing the cant profile with its matching horizontal
plan view:
- Top panel — plan view of the horizontal alignment (X vs Y, equal aspect ratio)
- Bottom panel — cant centerline elevation profile (distance along vs Y)

## Regenerating the testset

All output folders are generated from scratch by a single script:

```
python testset/scripts/generate_testsets.py
```

This deletes and recreates all four output directories, then runs the full pipeline:

| Stage | Script | Input | Output |
|---|---|---|---|
| Semantic IFC | `generate_horizontal.py`, `generate_vertical.py`, `generate_cant.py` | `scripts/cases_*.py` | `Alignment-semantic-testset/` |
| Geometry IFC | `generate_geometry.py` | `Alignment-semantic-testset/` | `Alignment-geometry-testset/` |
| Reference coordinates | `generate_csv.py` | `Alignment-geometry-testset/` | `Alignment-reference-testset/` |
| Plots | `generate_plots.py`, `generate_combined_plots.py` | `Alignment-reference-testset/` | `Alignment-plots/` + inline SVGs |

Test case parameters are defined in `scripts/cases_horizontal.py`,
`scripts/cases_vertical.py`, and `scripts/cases_cant.py`.

### Dependencies

- [IfcOpenShell](https://ifcopenshell.org/) with `ifcopenshell.api.alignment` (used for
  semantic IFC construction and geometry generation)
- [matplotlib](https://matplotlib.org/) (used for plot generation)
