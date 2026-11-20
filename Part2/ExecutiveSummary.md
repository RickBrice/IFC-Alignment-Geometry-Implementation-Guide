# Executive Summary

IFC4x3 — published as ISO 16739-1:2024 — is the first version of the IFC schema to support infrastructure alignment geometry. Once an alignment's horizontal, vertical, and cant curves can be evaluated, the alignment becomes the positioning backbone for everything built along it: offset curves, linearly placed objects, stations and referents, and the surfaces and solids that form the physical road or railway. The specification defines the *schema* for these concepts but leaves much of their interpretation and computation to the implementer. This guide, developed by the buildingSMART USA chapter of buildingSMART International, fills that gap.

**Purpose and audience.** This is an implementation guide, not a specification, written for software developers building or extending IFC4x3 alignment support in authoring tools, viewers, and validation software. Where the IFC specification states *what* an entity means, this guide supplies *how* to compute it: equations, algorithms, worked examples, and IFC-conformant sample models.

**Part 2 — Advanced Topics: Placement, Referencing, and Derived Geometry.** This document covers offset curves (Ch. 6); approximate polyline geometry (Ch. 7); alignments reusing a common horizontal layout (Ch. 8); linear placement (Ch. 9); referents and stationing, including ISO 19148 linear referencing (Ch. 10); sectioned surfaces and solids (Ch. 11); and precision and tolerance (Ch. 12).

**Part 1 — Fundamentals: Alignment Curve Geometry** is published separately and is a prerequisite for this document. It covers alignment concepts, the parametric equations for every horizontal, vertical, and cant curve type, the alignment geometry test set, and LandXML-to-IFC conversion (Ch. 1–5, Appendix A). Chapter numbering is continuous across both parts, so references such as "Section 4.2" identify a single location in the guide.

Each chapter closes with a self-contained implementation checklist and is illustrated with figures, worked examples, and links to IFC example files.
