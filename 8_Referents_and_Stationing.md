# Section 8 - IfcReferent and Stationing

The class `IfcReferent` defines a position at a particular offset along an
alignment curve. Stationing (also known as chainage) is a good example.

Referents are nested to alignments, using `IfcRelNests`. `IfcRelNests.RelatedObjects` is an ordered list so the first referent defines the starting station of the associated `IfcAlignment` related through `IfcRelNests.RelatingObject`.

`IfcRelNests.PredefinedType = STATION` is not well defined in the IFC specification, however it seems most appropriate for referents that only indicate a station.

The stationing value is is provided using `Pset_Stationing`. The `Station` property defines the station value at a location. Station equations (or chainage breaks) are defined by providing the `IncomingStation` and `Station` properties.

## IfcRelNests Usage
Alignment layouts and stationing referents both decompose `IfcAlignment` through `IfcRelNests`. The IFC specification is not clear if alignment layouts and referents belong in the same or different nests. Since alignment layout and referent are completely different things, it is recommended that they are contained within their own nest. This is illustrated in Figure 8.1.


![](images/image8.1.png)

*Figure 8.1 Recommended approach to nesting alignment layouts and referents*

Figure 8.1 shows two `IfcRelNests`, one each for alignment layout and referent. Also note the `IfcRelPositions` relationship. The referent defines the stationing and positions the alignment. The case shown is for horizontal, vertical, and cant. Horizontal only and horizontal with vertical are similar.

## Key Alignment Points

Key alignment points, such as Point Of Curvature (PC) of a horizontal curve or Point of Vertical Curve (VPC) for a vertical profile, are defined with an `IfcReferent`. These referents are contained in the `IfcRelNests.RelatedObjects` list. Based on the [Object Nesting](https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/concepts/Object_Composition/Nesting/Object_Nesting/content.html) concept template, all `IfcReferent` nest with the `IfcAlignment`. For this reason the `IfcRelNests.RelatedObjects` list may contain critical points for horizontal and vertical layouts. The `IfcReferent` must be in order of occurance. Additionally, the `IfcReferent` informs of the position of the curve segment with the `IfcRelPositions` relationship.

![](images/image8.2.png)
*Figure 8.2 Example of IfcReferent informing on the position of an IfcAlignmentSegment key point*