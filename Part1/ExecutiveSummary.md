# Executive Summary

IFC4x3 — published as ISO 16739-1:2024 — is the first version of the IFC schema to support infrastructure alignment geometry: the horizontal, vertical, and cant (superelevation) curves defining the plan, profile, and cross-slope of roads, railways, and other linear infrastructure. The specification defines the *schema* for these entities but not the *mathematics* needed to evaluate them — the parametric equations for curvature, tangent direction, and position are left to the implementer. This guide, developed by the buildingSMART USA chapter of buildingSMART International, fills that gap.

**Purpose and audience.** This is an implementation guide, not a specification, written for software developers building or extending IFC4x3 alignment support in authoring tools, viewers, and validation software. Where the IFC specification states *what* an entity means, this guide supplies *how* to compute it: closed-form and iterative equations, worked examples, and IFC-conformant sample models.

**Part 1 — Fundamentals: Alignment Curve Geometry.** This document covers the core of the alignment geometry stack: semantic vs. geometric representations and concept templates (Ch. 1); parametric equations for every horizontal, vertical, and cant curve type — lines, circular arcs, parabolas, and the transition-curve families (Clothoid, Bloss, Cosine, Sine, Helmert, Viennese Bend) (Ch. 2–4); a validated alignment geometry test set (Ch. 5); and LandXML-to-IFC conversion (Appendix A).

**Part 2 — Advanced Topics: Placement, Referencing, and Derived Geometry** is published separately. It builds on Part 1 to cover offset curves, approximate polyline geometry, alignment reuse across layouts, linear placement, referents and stationing, sectioned surfaces and solids, and precision and tolerance (Ch. 6–12). Chapter numbering is continuous across both parts.

Each chapter closes with a self-contained implementation checklist and is illustrated with figures, worked examples, and links to IFC example files. Readers new to IFC alignment geometry should start with Chapters 1–2; others may go directly to the chapter covering their feature of interest.
