# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a pure markdown documentation project: an **IFC4x3 Alignment Geometry Implementation Guide** authored by Richard Brice, PE. It captures implementation lessons learned while adding alignment geometry support to IfcOpenShell and provides mathematical reference for developers implementing IFC alignment-based geometry in infrastructure software.

There are no build, lint, or test commands — the project is entirely markdown documents, images, and IFC example files.

## Repository Structure

The guide is organized as numbered markdown chapters at the repository root:

| File | Topic | Status |
|------|-------|--------|
| `1_IFC_Alignment_Concepts.md` | IFC alignment concepts, semantic vs. geometric representations | Complete |
| `2_Horizontal_Alignments.md` | Parametric equations for all horizontal curve types | Complete (longest, ~1,300 lines) |
| `3_Vertical_Alignments.md` | Vertical alignment: grade lines, parabolic & circular arcs | Complete |
| `4_Cant_Alignments.md` | Rail superelevation via IfcSegmentedReferenceCurve | Complete |
| `5_OffsetCurves.md` | Offset curve definitions | Complete |
| `6_Approximate_Alignment_Geometry.md` | IfcPolyline and IfcIndexedPolyCurve — survey/early-planning representations | Complete |
| `7_Alignments_Reusing_Horizontal_Layout.md` | Multiple alignments sharing a common horizontal layout | Complete |
| `8_LinearPlacement.md` | Linear placement concepts | Complete |
| `9_Referents_and_Stationing.md` | Referents and stationing | Complete |
| `10_Sectioned_Surfaces_and_Solids.md` | Sectioned surfaces and solids (IfcSectionedSurface, IfcSectionedSolidHorizontal) | Complete |
| `11_Precision_and_Tolerance.md` | Precision and tolerance guidance | Complete |
| `12_Alignment_Geometry_Testset.md` | Alignment geometry testset | Complete |
| `13_References.md` | References | Complete |
| `Appendix_A_LandXML.md` | LandXML-to-IFC conversion (Appendix A) | Complete |

### Figures

`figures/` contains hand-edited IFC source files used as input to figure generation scripts. `figures/scripts/` contains the Python scripts that read those IFC files and write SVG output to `images/`. These IFC files have been manually adjusted to produce specific visual results and are not general-purpose alignment examples.

### Examples

`examples/IfcOffsetCurveByDistances.ifc` is a standalone IFC example for offset curves.

`examples/Alignment-atomic-testset/` contains 48 test cases across 6 transition curve types (Clothoid, Bloss, Cosine, Sine, Helmert, VienneseBend), each with 5 IFC variants. All IFC examples use schema version IFC4X3_ADD2 (ISO 16739-1:2024).

#### Testset file naming convention

IFC files in `Alignment-atomic-testset/` follow the pattern:
```
{CurveType}_TS{N}_{length}_{StartRadius}_{EndRadius}_{StartCurvature}_{EndCurvature}_{scale}_{unit}.ifc
```
Excel reports and plot images use the same base name. The five IFC variants per test case live in subdirectories: `horizontal/`, `horizontal_check/`, `horizontal_vertical/`, `horizontal_vertical_check/`, and `check/`.

The **`check`** variants contain only control alignment geometry and control points (reference geometry for verifying implementations), not the primary alignment definition. The `horizontal_check` and `horizontal_vertical_check` variants combine primary alignment with this check geometry.

The vertical layout in all testset cases is a flat grade (gradient = 0) — it exists solely to produce a valid 3D combined alignment for testing; it carries no elevation design intent.

## Domain Context

**IFC alignment** represents infrastructure geometry (roads, railways, tunnels) using three stacked alignment representations:
- **Horizontal alignment** (`IfcAlignmentHorizontal`) — plan-view geometry using Lines, CircularArcs, and transition curves
- **Vertical alignment** (`IfcAlignmentVertical`) — profile/grade using constant grades and parabolic/circular arcs
- **Cant alignment** (`IfcAlignmentCant`) — rail superelevation (cross-slope) defined along the horizontal alignment

These combine into a 3D alignment via `IfcGradientCurve` (horizontal + vertical → 2.5D) and `IfcSegmentedReferenceCurve` (adds cant → full 3D with banking).

**Six transition curve types** appear throughout the examples and chapter 2: Clothoid (Euler spiral), Bloss, Cosine, Sine, Helmert (biquadratic parabola), and VienneseBend. Each has distinct parametric equations for curvature, tangent angle, and x/y ordinates.

**Key IFC entities** referenced throughout:
- `IfcAlignment`, `IfcAlignmentHorizontal`, `IfcAlignmentVertical`, `IfcAlignmentCant`
- `IfcCompositeCurve`, `IfcGradientCurve`, `IfcSegmentedReferenceCurve`
- `IfcAlignmentSegment` with subtypes like `IfcAlignmentHorizontalSegment`, `IfcAlignmentVerticalSegment`
- `IfcCurveSegment` — the geometric counterpart to semantic alignment segments

## Writing Conventions

- Mathematical equations use LaTeX syntax rendered by GitHub Markdown (fenced with `$$` for display math, `$...$` for inline).
- Figures reference files in `images/` using relative markdown links. Both PNG and SVG files exist in `images/`; SVGs are used for technical line-art diagrams.
- IFC attribute names are written in `code style` (e.g., `StartRadiusOfCurvature`, `EndRadiusOfCurvature`, `SegmentLength`).
- Positive curvature convention: curves to the left (from the perspective of a traveler moving in the direction of increasing chainage).
- The guide distinguishes **semantic** alignment (business/design intent, `IfcAlignmentSegment` subtypes) from **geometric** alignment (mathematical curve representation, `IfcCurveSegment`).
- Tables and Figures are numbered using the section number and a sequence number. An example is Figure 3.2.1-3 is the third figure in section 3.2.1.
- The specification/schema is spelled **`IFC4x3`** (lowercase x) in prose. The literal schema identifier as it appears in STEP files and example code (e.g., `IFC4X3_ADD2`, `FILE_SCHEMA(('IFC4X3'))`) keeps its actual all-caps spelling — that's a literal enum/string value, not a prose reference, so it's not affected by this rule.

### Image naming

Two naming schemes exist in `images/`:
- Older chapters use generic names: `image1.png`, `image2.1.png`, etc.
- Newer chapters use descriptive names: `Figure_9.1_Superelevation_Transition.png`. Prefer this style for new figures.

Each curve-type subdirectory under `Alignment-atomic-testset/` also has its own `images/` folder for testset plot images — these are separate from the root `images/` directory.

### ERD (entity relationship diagram) figures

Several figures illustrate IFC entity relationships (which entity references which, via which attribute or relationship class) rather than geometry. These are **hand-authored raw SVG** — there is no generator script or diagramming tool involved; new ones are built by copying the structure of an existing one and editing it directly.

Canonical examples to copy from:
- `images/Figure_9.4.2-1_Referent_Entity_Relationship.svg` — best source for the shared `<defs>` block (arrow marker, text classes, color classes) and the legend box pattern.
- `images/Figure_9.3.2-1_Alignment_RelNests_ERD.svg` — best source for the "spine + branches" idiom (one entity fanning out to several related entities via a single trunk line).

Shared conventions across all ERD figures:
- **Color semantics** (applied via `c-purple`/`c-blue`/`c-teal`/`c-gray` classes on a `<g>` wrapping each box): purple = rooted product/root entity, blue = representation/placement infrastructure, teal = geometry or tag-carrying content, gray = relationship entities (`IfcRelNests`, `IfcRelAggregates`, etc.).
- Boxes are rounded rects (`rx="8"`) with a bold title (`.th`) and optional subtitle (`.ts`) reusing the shared `text`/`.th`/`.ts`/`.lbl` style rules and the single `<marker id="arrow">` definition — copy these verbatim rather than redefining per figure.
- A small legend box in a corner lists every color class actually used in that figure.
- **Spine + branches**: for one entity with an ordered list of several related entities (e.g. `Items`, `RelatedObjects`), draw one trunk line from the source box then branch to each target with its own arrowhead, labeled once near the trunk (e.g. "Items (ordered list of N)").
- **Dashed correlation**: for a relationship that is informal/by-convention rather than a formal schema attribute or relationship (e.g. two values that merely happen to match), use a dashed gray line with no intermediate box, labeled to say it is not a schema relationship.
- Accessibility: every ERD has `role="img"`, a `<title>`, and a `<desc>` summarizing the relationships depicted.
- Naming: `Figure_{section}-{n}_{Descriptive_Name}.svg`, following the general image-naming convention above; the markdown alt text starts with "Entity relationship diagram:".

## TO DO List

The following of a list of things to address for the next version of this document.

[ ] add a note in chapter 10, sectioned surfaces and solids, about the Tag attribute on IfcBuiltElement and reference the discussion here: https://community.osarch.org/discussion/comment/25421#Comment_25421
