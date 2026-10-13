# Chapter 9 — Referents and Stationing

## 9.0 Introduction

Chapter 8 established that `IfcPointByDistanceExpression.DistanceAlong` is a **geometric distance** — a raw arc-length measure from the start of a curve. But civil engineering practice does not communicate location this way. Engineers say “Pier 3 is at Station 14+235.75,” not “Pier 3 is 14,235.75 feet from the start of the survey baseline.” The station label is a human-readable, project-specific identifier that may begin at an arbitrary value, may use different units than the project, and may not even progress continuously along the alignment.

`IfcReferent` is the IFC mechanism that bridges these two worlds. It is a positioned object that attaches semantic location information — most importantly, stationing — to a specific geometric point on an alignment. It does not change the geometry; it annotates it.

`IfcReferent` plays two distinct roles, and this chapter is organized around them:

- What `IfcReferent` is and the range of uses it serves beyond stationing.
- Stationing as a concept: what a station is, why station equations (gaps and overlaps) exist, and how to convert between station labels and `DistanceAlong`.
- The **geometric role** — how a referent is attached to its own alignment: `Pset_Stationing`, `IfcRelNests`, and the nesting/placement edge cases that follow directly from that mechanism (the mixed-nesting problem, `ObjectPlacement` for semantic-only alignments, key-point referents marking a layout's own segment transitions, and — per ISO 19148 — why an `INTERSECTION` referent is owned by one alignment rather than shared between two).
- The **semantic role** — how a referent labels another product's position via `IfcRelPositions`, covering the single-point pattern (Product Relative Positioning) and the start/end-extent pattern (Product Span Positioning).
- How the fact that two alignments physically cross — as opposed to the station label at that location — is recorded independently of any referent, using `IfcRelInterferesElements` between the facilities the alignments lay out.

## 9.1 What Is a Referent?

`IfcReferent` is a subtype of `IfcPositioningElement`, which is itself a subtype of `IfcProduct`. Like any product, it has an `ObjectPlacement` (typically `IfcLinearPlacement`) that locates it geometrically on an alignment, and it can carry property sets that provide additional semantic information at that location.

The single attribute `IfcReferent` adds beyond its supertypes is `PredefinedType` (`IfcReferentTypeEnum`), which guides receivers on how to interpret the referent and which property sets are relevant:

- **Stationing system definition** (`STATION`). Defines the alignment's own stationing system: the starting station or a station equation. A `STATION` referent is nested under `IfcAlignment` via `IfcRelNests` (§9.3.1) — it establishes stationing, it does not label another object.
- **Linear referencing events** (`SUPERELEVATIONEVENT`, `WIDTHEVENT`). Locations where a design parameter changes — superelevation transitions, width changes, and similar cross-section events.
- **Reference markers and mileposts** (`REFERENCEMARKER`, `KILOPOINT`, `MILEPOINT`). Physical objects in the right-of-way that are part of a real-world linear referencing system.
- **Administrative boundaries** (`BOUNDARY`). Locations where a jurisdiction, maintenance zone, or asset ownership boundary crosses the alignment.
- **Intersection locations** (`INTERSECTION`). Points where another road or route crosses the alignment.
- **Position of another object** (`POSITION`). The most common use. Gives the station label of some other product's location — a bridge pier, a sign, a guardrail run — without defining the stationing system itself. A `POSITION` referent is linked to the object it labels via `IfcRelPositions` (§9.4).

`STATION` and `POSITION` are easy to conflate, since both carry `Pset_Stationing` and both resolve to a station label. The distinction is structural, not just semantic: a `STATION` referent is *part of* the alignment's stationing system (`IfcRelNests`), while a `POSITION` referent *consumes* that system to label something else (`IfcRelPositions`) — the two are never the same referent instance.

## 9.2 Stationing

### 9.2.1 What Is a Station?

Stationing (also called *chainage* in British practice) is a distance-based coordinate system used to identify locations along a linear route. In North American highway practice, stations are expressed in the form `ccc+dd.dd`, where the number before the `+` is the count of hundreds of feet (or hundreds of meters in metric projects) and the digits after are the remainder. For example, Sta. 142+35.75 means 14,235.75 feet (or meters) from the project datum.

The project datum — the zero point of stationing — is defined by the first `IfcReferent` nested in the alignment (see §9.3.1). Stationing typically begins at a round number such as 10+00 or 100+00 rather than 0+00, to avoid negative stations at points that may be surveyed upstream of the formal project start.

Stationing is a **display convention**, not a geometric quantity. The geometric position of a point is fully determined by `DistanceAlong` in `IfcPointByDistanceExpression`. The station label is metadata that identifies that point to engineers and field crews in human-readable terms.

### 9.2.2 Why Station Equations Exist

A station equation (also called a *chainage break* or *stationing equation*) is a discontinuity in the stationing system at which the station value jumps. Equations arise in several common situations:

**Realignment.** When a road is realigned — a curve is straightened or a new bypass is built — the new alignment geometry is a different length than the old. Rather than re-station the entire project downstream of the change (which would invalidate all existing plan sheets, permits, and as-built records), engineers introduce a station equation at the point where the old and new alignments reconnect. The geometry changes; the stationing on the downstream portion is preserved.

**Survey accumulation.** Long routes are often surveyed in segments. Small differences in measurement between survey crews produce a gap or overlap at the junction point. Rather than re-survey everything, an equation is introduced.

**Existing route adoption.** When a new project ties into an existing road with its own stationing, an equation reconciles the two stationing systems at the junction.

### 9.2.3 Gap Equations

A **gap equation** (also called a *station ahead* or *forward equation*) occurs when stationing jumps forward. The alignment geometry is continuous, but the station number increases by more than the physical length at the equation point.

*Example:* The alignment arrives at a point with incoming station 142+35.75. Due to a realignment that shortened the route, the outgoing station is 145+00.00. There is a gap of 264.25 ft. A distance of 14,235.75 ft of geometry corresponds to a label of 145+00, not 142+35.75.

![Figure 9.2.3-1 — Station gap equation: incoming alignment arrives at Sta. 142+35.75, the equation point jumps forward to Sta. 145+00.00, with a GAP annotation showing 264.25 ft of stationing skipped. The outgoing alignment continues to the right with an arrow.](images/Figure_9.2.3-1_Gap_Equation.svg)

*Figure 9.2.3-1 — Station gap equation. Geometry is continuous; station numbers jump forward.*

### 9.2.4 Overlap Equations

An **overlap equation** (also called a *station back* or *backward equation*) occurs when stationing jumps backward. The alignment geometry is continuous, but the station number decreases at the equation point.

*Example:* Incoming station 78+42.10, outgoing station 76+00.00. There is an overlap of 242.10 ft. Two different geometric points — one upstream and one downstream of the equation — carry station labels between 76+00 and 78+42.

![Figure 9.2.4-1 — Station overlap equation: incoming alignment arrives at Sta. 78+42.10, the equation point jumps backward to Sta. 76+00.00, with an OVERLAP annotation showing 242.10 ft of station range used twice. The outgoing alignment continues to the right with an arrow.](images/Figure_9.2.4-1_Overlap_Equation.svg)

*Figure 9.2.4-1 — Station overlap equation. Geometry is continuous; station numbers jump backward.*

### 9.2.5 Effect on `DistanceAlong` Conversion

The presence of station equations means that **you cannot convert a station label to `DistanceAlong` by simple subtraction of the starting station**. You must account for every equation encountered between the alignment start and the point of interest.

The conversion algorithm is:

1. Sort all referents on the alignment by `DistanceAlong`. For each referent record two values:
    - $D_i$: the `DistanceAlong` read directly from its `IfcLinearPlacement`
    - $S_i$: the outgoing station — `Pset_Stationing.Station`
1. *(Optional validation)* For any referent that also carries `IncomingStation`, verify that $S_{i-1} + (D_i - D_{i-1}) \approx \text{IncomingStation}$. This confirms that the station count in the preceding segment matches the geometry.
1. To convert a target station $S$ to `DistanceAlong`, find the last referent $i$ such that $S_i \leq S$. Then:

$$\text{DistanceAlong} = D_i + (S - S_i)$$

Before applying the formula, check whether the station overshoots the next referent: if a next referent exists and $S - S_i > D_{i+1} - D_i$, the station falls inside a gap — it was skipped by a forward equation — and `DistanceAlong` is undefined.

Figure 9.2.5-1 illustrates how the geometric distance axis and the station label axis diverge when equations are present.

![Figure 9.2.5-1 — Two-panel diagram. Top: uniform geometric distance axis with five points P₁–P₅ at 200 m spacing. Bottom: station label axis for the same points, with a station equation gap at P₃ (red — back station less than forward station) and an overlap at P₄ (green — back station greater than forward station), illustrating how station equations introduce discontinuities in the labeling axis.](images/Figure_9.2.5-1_Stationing_Diagram.svg)

*Figure 9.2.5-1 — Two-axis diagram comparing DistanceAlong (geometric distance) and station label for an alignment with one gap equation and one overlap equation.*

### 9.2.6 Example: `DistanceAlong` Conversion with Gap and Overlap Equations

The table below reflects the alignment shown in Figure 9.2.5-1: five points at 200 m intervals along a generic alignment, a gap equation at P3, and an overlap equation at P4. Only P1, P3, and P4 map to actual `IfcReferent` instances (§9.3.1) — P1 as the starting station, P3 and P4 at the equations. P2 and P5 are ordinary points on the alignment with no referent of their own; they appear here only to anchor the geometric spacing.

| Point | $D_i$ (m) | $S_i$ outgoing | `IncomingStation` | Note |
|----------|-----------|----------------|-------------------|------|
| P1 | 0 | 1000.00 (Sta. 10+00) | — | Starting station |
| P2 | 200 | 1200.00 (Sta. 12+00) | — | |
| P3 | 400 | 1700.00 (Sta. 17+00) | 1400.00 (Sta. 14+00) | Gap = 300 |
| P4 | 600 | 1850.00 (Sta. 18+50) | 1900.00 (Sta. 19+00) | Overlap = 50 |
| P5 | 800 | 2050.00 (Sta. 20+50) | — | |

**Between P2 and P3 — Sta. 13+00 (1300.00):**

Last $i$ where $S_i \leq 1300$: P2 ($S_2 = 1200$, $D_2 = 200$).

$$\text{DistanceAlong} = 200 + (1300 - 1200) = 300$$

**Between P3 and P4 — Sta. 18+00 (1800.00):**

Last $i$ where $S_i \leq 1800$: P3 ($S_3 = 1700$, $D_3 = 400$).

$$\text{DistanceAlong} = 400 + (1800 - 1700) = 500$$

**Between P4 and P5 — Sta. 19+25 (1925.00):**

Last $i$ where $S_i \leq 1925$: P4 ($S_4 = 1850$, $D_4 = 600$).

$$\text{DistanceAlong} = 600 + (1925 - 1850) = 675$$

Without accounting for the equations, naive subtraction gives $1925 - 1000 = 925$ — an error of 250 m. The error is the net station inflation introduced by the two equations: the gap at P3 added 300 station units with no corresponding geometry, and the overlap at P4 recovered 50, leaving a net surplus of $300 - 50 = 250$ station units.

**Gap check — Sta. 15+00 (1500.00):**

- P1: $S_1 = 1000 \leq 1500$ ✓
- P2: $S_2 = 1200 \leq 1500$ ✓
- P3: $S_3 = 1700 > 1500$ ✗

Last is P2 ($D_2 = 200$, $S_2 = 1200$). Before computing, check whether the station overshoots the next referent: $S - S_2 = 1500 - 1200 = 300$, but the geometric span to P3 is only $D_3 - D_2 = 400 - 200 = 200$. Since $300 > 200$, Sta. 15+00 falls inside the gap — it was skipped by the forward equation at P3 and `DistanceAlong` is undefined. Any station between Sta. 14+00 and Sta. 16+99 produces the same result.

Implementations must handle this case gracefully — returning an error, `null`, or a domain-specific sentinel value rather than silently producing a geometrically meaningless `DistanceAlong`.

**Overlap ambiguity — Sta. 18+75 (1875.00):**

The overlap zone spans Sta. 18+50 (1850) to Sta. 19+00 (1900) — the range of station values that appear on both the incoming segment (P3→P4) and the outgoing segment (P4→P5). Station 18+75 falls inside this zone and resolves to two distinct geometric points:

*As a point in the P3→P4 segment* (before the equation): last $i$ where $S_i \leq 1875$ ignoring P4 gives P3 ($S_3 = 1700$, $D_3 = 400$):

$$\text{DistanceAlong} = 400 + (1875 - 1700) = 575$$

*As a point in the P4→P5 segment* (after the equation): the algorithm as defined returns P4 ($S_4 = 1850$, $D_4 = 600$):

$$\text{DistanceAlong} = 600 + (1875 - 1850) = 625$$

Both answers are geometrically valid. The algorithm as defined in §9.2.5 always returns the post-equation result (625 m here), silently discarding the pre-equation match. Implementations that need to resolve ambiguous overlap stations must detect the overlap zone — any $S$ where $S_i^{\text{outgoing}} \leq S \leq S_i^{\text{incoming}}$ at an overlap equation referent — and either return both candidate distances or apply project-specific rules to select one.

## 9.3 Attaching Referents to an Alignment

This section covers the **geometric role** of `IfcReferent`: how a referent is nested under, ordered along, and placed on the alignment it belongs to.

### 9.3.1 Defining Stationing in IFC

With the stationing concept established in §9.2, this section describes how it is encoded: `IfcReferent` carries the station value via `Pset_Stationing`, and referents are ordered along the alignment via `IfcRelNests`.

Stationing metadata is stored in `Pset_Stationing`, attached to an `IfcReferent` via `IfcRelDefinesByProperties`. The property set has three properties:

|Property              |Type              |Description                                                                                                                                                                             |
|--------------------|---------------|-------------------------------------------------------------------|
|`Station`             |`IfcLengthMeasure`|The station value at this referent’s location. For the first referent, this defines the starting station of the alignment.                                                              |
|`IncomingStation`     |`IfcLengthMeasure`|Present only at a station equation. The station value on the *incoming* (upstream) side of the break. The `Station` property holds the *outgoing* value immediately after the break.    |
|`HasIncreasingStation`|`IfcBoolean`      |Controls the direction of stationing. If `TRUE` (or absent), subsequently nested referents have increasing station values. If `FALSE`, they decrease. Covers reverse-stationing schemes.|

The `Station` value is expressed in the same units as the project length unit (typically meters or feet), **not** in the `ccc+dd.dd` string form. A station of 142+35.75 ft is stored as `14235.75` with feet as the project unit.

`IfcReferent` instances are connected to their parent `IfcAlignment` through `IfcRelNests`. This relationship has two key properties:

1. **`RelatingObject`** — the `IfcAlignment` (the parent).
1. **`RelatedObjects`** — an ordered list of objects nested within. Referents must appear in the list in order of increasing `DistanceAlong`. This ordering is required by the IFC concept template ([4.1.4.4.3 Object Nesting](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Object_Nesting/content.html)) but is not enforced by a schema WHERE rule. Implementations that read referent data should sort by `DistanceAlong` before processing and not assume the list arrives pre-sorted; implementations that write referent data must produce a sorted list.

The first `IfcReferent` in `RelatedObjects` defines the **starting station** of the alignment. Its `Pset_Stationing.Station` value is the station label at `DistanceAlong = 0.0` of the alignment curve. As a best practice, place this referent at `DistanceAlong = 0.0` so that the station origin and the geometric origin of the alignment coincide.

Figure 9.3.1-1 shows this mechanism populated with the starting-station referent (P1) and the two equation referents (P3, P4) from the §9.2.6 worked example.

![Figure 9.3.1-1 — Entity relationship diagram: IfcAlignment is the RelatingObject of an IfcRelNests relationship whose RelatedObjects list, ordered by DistanceAlong, contains three IfcReferent instances — P1 (start), P3 (gap equation), and P4 (overlap equation) — each carrying a Pset_Stationing property set with values matching the §9.2.6 example.](images/Figure_9.3.1-1_IfcRelNests_Stationing_Mechanism.svg)

*Figure 9.3.1-1 — `IfcRelNests` establishing the stationing order for `IfcReferent` instances P1, P3, and P4, with `Pset_Stationing` values matching the §9.2.6 worked example. P2 and P5 are omitted because they are ordinary points on the alignment, not referents — of the five points in the §9.2.6 example, only P1, P3, and P4 have a corresponding `IfcReferent`.*

### 9.3.2 The Mixed-Nesting Problem

`IfcRelNests` is also used to attach alignment layout components (`IfcAlignmentHorizontal`, `IfcAlignmentVertical`, `IfcAlignmentCant`) to `IfcAlignment`. Both layout sub-objects and referents decompose the same parent through the same relationship type. This creates ambiguity: should layout sub-objects and referents share a single `IfcRelNests` instance, or should they use separate ones?

The IFC specification does not resolve this clearly. Two patterns are seen in practice:

**Pattern A — Shared nest.** A single `IfcRelNests` instance contains both layout objects and referents interleaved or grouped. This works but can make parsing complex, because consumers must distinguish layout objects from referents by type.

**Pattern B — Separate nests (recommended).** Two distinct `IfcRelNests` instances are used: one whose `RelatedObjects` contains only the alignment layout sub-objects, and one whose `RelatedObjects` contains only `IfcReferent` instances.

**Recommendation:** Use Pattern B — separate nests. This is the pattern illustrated in the existing Figure 9.3.2-1 and is more robust for software implementations. The layout nest and the referent nest are independent, and each can be processed without concern for the content of the other.

![Figure 9.3.2-1 — Entity relationship diagram: IfcAlignment uses two separate IfcRelNests relationships — one nesting the alignment layout types (IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant) and a second nesting IfcReferent instances of type STATION carrying Pset_Stationing.](images/Figure_9.3.2-1_Alignment_RelNests_ERD.svg)

*Figure 9.3.2-1 — Two `IfcRelNests` relationships: one for alignment layout sub-objects (horizontal, vertical, cant) and one for `IfcReferent` instances.*

### 9.3.3 `ObjectPlacement` for `IfcReferent`

`IfcReferent` is a subtype of `IfcPositioningElement`, which requires an `ObjectPlacement` (omitting `ObjectPlacement` results in a bSI Validation Service error). Although the schema permits any subtype of `IfcObjectPlacement`, only `IfcLinearPlacement` is practical for referents on an alignment with geometry. `IfcLocalPlacement` and `IfcGridPlacement` carry no `DistanceAlong` value, so a consumer reading a model that uses these placement types has no reliable basis for ordering referents or performing station-to-distance conversions.

Two cases arise in practice:

**Alignment with geometry.** Use `IfcLinearPlacement` with `IfcPointByDistanceExpression` referencing the alignment's horizontal geometric curve. The `DistanceAlong` value establishes the referent's geometric position and is the basis for ordering.

**Semantic-only alignment.** When the alignment carries no geometric representation, `IfcLinearPlacement` cannot be evaluated — there is no basis curve from which to measure distance. Set `IfcReferent.ObjectPlacement` to the same placement instance as `IfcAlignment.ObjectPlacement`. Implementations that later add a geometric representation must update all referent placements accordingly; retaining the copied alignment placement after geometry is added will cause the referent's resolved position to diverge from its geometric intent.

### 9.3.4 Key-Point Referents

Beyond stationing (§9.3.1) and labeling another product's position (§9.4), a third, entirely discretionary use of `IfcReferent` marks the geometric transition points within the alignment's own layout: where a line meets a curve, where one curve type gives way to another, where the layout begins and ends. On a horizontal layout these are the familiar Point of Beginning, Point of Curvature, Point of Tangency, Point of Intersection, and similar transition points; on a vertical layout, the analogous Point of Vertical Curvature, Point of Vertical Tangency, and Point of Vertical Intersection. Modeling these points as referents is a choice, not a requirement — a consumer can always re-derive a transition's station by walking `IfcAlignmentSegment`/`IfcCurveSegment` lengths from the start of the layout. Key-point referents exist purely so that a downstream consumer — a viewer, a plan-production tool, a reviewer opening the model directly — can read these locations and their station labels without performing that walk itself.

**Predefined type and relationship.** A key-point referent identifies the position of a point on the alignment's own geometry — it does not define the alignment's stationing system, so `STATION` (§9.3.1) does not apply. It uses the same `PredefinedType = POSITION` value already introduced in §9.1 for labeling another product's location (elaborated in §9.4.1), but the relationship pattern is different: a key-point referent is related to `IfcAlignment` by `IfcRelNests` (the geometric role, exactly like the `STATION` referent's relationship to `IfcAlignment` in §9.3.1), not by `IfcRelPositions` (the semantic role used in §9.4.1 to label another product). Both flavors of `POSITION` referent carry `Pset_Stationing`; only the relationship distinguishes "this referent marks a point on the alignment's own geometry" from "this referent labels some other product's position."

**Nesting.** [Concept Template 4.1.4.4.3 Object Nesting](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Object_Nesting/content.html) lists `IfcAlignment` as `RelatingObject` for `IfcReferent` `RelatedObjects` — the same pairing already used for the `STATION` referent in §9.3.1.

- **One nest per discipline.** Each applicable discipline — horizontal, vertical, cant — gets its own `IfcRelNests`, `RelatingObject` = `IfcAlignment`, `RelatedObjects` = only that discipline's key-point referents. This is independent of, but structurally identical to, the stationing nest of §9.3.1: several `IfcRelNests` instances can share the same `RelatingObject` (`IfcAlignment`), distinguished only by which referents each one's `RelatedObjects` holds.
- **Possible but discouraged: a single combined nest for all disciplines.** Every horizontal, vertical, and cant key-point referent in one `IfcRelNests.RelatedObjects` list is schema-legal and still `RelatingObject = IfcAlignment`, but it reproduces the same problem Pattern A in §9.3.2 already warned against: a consumer must inspect each referent's placement or label just to determine which discipline it belongs to, rather than being able to read that from the nest itself.

Whichever form is chosen, the key-point nest (or nests) is independent of both the horizontal/vertical/cant layout nest (§9.3.2) and the stationing nest (§9.3.1) — a third category that extends, rather than replaces, the mixed-nesting guidance of §9.3.2: layout sub-objects, key-point referents, and stationing referents all coexist under `IfcAlignment.IsNestedBy`, each in its own `IfcRelNests`.

**A note on Object Nesting and the Alignment-based View MVD.** Concept Template 4.1.4.4.3 is not itself tagged as part of the Alignment-based View (AbV), even though it is the only schema mechanism that establishes alignment stationing (§9.3.1) or key-point referents at all. Apply it regardless — omitting it would leave no conforming way to model stationing or key-point referents on an AbV alignment. (§9.5.2 notes a similar AbV-tagging gap for `IfcConnectionGeometry`.)

**Naming.** `Name` is free-form text, not a schema-constrained enumeration — nothing in IFC fixes the abbreviation vocabulary. The worked example below (§9.3.4.1) uses `"{alignment name} {station string} ({abbreviation})"`, e.g. `"E-Line 119+56.79 (P.C.)"`. Leading with the alignment name makes every referent nested under an alignment identifiable by its name alone, without inspecting its placement or `Pset_Stationing`. The abbreviations are typical of North American highway practice: `P.O.B.`/`P.O.E.` for the layout's start/end, `P.C.`/`P.T.` at line-to-arc and arc-to-line transitions on the horizontal layout, and `V.P.O.B.`/`P.V.C.`/`P.V.T.`/`V.P.O.E.` for the corresponding vertical-layout points. Other jurisdictions and agencies use different abbreviations, additional key-point types (e.g. `P.I.` at a line-to-line deflection, `P.C.C.` at an arc-to-arc transition), or different station-string formats — the guide shows one typical, commonly-seen convention, not a vocabulary implementations must reproduce.

**Placement and properties.** `ObjectPlacement` follows the same two cases already described in §9.3.3: `IfcLinearPlacement`/`IfcPointByDistanceExpression` against the layout's curve when geometry exists, or a placement copied from the alignment itself for a semantic-only layout. Each referent carries `Pset_Stationing` (§9.3.1), giving it a station value in addition to its geometric position. As with other referents in this chapter, no `Representation` is created — placement and property data are sufficient.

Figure 9.3.4-1 shows the nesting pattern.

![Figure 9.3.4-1 — Entity relationship diagram: IfcAlignment as RelatingObject of two independent IfcRelNests instances, each nesting a list of IfcReferent instances of PredefinedType POSITION carrying Pset_Stationing, labeled with example key-point names such as P.O.B., P.C., P.T., P.O.E. (horizontal) and V.P.O.B., P.V.C., P.V.T., V.P.O.E. (vertical).](images/Figure_9.3.4-1_KeyPointReferent_Nesting.svg)

*Figure 9.3.4-1 — Key-point-referent nesting: one `IfcRelNests` per discipline, `RelatingObject` = `IfcAlignment`, `RelatedObjects` = that discipline's `POSITION` referents.*

#### 9.3.4.1 Worked Example: the FHWA E-Line

The FHWA Bridge Geometry Manual E-Line alignment already used as the real-world test case in [Chapter 12](12_Alignment_Geometry_Testset.md#fhwa-bridge-geometry-manual) demonstrates this pattern: [`testset/real-world-alignments/FHWA_Alignment.ifc`](testset/real-world-alignments/FHWA_Alignment.ifc) carries one `IfcRelNests` nested to `IfcAlignment` with eight `POSITION` referents (`E-Line 100+00.00 (P.O.B.)` through `E-Line 223+37.07 (P.O.E.)`, with `P.C.`/`P.T.` pairs at each of the three horizontal curves), and a second `IfcRelNests`, also nested to `IfcAlignment`, with ten `POSITION` referents (`E-Line 100+00.00 (V.P.O.B.)` through `E-Line 228+00.00 (V.P.O.E.)`, with `P.V.C.`/`P.V.T.` pairs at each of the four vertical curves) — independent of, and in addition to, the single starting-station `STATION` referent nested to `IfcAlignment` per §9.3.1. All three nests share `RelatingObject = IfcAlignment`, distinguished only by which referents each one's `RelatedObjects` holds.

## 9.4 Product Positioning

This section covers the **semantic role** of `IfcReferent`: how it semantically labels the position of a product. IFC formalizes two patterns for this under Object Connectivity: **Product Relative Positioning** ([Concept Template 4.1.5.8](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Product_Relative_Positioning/content.html)), which uses a single `IfcReferent` to label one point, and **Product Span Positioning** ([Concept Template 4.1.5.9](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Product_Span_Positioning/content.html)).

It is important to understand that `IfcReferent` serves two distinct roles that must not be conflated:

**Geometric role.** When an `IfcReferent` carries an `IfcLinearPlacement`, it has a precise geometric location on the alignment.

**Semantic role.** An `IfcReferent` can *annotate* the position of another object — not by moving it, but by providing a human-readable label (typically a station) that names its location. This is purely informational metadata.

The geometric location of an infrastructure element (a bridge pier, a sign, a drain inlet) is defined entirely by its own `IfcObjectPlacement`. An associated referent gives that location a name. Removing or changing the referent does not move the object.

### 9.4.1 Product Relative Positioning

The relationship between an `IfcReferent` and the object whose position it annotates is `IfcRelPositions`:

- `RelatingPositioningElement` — the `IfcPositioningElement` providing the semantic position.
- `RelatedProducts` — the `IfcProduct` instances positioned by the `RelatingPositioningElement`.

This is exactly the `IfcRelPositions` pattern defined by [Concept Template 4.1.5.8, Product Relative Positioning](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Product_Relative_Positioning/content.html): one positioning element, one or more related products.

Suppose the alignment's starting station is Sta. 100+00 — that is, the first referent nested under the alignment (§9.3.1) carries `Pset_Stationing.Station = 10000.0` at `DistanceAlong = 0.0`. A bridge pier (`IfcBridgePart.PIER`) is geometrically placed at `DistanceAlong = 14235.75`. Its station label is *not* 14235.75 — it is the starting station plus the distance along: 10000.0 + 14235.75 = 24235.75, i.e., Sta. 242+35.75. An `IfcReferent` with `PredefinedType = POSITION` and `Pset_Stationing.Station = 24235.75` is connected to the pier via `IfcRelPositions`. The pier's station label is now Sta. 242+35.75. The pier's geometry — `DistanceAlong = 14235.75` on its own `IfcLinearPlacement` — is entirely unaffected by the starting station value; only the label changes. However, the semantic position of the pier is incomplete. We know it is at Sta. 242+35.75 but the `IfcReferent` does not inform which alignment that station refers to, nor where that alignment's stationing begins. Two further relationships resolve this. First, the `IfcReferent` that was the `RelatingPositioningElement` for the pier is now itself `RelatedProducts` in a second `IfcRelPositions`, where `IfcAlignment` is the `RelatingPositioningElement`. This ties the pier's referent to the specific alignment it stations. Second, and independently, the alignment's starting-station referent (`Pset_Stationing.Station = 10000.0`, `DistanceAlong = 0.0`) is nested under `IfcAlignment` by `IfcRelNests`, per §9.3.1 — this is what fixes the 10000.0 offset that turns `DistanceAlong = 14235.75` into Sta. 242+35.75. The positioning relationships are shown in Figure 9.4.1-1.

![Figure 9.4.1-1 — Entity relationship diagram: IfcBridgePart.PIER and IfcReferent share the same IfcLinearPlacement. Pset_Stationing (Station = 24235.75) attaches to IfcReferent. IfcRelPositions links the IfcReferent to IfcBridgePart, so the pier is located by its station and offset. A second IfcRelPositions links IfcAlignment to that same IfcReferent. A separate starting-station IfcReferent (Station = 10000.0) is nested under IfcAlignment by IfcRelNests and has its own IfcLinearPlacement at DistanceAlong = 0.0.](images/Figure_9.4.1-1_Referent_Entity_Relationship.svg)

*Figure 9.4.1-1 — Object graph showing an `IfcBridgePart.PIER` with its own `IfcLinearPlacement`, an `IfcReferent` (POSITION type) with `Pset_Stationing`, and the `IfcRelPositions` link between them. To the right, `IfcAlignment` is the `RelatingPositioningElement` for a second `IfcRelPositions` that has the pier's referent as `RelatedProducts`, and a starting-station `IfcReferent` (`Station = 10000.0`) is nested under `IfcAlignment` by `IfcRelNests`, supplying the offset used to derive Sta. 242+35.75 from `DistanceAlong = 14235.75`. Below `IfcRelNests`, that starting-station referent has its own `IfcLinearPlacement` at `DistanceAlong = 0.0`.*

Note the two different relationships an `IfcReferent` can have with the alignment, depending on its role: an `IfcReferent` that *defines* stationing — such as the starting-station referent or a station equation — is related to the `IfcAlignment` with `IfcRelNests`. An `IfcReferent` that *provides the stationing value of another object* — such as the pier's referent — is related to the `IfcAlignment` with `IfcRelPositions`. This is a subtle but important distinction.

### 9.4.2 Product Span Positioning

Some infrastructure elements are not defined by a single point but by a linear extent — a guardrail run, a noise barrier, a pavement marking, a work-zone limit. [Concept Template 4.1.5.9, Product Span Positioning](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Connectivity/Product_Span_Positioning/content.html), covers this case: an `IfcProduct` is positioned relative to *two* `IfcReferent` instances, marking the boundaries of the span, via **two** separate `IfcRelPositions` relationships — one per referent, each with the referent as `RelatingPositioningElement` and the product as `RelatedProducts`.

*Example:* Continuing the alignment from §9.4.1 (starting station Sta. 100+00), a guardrail run (`IfcRailing`) begins at Sta. 240+00 and ends at Sta. 250+00. Two `IfcReferent` instances, each with `PredefinedType = POSITION`, mark these locations, each carrying its own `Pset_Stationing` (`Station = 24000.00` and `Station = 25000.00` respectively) and its own `IfcLinearPlacement`. Toward the `IfcRailing`, Product Span Positioning applies; toward the `IfcAlignment`, Product Relative Positioning applies (§9.4.1). As with the single-point pattern, `Pset_Stationing` values on the span referents are independent of the guardrail's own geometry — moving the guardrail's `IfcLinearPlacement` does not move the referents, and vice versa.

![Figure 9.4.2-1 — Entity relationship diagram: an IfcRailing is positioned by two separate IfcRelPositions relationships. Each RelatingPositioningElement points to a different IfcReferent — a start referent at DistanceAlong 14000.0 with Pset_Stationing Station = 24000.00, and an end referent at DistanceAlong 15000.0 with Pset_Stationing Station = 25000.00. Both IfcRelPositions instances have the IfcRailing as RelatedProducts. A third IfcRelPositions has IfcAlignment as RelatingPositioningElement and both the start and end IfcReferent together as RelatedProducts.](images/Figure_9.4.2-1_Product_Span_Positioning.svg)

*Figure 9.4.2-1 — Two concept templates combined: Product Span Positioning (two `IfcRelPositions` relationships linking the `IfcRailing` to its start and end `IfcReferent` instances) and Product Relative Positioning (a single `IfcRelPositions` linking both referents to the `IfcAlignment` they are stationed against).*

## 9.5 The `INTERSECTION` Referent

An `IfcReferent` with `PredefinedType = INTERSECTION` marks the point where two or more routes cross. A single crossing uses **two** `IfcReferent` instances of type `INTERSECTION`, one per intersecting alignment, each related to its own single owning alignment by `IfcRelPositions`. That referent pattern (§9.5.1) only ever names a station on one alignment — it is not, by itself, a record that the two alignments cross. This section works through two related but distinct questions: how each `INTERSECTION` referent is owned (§9.5.1), and how the crossing itself — a fact about the two facilities, established independently of any referent — is recorded with `IfcRelInterferesElements` (§9.5.2).

### 9.5.1 Referent Ownership: One Referent Per Alignment

In each case, the `IfcRelPositions` has that `IfcAlignment` as `RelatingPositioningElement` and the referent as `RelatedProducts` — the same alignment-link pattern used for the `POSITION` referent's second `IfcRelPositions` in §9.4.1 — and each referent carries its own `Pset_Stationing.Station` value in its owning alignment's stationing. This interpretation follows directly from ISO 19148 §6.2.12.1, which IFC's linear referencing model is built on (§8.6):

> Referents are owned by a single feature. For example, the reference markers along Interstate 95 are owned by the feature that represents Interstate 95. The referent representing the intersection with First Avenue along Washington Street is owned by Washington Street if it is used to specify relative linearly referenced locations along Washington Street. The location of this referent is most likely specified with a position expression along Washington Street. A different referent can represent the intersection with Washington Street along First Avenue. This referent is owned by First Avenue and is used to specify relative linearly referenced locations along First Avenue.

Applied to that example: Washington Street's `INTERSECTION` referent is placed via `IfcLinearPlacement`/`DistanceAlong` on Washington Street's curve, carries `Pset_Stationing.Station = 1000.00` (Sta. 10+00) in Washington Street's stationing, and is related to `IfcAlignment` — Washington Street by its own `IfcRelPositions`. First Avenue's `INTERSECTION` referent is an entirely separate instance: placed on First Avenue's own curve, carrying `Pset_Stationing.Station = 1200.00` (Sta. 12+00) in First Avenue's stationing, and related to `IfcAlignment` — First Avenue by a second, independent `IfcRelPositions`. Figure 9.5-1 shows the two independent object graphs.

![Figure 9.5-1 — Entity relationship diagram: two independent IfcReferent instances of PredefinedType INTERSECTION, each related to a different IfcAlignment via its own IfcRelPositions. Left: IfcAlignment "Washington Street" is RelatingPositioningElement of an IfcRelPositions whose RelatedProducts is an IfcReferent (INTERSECTION) placed on Washington Street's own curve, carrying Pset_Stationing Station = 1000.00 (Sta. 10+00). Right: IfcAlignment "First Avenue" is RelatingPositioningElement of a separate IfcRelPositions whose RelatedProducts is a second, independent IfcReferent (INTERSECTION) placed on First Avenue's own curve, carrying Pset_Stationing Station = 1200.00 (Sta. 12+00). Nothing connects the two graphs.](images/Figure_9.5-1_Intersection_Referent_Ownership.svg)

*Figure 9.5-1 — Two independent `INTERSECTION` referents, each related to its own alignment by its own `IfcRelPositions`, following the same alignment-link pattern as the `POSITION` referent in Figure 9.4.1-1 — applied once per alignment rather than shared between two. Nothing in this graph connects the two referents or the two alignments; the fact that they cross is established separately, in §9.5.2.*

This pattern scales to a multi-leg intersection without modification — one `INTERSECTION` referent per crossing alignment.

### 9.5.2 `IfcRelInterferesElements`: Recording That Two Facilities Cross

The referent and the `IfcRelPositions` instance that ties it to its owning alignment (§9.5.1) do exactly one thing: they give a *name* — a station — to a location on one alignment. Neither asserts anything about the alignment on the other side of the crossing. It is easy to misread two `INTERSECTION` referents at coincident locations as if that, by itself, recorded "these two roads cross," but nothing in §9.5.1 relates Washington Street's referent to First Avenue's, or either referent to the other alignment. Whether the crossing needs to be recorded as queryable schema data — as distinct from a fact two engineers can see on a plan sheet — is answered by a relationship that has nothing to do with referents or stationing: `IfcRelInterferesElements`.

`IfcRelInterferesElements` (a subtype of `IfcRelConnects`) is an objectified relationship stating that two elements interfere, physically or logically, independent of either element's own definition. Its attributes:

- `RelatingElement`, `RelatedElement` — typed `IfcInterferenceSelect`, meaning each must be a subtype of `IfcElement` or of `IfcSpatialElement`.
- `InterferenceGeometry` — optional `IfcConnectionGeometry`, the shape of the interference itself, expressed in `RelatingElement`'s object coordinate system.
- `InterferenceType` — optional `IfcIdentifier`. This is free text, **not a restricted enumeration** — the schema documentation offers values like `Crosses`, `PassesOver`, `PassesUnder`, `PassesThrough`, `Along`, and `Clash` only as examples a project might adopt as a convention, not as a fixed value list IFC enforces.
- `ImpliedOrder` — `IfcLogical`, indicating whether `RelatingElement` should be read as a source and `RelatedElement` as a target for the chosen `InterferenceType` (meaningful for a directional type like `PassesOver`; not meaningful for an undirected `Clash`).
- `InterferenceSpace` — optional `IfcSpatialZone`, the space in which the interference occurs.

**`IfcAlignment` cannot itself be a party to this relationship.** `IfcAlignment` is a subtype of `IfcPositioningElement` (via `IfcLinearPositioningElement`), not of `IfcElement` or `IfcSpatialElement` — the only two branches `IfcInterferenceSelect` accepts. That follows from what an alignment *is* in this schema: a positioning/reference curve, not a physical or spatial occurrence. What can carry the relationship is whatever `IfcElement` or `IfcSpatialElement` the alignment describes the layout of — typically the `IfcRoad` or `IfcRailway` facility the alignment lays out, or, where the crossing needs to be tied to a specific occurrence rather than the facility as a whole, a physical element such as a pavement course or a bridge structure.

The facility does not *aggregate* the alignment, either. `IfcAlignment` is conventionally aggregated directly under `IfcProject` (per the concept template in IFC 4.1.4.1.1, Alignment Aggregation To Project), and the bSI Validation Service's SPS002 rule (Correct spatial breakdown) restricts what `IfcRelAggregates` may nest under an `IfcRoad` to other facility/space-type entities — `IfcAlignment` is not among them, so aggregating an alignment under a road fails validation. Instead, the road references its alignment with `IfcRelReferencedInSpatialStructure` — the same non-hierarchical relationship used elsewhere for an element that logically belongs to more than one spatial structure (§9.3, e.g. a multi-storey column) — with the `IfcRoad` as `RelatingStructure` and the `IfcAlignment` as one of its `RelatedElements`.

*Example, continuing §9.5.1:* Washington Street and First Avenue are each modeled as an `IfcRoad`, each referencing its respective `IfcAlignment` (which remains aggregated under `IfcProject`). The at-grade crossing is recorded independently of either `INTERSECTION` referent:

- `RelatingElement` = Washington Street (`IfcRoad`)
- `RelatedElement` = First Avenue (`IfcRoad`)
- `InterferenceType` = `"Crosses"`
- `ImpliedOrder` = `FALSE` — an at-grade crossing has no source/target direction

Figure 9.5.2-1 shows this alongside the `IfcRelReferencedInSpatialStructure` that ties each `IfcRoad` to its `IfcAlignment`.

![Figure 9.5.2-1 — Entity relationship diagram: IfcRelInterferesElements recording that two IfcRoad facilities cross, independent of the IfcAlignment instances each lays out. Left: an IfcRoad "Washington Street" is RelatingStructure of an IfcRelReferencedInSpatialStructure whose RelatedElements includes an IfcAlignment "Washington Street". Right: an IfcRoad "First Avenue" is RelatingStructure of a separate IfcRelReferencedInSpatialStructure whose RelatedElements includes the IfcAlignment "First Avenue". Center: a single IfcRelInterferesElements has RelatingElement = the Washington Street IfcRoad and RelatedElement = the First Avenue IfcRoad, with InterferenceType = "Crosses" and ImpliedOrder = FALSE. The interference relates the two IfcRoad facilities directly; it does not reference either IfcAlignment or either INTERSECTION referent from Figure 9.5-1.](images/Figure_9.5.2-1_IfcRelInterferesElements.svg)

*Figure 9.5.2-1 — A single `IfcRelInterferesElements` relating the two `IfcRoad` facilities. Each facility separately references the `IfcAlignment` that lays it out via `IfcRelReferencedInSpatialStructure`, not `IfcRelAggregates` — the alignments themselves are outside the interference relationship, since `IfcInterferenceSelect` does not accept `IfcPositioningElement`.*

This `IfcRelInterferesElements` instance is what lets software ask "does Washington Street cross another facility, and which one?" without parsing referents or comparing coordinates. It complements, but does not replace, the two `INTERSECTION` referents from §9.5.1: the referents answer "at what station," which `IfcRelInterferesElements` does not carry, while `IfcRelInterferesElements` answers "is this a real, queryable crossing," which the referents do not assert. The two relationships never reference each other. A model can legitimately have `INTERSECTION` referents with no corresponding `IfcRelInterferesElements` (the crossing is only implied by proximity — common in low-detail concept models), or an `IfcRelInterferesElements` instance with no referents yet (the crossing is flagged before it has been given a station label).

A grade-separated (multi-level) crossing — a road passing over another road, or over a railway — is recorded the same way, but with a directional `InterferenceType` and `ImpliedOrder = TRUE`: `InterferenceType = "PassesOver"`, `RelatingElement` = the facility physically above, `RelatedElement` = the facility below. Nothing about the two `INTERSECTION` referents changes between the at-grade and grade-separated cases — both still use the identical `PredefinedType = INTERSECTION` and carry no elevation information of their own — so `IfcRelInterferesElements` is also the only place in the model that distinguishes an at-grade crossing from a grade-separated one.

Two example files demonstrate this pattern:

- [`IntersectionReferent_AtGradeCrossing.ifc`](examples/IntersectionReferent_AtGradeCrossing.ifc) — two alignments crossing at a true 3D intersection, each referenced by its own `IfcRoad`; a single `IfcRelInterferesElements` between the two roads carries `InterferenceType = "Crosses"`, `ImpliedOrder = FALSE`, and an `IfcConnectionPointGeometry` `InterferenceGeometry` built from the same two `IfcPointByDistanceExpression` instances already used by the `INTERSECTION` referents' own placements, rather than duplicating the location as new `IfcCartesianPoint`s.
- [`IntersectionReferent_GradeSeparatedCrossing.ifc`](examples/IntersectionReferent_GradeSeparatedCrossing.ifc) — the same plan-view crossing, but with one alignment's grade reversed so the two roads no longer meet in 3D; the `IfcRelInterferesElements` between them carries `InterferenceType = "PassesOver"`, `ImpliedOrder = TRUE`, and an `IfcConnectionPointEccentricity` `InterferenceGeometry` — the same two reused points, plus `EccentricityInZ` recording the 30 ft vertical separation between them.

**A note on `InterferenceGeometry` and the Alignment-based View MVD.** [`IfcConnectionGeometry`](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcConnectionGeometry.htm) is tagged as part of the Alignment-based View (AbV), but it is abstract, and none of its five concrete descendants — including `IfcConnectionPointGeometry` and `IfcConnectionPointEccentricity`, used above — carry that tag themselves, the same kind of AbV-tagging gap noted for Object Nesting in §9.3.4. The two example files were checked against the bSI Validation Service and were not flagged as non-conforming to AbV.

## 9.6 Summary and Implementation Checklist

|# |Item                                                                                                                                                      |Notes                                                                                   |
|-----|-----------------------------------------------|------------------------------------------------|
|1 |Use `IfcReferent` to attach station labels and other semantic location information to alignment positions.                                                |Referents are informational overlays on geometry, not geometry themselves.              |
|2 |Store the station value in `Pset_Stationing.Station` as a plain `IfcLengthMeasure` in project length units.                                               |Do not store the `ccc+dd.dd` string — compute it from the numeric value when displaying.|
|3 |Set `Pset_Stationing.HasIncreasingStation = FALSE` only for reverse-stationing schemes.                                                                   |When absent or `TRUE`, stationing increases in the direction of the alignment.          |
|4 |At a station equation, provide both `IncomingStation` and `Station` on the same referent.                                                                 |`IncomingStation` = upstream label; `Station` = downstream label.                       |
|5 |Do not convert station labels to `DistanceAlong` by simple subtraction. For each referent record $D_i$ and outgoing $S_i$; find the last $i$ where $S_i \leq S$; then `DistanceAlong` $= D_i + (S - S_i)$.|See §9.2.5 for the full algorithm.                                                      |
|6 |Before applying the conversion formula, check for a gap: if $S - S_i > D_{i+1} - D_i$, the station was skipped by a forward equation and `DistanceAlong` is undefined.|Return an error or sentinel value — do not silently produce a meaningless distance. See §9.2.6.|
|7 |Stations in an overlap zone map to two geometric points. Detect the zone ($S_i^{\text{outgoing}} \leq S \leq S_i^{\text{incoming}}$ at an overlap referent) and either return both candidates or apply project rules to select one.|See §9.2.6.                                                                             |
|8 |Use separate `IfcRelNests` instances for alignment layout sub-objects and referents.                                                                      |Mixing them in a single nest is allowed but makes parsing harder.                       |
|9 |Order referents in `IfcRelNests.RelatedObjects` by increasing `DistanceAlong`.                                                                            |Required by the nesting concept template; sort defensively when reading.                |
|10|Place the first referent at `DistanceAlong = 0.0` and set `Pset_Stationing.Station` to the starting station value.                                        |Commonly a round number like 1000.00 (Sta. 10+00). For semantic-only alignments, `ObjectPlacement` = alignment's placement; for geometric alignments, use `IfcLinearPlacement` at distance 0. Update when adding geometry.|
|11|Use `IfcRelPositions` to link a referent to the object(s) whose station it names.                                                                         |This is semantic annotation only; it does not affect geometry.                          |
|12|An `IfcReferent` that provides stationing should itself be linked to its `IfcAlignment` via `IfcRelPositions`, with `IfcAlignment` as `RelatingPositioningElement` and the referent as `RelatedProducts`.|Without this link, a station label is ambiguous — nothing states which alignment's stationing it belongs to. See §9.4.1, §9.4.2.|
|13|For linear-extent elements (guardrails, barriers, work-zone limits) spanning between two referents, link the product to each referent with its own `IfcRelPositions` (Product Span Positioning, Concept Template 4.1.5.9).|Toward the alignment, several referents share a single `IfcRelPositions` under Product Relative Positioning (§9.4.1). See §9.4.2.|
|14|Model an intersection as **one `INTERSECTION` referent per crossing alignment** (two for a simple crossing, more for a multi-leg intersection), each with its own `IfcRelPositions` to its own alignment and its own `Pset_Stationing.Station`.|Do not link one shared referent to multiple alignments — `Pset_Stationing` holds only one `Station` value. Per ISO 19148 §6.2.12.1. See §9.5.1.|
|15|Record the crossing itself — as a fact about the two facilities, independent of either `INTERSECTION` referent — with a single `IfcRelInterferesElements` relating the two `IfcRoad`/`IfcRailway` (or other `IfcElement`/`IfcSpatialElement`) instances the alignments lay out.|`IfcAlignment` cannot be `RelatingElement`/`RelatedElement` — `IfcInterferenceSelect` accepts only `IfcElement` or `IfcSpatialElement`, and `IfcAlignment` is `IfcPositioningElement`. `InterferenceType` is a free-text `IfcIdentifier`, not an enumeration. Use `ImpliedOrder = TRUE` with a directional type (e.g. `PassesOver`) for grade separations; `FALSE` for an undirected at-grade `Crosses`. See §9.5.2.|
|16|Keep `IfcAlignment` aggregated under `IfcProject`; link a facility (`IfcRoad`/`IfcRailway`) to the alignment it lays out with `IfcRelReferencedInSpatialStructure` (facility as `RelatingStructure`, alignment as one of `RelatedElements`), not `IfcRelAggregates`.|The bSI Validation Service's SPS002 rule (Correct spatial breakdown) restricts what `IfcRelAggregates` may nest under an `IfcRoad`/`IfcRailway` to other facility/space-type entities; `IfcAlignment` is not among them, and aggregating it under a facility fails validation. See §9.5.2.|
|17|Model `InterferenceGeometry` with a concrete `IfcConnectionGeometry` subtype — `IfcConnectionPointGeometry` for a coincident point, `IfcConnectionPointEccentricity` when the two points differ (e.g. the vertical offset at a grade separation) — reusing the alignments' existing `IfcPointByDistanceExpression` points rather than duplicating coordinates as new `IfcCartesianPoint`s.|`PointOnRelatingElement`/`PointOnRelatedElement` accept any `IfcPoint`, including an already-built `IfcPointByDistanceExpression`. See §9.5.2.|
|18|Don't be alarmed that none of `IfcConnectionGeometry`'s concrete subtypes are individually tagged Alignment-based View (AbV) — only the abstract supertype is.|A documentation ambiguity in the MVD, not a modeling error; confirmed against the bSI Validation Service on this guide's example files. See §9.5.2.|
|19|Key-point referents (P.C., P.T., and similar segment-transition markers) are optional. When used, give them `PredefinedType = POSITION` and relate them with `IfcRelNests`, one nest per applicable discipline, `RelatingObject = IfcAlignment` — not `IfcRelPositions`, and not `STATION`.|`POSITION` here does not mean the same relationship as the product-labeling `POSITION` referent of §9.4.1 — same enum value, different relationship. See §9.3.4.|
|20|Don't be alarmed that Concept Template 4.1.4.4.3 (Object Nesting) isn't itself tagged Alignment-based View (AbV) — apply it anyway for stationing and key-point referents.|A gap in the MVD's tagging, not a reason to avoid the concept template; the same kind of gap noted for `IfcConnectionGeometry` in item 18. See §9.3.4.|
|21|Treat the abbreviation text used in a key-point referent's `Name` as a display convention, not a schema enumeration.|The guide's worked example uses a typical North American convention; other jurisdictions/agencies may use different abbreviations or additional key-point types. See §9.3.4.|
