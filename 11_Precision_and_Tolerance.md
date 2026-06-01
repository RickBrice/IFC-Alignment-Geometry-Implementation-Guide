# Chapter 11 — Precision and Tolerance

## 11.0 Introduction

Alignment geometry is rarely mathematically perfect. Design parameters are rounded to convenient values, segment coordinates are computed independently by different tools, and transition curve ordinates are approximated by numerical integration — all of which introduce small discrepancies at segment joints. Alignments derived from historical sources carry additional uncertainty from the original survey or drafting. IFC provides mechanisms for both declaring the intended geometric continuity at segment joints and communicating the tolerance within which that continuity should be evaluated.

The primary declaration mechanism is `IfcCurveSegment.Transition`, which specifies the intended relationship between the end of one segment and the start of the next. Table 11.0-1 lists the available transition codes.

|Transition Value               |Description                                                                                                                                                                                                                                                                                                                    |
|-----------------------------|-------------------------------------------------------------------|
|`CONTINUOUS`                   |The segments join but no condition on their tangents is implied.                                                                                                                                                                                                                                                               |
|`CONTSAMEGRADIENT`             |The segments join and their tangent vectors or tangent planes are parallel and have the same direction at the joint; equality of derivative is not required.                                                                                                                                                                   |
|`CONTSAMEGRADIENTSAMECURVATURE`|For a curve, the segments join, their tangent vectors are parallel and in the same direction and their curvatures are equal at the joint: equality of derivatives is not required. For a surface this implies that the principle curvatures are the same and the principle directions are coincident along the common boundary.|
|`DISCONTINUOUS`                |The segments do not join. This is permitted only at the boundary of the curve or surface to indicate that it is not closed.                                                                                                                                                                                                |

*Table 11.0-1 — IfcCurveSegment transition codes*

Figure 11.0-1 illustrates the various transition types. 

![Figure 11.0-1 — Diagram illustrating four IfcTransitionCode values at segment junctions: CONT_SAME_GRADIENT_SAME_CURVATURE (C2-continuous, smooth), CONT_SAME_GRADIENT (C1, tangent-continuous), CONTINUOUS (C0, positional only), and DISCONTINUOUS (gap or kink). Each value is illustrated with a representative curve junction sketch.](images/Figure_11.0-1_IfcTransitionCode.gif)

*Figure 11.0-1 - Illustration of segment transition types*

These transition codes declare intent, not guarantee. Adjacent segment end and start points may not exactly line up in position, gradient, or curvature for several reasons:

* **Rounded design parameters.** Designers routinely round curve parameters — radius, arc length, tangent bearing — to convenient values. Geometry computed from those rounded values does not land exactly on the next segment's stored start point.
* **Independent segment computation.** Each segment's coordinates are often computed independently from its own parameters rather than chained forward from the previous segment's computed end. Floating-point rounding differences between two independent computations of the same nominal point produce small gaps or overlaps at joints.
* **Numerical integration of transition curves.** The x/y ordinates at the end of a spiral are transcendental integrals — Fresnel integrals for Clothoids, analogous forms for Bloss, Cosine, and the other spiral types — that different software approximates with different precision. The same nominal parameters can yield slightly different endpoint coordinates depending on the tool that produced them.
* **Unit conversion.** Converting between feet and meters, or between degrees/minutes/seconds and decimal degrees, introduces rounding that propagates to all downstream coordinates.
* **Legacy source fidelity.** Alignments derived from historical plan sheets, right-of-way plats, or field surveys carry the measurement uncertainty inherent in the original source material. Many times, the accuracy is "good enough" for its purpose.

`Pset_Tolerance` indicates the acceptable tolerance under which the calculated end point of a preceding segment would be considered geometrically continuous with the provided start point of the following segment. No implementation agreement exists for how its properties should be used; the `OverallTolerance` property is recommended. Similarly, `Pset_Uncertainty` indicates the uncertainty inherent in historical information gleaned from plan sets and other historic sources, and carries no implementation agreement; the `LinearUncertainty` property is recommended. As a fallback if `Pset_Tolerance` is not provided, tolerance can be taken from `IfcGeometricRepresentationContext.Precision`.

## 11.1 Handling Geometry Mismatches at Segment Joints

The IFC specification is silent on how an implementation should respond when the computed end point of one segment does not exactly match the stored start point of the next, even when a `CONTSAMEGRADIENT` or `CONTSAMEGRADIENTSAMECURVATURE` transition is declared.

Mismatches are inevitable in practice. They are especially common in alignments derived from historical sources, where design parameters were rounded for readability on paper plan sheets. Tangent bearings are a typical case: a bearing recorded in degrees-minutes-seconds with the seconds term truncated to a whole number introduces a small angular error whose positional effect accumulates over the length of the tangent run. Segment lengths and curve delta angles are similarly simplified — rounded to the nearest foot, or to a convenient angle. Each segment is computed independently from its own rounded parameters, and the positional differences at joints can reach non-trivial magnitudes. The BPaimio–Kupittaa railway alignment in [Chapter 12](12_Alignment_Geometry_Testset.md) is a real-world example: its `IfcGeometricRepresentationContext.Precision` is set to 0.1 m, reflecting exactly this kind of plan-rounding heritage. Critically, the gaps exist only in the data — the physical railway has no abrupt offsets or kinks at segment boundaries. The infrastructure is continuous; the apparent discontinuity is an artifact of parameter rounding in the original record or the inherent limitations of the surveying techniques used to capture it.

Several reconciliation strategies are possible; the right choice depends on the application's purpose:

- **Accept and evaluate as-is.** Each segment is evaluated from its own stored start point. Gaps and overlaps at joints are ignored. The declared transition code is taken as a statement of design intent rather than a geometric guarantee. This is the most faithful reading of the file and is appropriate for applications whose primary task is geometry display or quantity take-off where sub-meter positional accuracy is sufficient.

- **Chain forward (snap).** The computed end point of each segment is carried forward as the start point of the next, overriding the stored value. This produces a geometrically continuous chain but subtly distorts the individual segment parameters. It is appropriate when downstream processing requires strict continuity — for example, when constructing a composite curve for clash detection or BIM integration — provided the caller understands the parameters have been adjusted.

- **Interpolate across the gap.** A blending zone is constructed at each joint to smooth over the mismatch. This is geometrically the most forgiving approach but adds complexity, introduces geometry not present in the original design, and is difficult to implement consistently. It is rarely the right choice for engineering applications.

- **Reject or warn.** Files in which a declared continuous transition is violated beyond a threshold are flagged. This is appropriate for authoring and validation tools whose role is to enforce data quality. The warning should report the mismatch magnitude so the sender can investigate its source.

No single strategy is universally correct. A staking or track geometry application demands accuracy that the accept-as-is strategy cannot provide; a visualisation tool has no need to chain-forward. Implementations should document which strategy they apply and, where possible, expose it as a configurable option.

## 11.2 IfcGeometricRepresentationContext.Precision

`IfcGeometricRepresentationContext.Precision` declares the intended coordinate precision of the model — the smallest meaningful distance in the model's unit system. It is the appropriate fallback when `Pset_Tolerance` is not attached to the alignment.

The precision value varies widely depending on the source and purpose of the model. A freshly computed design model may carry a precision of 10⁻⁵ m or smaller, consistent with double-precision floating-point arithmetic. A model converted from historical plan data — such as the BPaimio–Kupittaa example — may carry 0.1 m, reflecting the resolution of the original source.

An implementation reading an alignment should retrieve this value and use it to contextualise segment joint mismatches: a gap smaller than the declared precision is likely a rounding artefact and should be treated accordingly; a gap that substantially exceeds it warrants investigation.
