# Chapter 9 — Referents and Stationing

## 9.0 Introduction

Chapter 8 established that `IfcPointByDistanceExpression.DistanceAlong` is a **geometric distance** — a raw arc-length measure from the start of a curve. But civil engineering practice does not communicate location this way. Engineers say “Pier 3 is at Station 14+235.75,” not “Pier 3 is 14,235.75 meters from the start of the survey baseline.” The station label is a human-readable, project-specific identifier that may begin at an arbitrary value, may use different units than the project, and may not even progress continuously along the alignment.

`IfcReferent` is the IFC mechanism that bridges these two worlds. It is a positioned object that attaches semantic location information — most importantly, stationing — to a specific geometric point on an alignment. It does not change the geometry; it annotates it.

This section covers:

- What `IfcReferent` is and the range of uses it serves beyond stationing.
- How stationing is expressed using `Pset_Stationing`, and how station values relate to geometric distances.
- Station equations: gap and overlap breaks, their physical causes, and how they affect `DistanceAlong` conversions.
- How referents are nested to alignments using `IfcRelNests`, including the recommended approach for mixed nesting with alignment layouts.
- How `IfcReferent` informs the semantic position of other objects via `IfcRelPositions`, without affecting their geometry.

## 9.1 What Is a Referent?

`IfcReferent` is a subtype of `IfcPositioningElement`, which is itself a subtype of `IfcProduct`. Like any product, it has an `ObjectPlacement` (typically `IfcLinearPlacement`) that locates it geometrically on an alignment, and it can carry property sets that provide additional semantic information at that location.

The single attribute `IfcReferent` adds beyond its supertypes is `PredefinedType` (`IfcReferentTypeEnum`), which guides receivers on how to interpret the referent and which property sets are relevant:

- **Stationing / chainage** (`STATION`). The most common use. Marks a position with a human-readable station label, defines the alignment's starting station or records a station equation.
- **Linear referencing events** (`SUPERELEVATIONEVENT`, `WIDTHEVENT`). Locations where a design parameter changes — superelevation transitions, width changes, and similar cross-section events.
- **Reference markers and mileposts** (`REFERENCEMARKER`, `KILOPOINT`, `MILEPOINT`). Physical objects in the right-of-way that are part of a real-world linear referencing system.
- **Administrative boundaries** (`BOUNDARY`). Locations where a jurisdiction, maintenance zone, or asset ownership boundary crosses the alignment.
- **Intersection locations** (`INTERSECTION`). Points where another road or route crosses the alignment.
- **General positioned location** (`POSITION`). A fully described linearly referenced location combining alignment, LRM, and measure value.

## 9.2 Stationing: Concept and Practice

### 9.2.1 What Is a Station?

Stationing (also called *chainage* in British practice) is a distance-based coordinate system used to identify locations along a linear route. In North American highway practice, stations are expressed in the form `ccc+dd.dd`, where the number before the `+` is the count of hundreds of feet (or hundreds of meters in metric projects) and the digits after are the remainder. For example, Sta. 142+35.75 means 14,235.75 feet (or meters) from the project datum.

The project datum — the zero point of stationing — is defined by the first `IfcReferent` nested in the alignment (see §9.4). Stationing typically begins at a round number such as 10+00 or 100+00 rather than 0+00, to avoid negative stations at points that may be surveyed upstream of the formal project start.

Stationing is a **display convention**, not a geometric quantity. The geometric position of a point is fully determined by `DistanceAlong` in `IfcPointByDistanceExpression`. The station label is metadata that identifies that point to engineers and field crews in human-readable terms.

### 9.2.2 Pset_Stationing

Stationing metadata is stored in `Pset_Stationing`, attached to an `IfcReferent` via `IfcRelDefinesByProperties`. The property set has three properties:

|Property              |Type              |Description                                                                                                                                                                             |
|--------------------|---------------|-------------------------------------------------------------------|
|`Station`             |`IfcLengthMeasure`|The station value at this referent’s location. For the first referent, this defines the starting station of the alignment.                                                              |
|`IncomingStation`     |`IfcLengthMeasure`|Present only at a station equation. The station value on the *incoming* (upstream) side of the break. The `Station` property holds the *outgoing* value immediately after the break.    |
|`HasIncreasingStation`|`IfcBoolean`      |Controls the direction of stationing. If `TRUE` (or absent), subsequently nested referents have increasing station values. If `FALSE`, they decrease. Covers reverse-stationing schemes.|

The `Station` value is expressed in the same units as the project length unit (typically meters or feet), **not** in the `ccc+dd.dd` string form. A station of 142+35.75 ft is stored as `14235.75` with feet as the project unit.

## 9.3 Station Equations: Gaps and Overlaps

### 9.3.1 Why Station Equations Exist

A station equation (also called a *chainage break* or *stationing equation*) is a discontinuity in the stationing system at which the station value jumps. Equations arise in several common situations:

**Realignment.** When a road is realigned — a curve is straightened or a new bypass is built — the new alignment geometry is a different length than the old. Rather than re-station the entire project downstream of the change (which would invalidate all existing plan sheets, permits, and as-built records), engineers introduce a station equation at the point where the old and new alignments reconnect. The geometry changes; the stationing on the downstream portion is preserved.

**Survey accumulation.** Long routes are often surveyed in segments. Small differences in measurement between survey crews produce a gap or overlap at the junction point. Rather than re-survey everything, an equation is introduced.

**Existing route adoption.** When a new project ties into an existing road with its own stationing, an equation reconciles the two stationing systems at the junction.

### 9.3.2 Gap Equations

A **gap equation** (also called a *station ahead* or *forward equation*) occurs when stationing jumps forward. The alignment geometry is continuous, but the station number increases by more than the physical length at the equation point.

*Example:* The alignment arrives at a point with incoming station 142+35.75. Due to a realignment that shortened the route, the outgoing station is 145+00.00. There is a gap of 264.25 ft. A distance of 14,235.75 ft of geometry corresponds to a label of 145+00, not 142+35.75.

![Figure 9.3.2-1 — Station gap equation: incoming alignment arrives at Sta. 142+35.75, the equation point jumps forward to Sta. 145+00.00, with a GAP annotation showing 264.25 ft of stationing skipped. The outgoing alignment continues to the right with an arrow.](images/Figure_9.3.2-1_Gap_Equation.svg)

*Figure 9.3.2-1 — Station gap equation. Geometry is continuous; station numbers jump forward.*

### 9.3.3 Overlap Equations

An **overlap equation** (also called a *station back* or *backward equation*) occurs when stationing jumps backward. The alignment geometry is continuous, but the station number decreases at the equation point.

*Example:* Incoming station 78+42.10, outgoing station 76+00.00. There is an overlap of 242.10 ft. Two different geometric points — one upstream and one downstream of the equation — carry station labels between 76+00 and 78+42.

![Figure 9.3.3-1 — Station overlap equation: incoming alignment arrives at Sta. 78+42.10, the equation point jumps backward to Sta. 76+00.00, with an OVERLAP annotation showing 242.10 ft of station range used twice. The outgoing alignment continues to the right with an arrow.](images/Figure_9.3.3-1_Overlap_Equation.svg)

*Figure 9.3.3-1 — Station overlap equation. Geometry is continuous; station numbers jump backward.*

### 9.3.4 Effect on `DistanceAlong` Conversion

The presence of station equations means that **you cannot convert a station label to `DistanceAlong` by simple subtraction of the starting station**. You must account for every equation encountered between the alignment start and the point of interest.

The conversion algorithm is:

1. Sort all referents on the alignment by `DistanceAlong`. For each referent record two values:
    - $D_i$: the `DistanceAlong` read directly from its `IfcLinearPlacement`
    - $S_i$: the outgoing station — `Pset_Stationing.Station`
1. *(Optional validation)* For any referent that also carries `IncomingStation`, verify that $S_{i-1} + (D_i - D_{i-1}) \approx \text{IncomingStation}$. This confirms that the station count in the preceding segment matches the geometry.
1. To convert a target station $S$ to `DistanceAlong`, find the last referent $i$ such that $S_i \leq S$. Then:

$$\text{DistanceAlong} = D_i + (S - S_i)$$

Before applying the formula, check whether the station overshoots the next referent: if a next referent exists and $S - S_i > D_{i+1} - D_i$, the station falls inside a gap — it was skipped by a forward equation — and `DistanceAlong` is undefined.

Figure 9.3.4-1 illustrates how the geometric distance axis and the station label axis diverge when equations are present.

![Figure 9.3.4-1 — Two-panel diagram. Top: uniform geometric distance axis with five referents R₁–R₅ at 200 m spacing. Bottom: station label axis for the same referents, with a station equation gap at R₃ (red — back station less than forward station) and an overlap at R₄ (green — back station greater than forward station), illustrating how station equations introduce discontinuities in the labeling axis.](images/Figure_9.3.4-1_Stationing_Diagram.svg)

*Figure 9.3.4-1 — Two-axis diagram comparing DistanceAlong (geometric distance) and station label for an alignment with one gap equation and one overlap equation.*

### 9.3.5 Example: `DistanceAlong` Conversion with Gap and Overlap Equations

The table below reflects the alignment shown in Figure 9.3.4-1: five referents at 200 m intervals, a gap equation at R3, and an overlap equation at R4.

| Referent | $D_i$ (m) | $S_i$ outgoing | `IncomingStation` | Note |
|----------|-----------|----------------|-------------------|------|
| R1 | 0 | 1000.00 (Sta. 10+00) | — | Starting station |
| R2 | 200 | 1200.00 (Sta. 12+00) | — | |
| R3 | 400 | 1700.00 (Sta. 17+00) | 1400.00 (Sta. 14+00) | Gap = 300 |
| R4 | 600 | 1850.00 (Sta. 18+50) | 1900.00 (Sta. 19+00) | Overlap = 50 |
| R5 | 800 | 2050.00 (Sta. 20+50) | — | |

**Between R2 and R3 — Sta. 13+00 (1300.00):**

Last $i$ where $S_i \leq 1300$: R2 ($S_2 = 1200$, $D_2 = 200$).

$$\text{DistanceAlong} = 200 + (1300 - 1200) = 300$$

**Between R3 and R4 — Sta. 18+00 (1800.00):**

Last $i$ where $S_i \leq 1800$: R3 ($S_3 = 1700$, $D_3 = 400$).

$$\text{DistanceAlong} = 400 + (1800 - 1700) = 500$$

**Between R4 and R5 — Sta. 19+25 (1925.00):**

Last $i$ where $S_i \leq 1925$: R4 ($S_4 = 1850$, $D_4 = 600$).

$$\text{DistanceAlong} = 600 + (1925 - 1850) = 675$$

Without accounting for the equations, naive subtraction gives $1925 - 1000 = 925$ — an error of 250 m. The error is the net station inflation introduced by the two equations: the gap at R3 added 300 station units with no corresponding geometry, and the overlap at R4 recovered 50, leaving a net surplus of $300 - 50 = 250$ station units.

**Gap check — Sta. 15+00 (1500.00):**

- R1: $S_1 = 1000 \leq 1500$ ✓
- R2: $S_2 = 1200 \leq 1500$ ✓
- R3: $S_3 = 1700 > 1500$ ✗

Last is R2 ($D_2 = 200$, $S_2 = 1200$). Before computing, check whether the station overshoots the next referent: $S - S_2 = 1500 - 1200 = 300$, but the geometric span to R3 is only $D_3 - D_2 = 400 - 200 = 200$. Since $300 > 200$, Sta. 15+00 falls inside the gap — it was skipped by the forward equation at R3 and `DistanceAlong` is undefined. Any station between Sta. 14+00 and Sta. 16+99 produces the same result.

Implementations must handle this case gracefully — returning an error, `null`, or a domain-specific sentinel value rather than silently producing a geometrically meaningless `DistanceAlong`.

**Overlap ambiguity — Sta. 18+75 (1875.00):**

The overlap zone spans Sta. 18+50 (1850) to Sta. 19+00 (1900) — the range of station values that appear on both the incoming segment (R3→R4) and the outgoing segment (R4→R5). Station 18+75 falls inside this zone and resolves to two distinct geometric points:

*As a point in the R3→R4 segment* (before the equation): last $i$ where $S_i \leq 1875$ ignoring R4 gives R3 ($S_3 = 1700$, $D_3 = 400$):

$$\text{DistanceAlong} = 400 + (1875 - 1700) = 575$$

*As a point in the R4→R5 segment* (after the equation): the algorithm as defined returns R4 ($S_4 = 1850$, $D_4 = 600$):

$$\text{DistanceAlong} = 600 + (1875 - 1850) = 625$$

Both answers are geometrically valid. The algorithm as defined in §9.3.4 always returns the post-equation result (625 m here), silently discarding the pre-equation match. Implementations that need to resolve ambiguous overlap stations must detect the overlap zone — any $S$ where $S_i^{\text{outgoing}} \leq S \leq S_i^{\text{incoming}}$ at an overlap equation referent — and either return both candidate distances or apply project-specific rules to select one.

## 9.4 Nesting Referents to Alignments

### 9.4.1 IfcRelNests

`IfcReferent` instances are connected to their parent `IfcAlignment` through `IfcRelNests`. This relationship has two key properties:

1. **`RelatingObject`** — the `IfcAlignment` (the parent).
1. **`RelatedObjects`** — an ordered list of objects nested within. Referents must appear in the list in order of increasing `DistanceAlong`. This ordering is required by the IFC concept template ([4.1.4.4.3 Object Nesting](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Object_Nesting/content.html)) but is not enforced by a schema WHERE rule. Implementations that read referent data should sort by `DistanceAlong` before processing and not assume the list arrives pre-sorted; implementations that write referent data must produce a sorted list.

The first `IfcReferent` in `RelatedObjects` defines the **starting station** of the alignment. Its `Pset_Stationing.Station` value is the station label at `DistanceAlong = 0.0` of the alignment curve. As a best practice, place this referent at `DistanceAlong = 0.0` so that the station origin and the geometric origin of the alignment coincide.

### 9.4.2 The Mixed-Nesting Problem

`IfcRelNests` is also used to attach alignment layout components (`IfcAlignmentHorizontal`, `IfcAlignmentVertical`, `IfcAlignmentCant`) to `IfcAlignment`. Both layout sub-objects and referents decompose the same parent through the same relationship type. This creates ambiguity: should layout sub-objects and referents share a single `IfcRelNests` instance, or should they use separate ones?

The IFC specification does not resolve this clearly. Two patterns are seen in practice:

**Pattern A — Shared nest.** A single `IfcRelNests` instance contains both layout objects and referents interleaved or grouped. This works but can make parsing complex, because consumers must distinguish layout objects from referents by type.

**Pattern B — Separate nests (recommended).** Two distinct `IfcRelNests` instances are used: one whose `RelatedObjects` contains only the alignment layout sub-objects, and one whose `RelatedObjects` contains only `IfcReferent` instances.

**Recommendation:** Use Pattern B — separate nests. This is the pattern illustrated in the existing Figure 9.4.2-1 and is more robust for software implementations. The layout nest and the referent nest are independent, and each can be processed without concern for the content of the other.

![Figure 9.4.2-1 — Entity relationship diagram: IfcAlignment uses two separate IfcRelNests relationships — one nesting the alignment layout types (IfcAlignmentHorizontal, IfcAlignmentVertical, IfcAlignmentCant) and a second nesting IfcReferent instances of type STATION carrying Pset_Stationing.](images/Figure_9.4.2-1_Alignment_RelNests_ERD.svg)

*Figure 9.4.2-1 — Two `IfcRelNests` relationships: one for alignment layout sub-objects (horizontal, vertical, cant) and one for `IfcReferent` instances.*

### 9.4.3 ObjectPlacement for IfcReferent

`IfcReferent` is a subtype of `IfcPositioningElement`, which requires an `ObjectPlacement`. Although the schema permits any subtype of `IfcObjectPlacement`, only `IfcLinearPlacement` is practical for referents on an alignment with geometry. `IfcLocalPlacement` and `IfcGridPlacement` carry no `DistanceAlong` value, so a consumer reading a model that uses these placement types has no reliable basis for ordering referents or performing station-to-distance conversions.

Three cases arise in practice:

**Alignment with geometry.** Use `IfcLinearPlacement` with `IfcPointByDistanceExpression` referencing the alignment's horizontal geometric curve. The `DistanceAlong` value establishes the referent's geometric position and is the basis for ordering.

**Semantic-only alignment.** When the alignment carries no geometric representation, `IfcLinearPlacement` cannot be evaluated — there is no basis curve from which to measure distance. Set `IfcReferent.ObjectPlacement` to the same placement instance as `IfcAlignment.ObjectPlacement`. Implementations that later add a geometric representation must update all referent placements accordingly; retaining the copied alignment placement after geometry is added will cause the referent's resolved position to diverge from its geometric intent.

**`INTERSECTION` referents.** An `IfcReferent` with `PredefinedType = INTERSECTION` marks the point where two or more routes cross. Because the intersection is geometrically meaningful on all of the crossing alignments, the choice of which alignment's curve serves as the `BasisCurve` in `IfcPointByDistanceExpression` is unspecified by the IFC standard. This is an open issue; current practice is to nest the referent under the primary alignment and use its curve, but no normative guidance exists.

## 9.5 Semantic vs. Geometric Positioning

### 9.5.1 The Distinction

It is important to understand that `IfcReferent` serves two distinct roles that must not be conflated:

**Geometric role.** When an `IfcReferent` carries an `IfcLinearPlacement`, it has a precise geometric location on the alignment. This location participates in coordinate computations.

**Semantic role.** An `IfcReferent` can *annotate* the position of another object — not by moving it, but by providing a human-readable station label that names its location. This is purely informational metadata.

The geometric placement of an infrastructure element (a bridge pier, a sign, a drain inlet) is defined entirely by its own `IfcLinearPlacement` with an `IfcPointByDistanceExpression`. An associated referent gives that location a name. Removing or changing the referent does not move the object.

### 9.5.2 IfcRelPositions

The relationship between an `IfcReferent` and the object whose position it annotates is `IfcRelPositions`:

- `RelatingPositioningElement` — the `IfcReferent` (the name-giver).
- `RelatedProducts` — the set of `IfcProduct` instances (the positioned objects) whose station label is defined by this referent.

*Example:* A bridge pier (`IfcBridgePart.PIER`) is geometrically placed at `DistanceAlong = 14235.75`. An `IfcReferent` with `PredefinedType = STATION` and `Pset_Stationing.Station = 14235.75` (relative to the starting station) is connected to the pier via `IfcRelPositions`. The pier’s station label is now Sta. 142+35.75. The pier’s geometry is unchanged. This is shown in Figure 9.5.2-1.

![Figure 9.5.2-1 — Entity relationship diagram: IfcBridgePart.PIER and IfcReferent share the same IfcLinearPlacement. Pset_Stationing (Station = 14235.75) attaches to IfcReferent. IfcRelPositions links the IfcReferent to IfcBridgePart, so the pier is located by its station and offset.](images/Figure_9.5.2-1_Referent_Entity_Relationship.svg)

*Figure 9.5.2-1 — Object graph showing an `IfcBridgePart.PIER` with its own `IfcLinearPlacement`, an `IfcReferent` (STATION type) with `Pset_Stationing`, and the `IfcRelPositions` link between them.*

## 9.6 Summary and Implementation Checklist

|# |Item                                                                                                                                                      |Notes                                                                                   |
|-----|-----------------------------------------------|------------------------------------------------|
|1 |Use `IfcReferent` to attach station labels and other semantic location information to alignment positions.                                                |Referents are informational overlays on geometry, not geometry themselves.              |
|2 |Store the station value in `Pset_Stationing.Station` as a plain `IfcLengthMeasure` in project length units.                                               |Do not store the `ccc+dd.dd` string — compute it from the numeric value when displaying.|
|3 |Place the first referent at `DistanceAlong = 0.0` and set `Pset_Stationing.Station` to the starting station value.                                        |Commonly a round number like 1000.00 (Sta. 10+00). For semantic-only alignments, `ObjectPlacement` = alignment's placement; for geometric alignments, use `IfcLinearPlacement` at distance 0. Update when adding geometry.|
|4 |At a station equation, provide both `IncomingStation` and `Station` on the same referent.                                                                 |`IncomingStation` = upstream label; `Station` = downstream label.                       |
|5 |Do not convert station labels to `DistanceAlong` by simple subtraction. For each referent record $D_i$ and outgoing $S_i$; find the last $i$ where $S_i \leq S$; then `DistanceAlong` $= D_i + (S - S_i)$.|See §9.3.4 for the full algorithm.                                                      |
|6 |Before applying the conversion formula, check for a gap: if $S - S_i > D_{i+1} - D_i$, the station was skipped by a forward equation and `DistanceAlong` is undefined.|Return an error or sentinel value — do not silently produce a meaningless distance. See §9.3.5.|
|7 |Stations in an overlap zone map to two geometric points. Detect the zone ($S_i^{\text{outgoing}} \leq S \leq S_i^{\text{incoming}}$ at an overlap referent) and either return both candidates or apply project rules to select one.|See §9.3.5.                                                                             |
|8 |Use separate `IfcRelNests` instances for alignment layout sub-objects and referents.                                                                      |Mixing them in a single nest is allowed but makes parsing harder.                       |
|9 |Order referents in `IfcRelNests.RelatedObjects` by increasing `DistanceAlong`.                                                                            |Required by the nesting concept template; sort defensively when reading.                |
|10|Use `IfcRelPositions` to link a referent to the object(s) whose station it names.                                                                         |This is semantic annotation only; it does not affect geometry.                          |
|11|Use named referents (PC, PT, PVC, PVI, etc.) for alignment key points, linked via `IfcRelPositions` to the corresponding `IfcAlignmentSegment`.           |Enables station-based queries without re-deriving geometry.                             |
|12|Set `Pset_Stationing.HasIncreasingStation = FALSE` only for reverse-stationing schemes.                                                                   |When absent or `TRUE`, stationing increases in the direction of the alignment.          |
