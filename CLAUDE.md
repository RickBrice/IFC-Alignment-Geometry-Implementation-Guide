# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a pure markdown documentation project: an **IFC4x3 Alignment Geometry Implementation Guide** authored by Richard Brice, PE. It captures implementation lessons learned while adding alignment geometry support to IfcOpenShell and provides mathematical reference for developers implementing IFC alignment-based geometry in infrastructure software.

There are no build, lint, or test commands — the project is entirely markdown documents, images, and IFC example files.

## Repository Structure

The guide is organized as 11 numbered markdown chapters at the repository root:

| File | Topic | Status |
|------|-------|--------|
| `1_Introduction.md` | IFC alignment concepts, semantic vs. geometric representations | Complete |
| `2_Horizontal.md` | Parametric equations for all horizontal curve types | Complete (longest, ~1,300 lines) |
| `3_Vertical.md` | Vertical alignment: grade lines, parabolic & circular arcs | Complete |
| `4_Cant.md` | Rail superelevation via IfcSegmentedReferenceCurve | Complete |
| `5_LinearPlacement.md` | Linear placement concepts | Partial |
| `6_OffsetCurves.md` | Offset curve definitions | Partial |
| `8_Referents_and_Stationing.md` | Referents and stationing | Partial |
| `9_Specialized_Infrastructure_Geometry.md` | Domain-specific geometry | Stub |
| `10_LandXML.md` | LandXML-to-IFC conversion | Stub |
| `11_Precision_and_Tolerance.md` | Precision and tolerance guidance | Partial |


`examples/` contains IFC file examples and the `Alignment-atomic-testset/` with 48 test cases across 6 transition curve types (Clothoid, Bloss, Cosine, Sine, Helmert, VienneseBend), each with 5 IFC variants (horizontal only, with/without check data, combined horizontal+vertical). All IFC examples use schema version IFC4X3_ADD2 (ISO 16739-1:2024).

### Testset file naming convention

IFC files in `Alignment-atomic-testset/` follow the pattern:
```
{CurveType}_TS{N}_{length}_{StartRadius}_{EndRadius}_{StartCurvature}_{EndCurvature}_{scale}_{unit}.ifc
```
Excel reports and plot images use the same base name. The five IFC variants per test case live in subdirectories: `horizontal/`, `horizontal_check/`, `horizontal_vertical/`, `horizontal_vertical_check/`, and `check/`.

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
- Figures reference files in `images/` using relative markdown links.
- IFC attribute names are written in `code style` (e.g., `StartRadius`, `EndRadius`, `SegmentLength`).
- Positive curvature convention: curves to the left (from the perspective of a traveler moving in the direction of increasing chainage).
- The guide distinguishes **semantic** alignment (business/design intent, `IfcAlignmentSegment` subtypes) from **geometric** alignment (mathematical curve representation, `IfcCurveSegment`).

### Image naming

Two naming schemes exist in `images/`:
- Older chapters use generic names: `image1.png`, `image2.1.png`, etc.
- Newer/in-progress chapters use descriptive names: `Figure_9.1_Superelevation_Transition.png`. Prefer this style for new figures.

### Draft outline notes

Partial and stub chapters often begin with a plain-text `outline:` block (before the first heading) listing content still to be written. Preserve these notes when editing; remove a note only once its corresponding content has been written.
