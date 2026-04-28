# IFC4x3 Alignment Geometry Implementation Guide
Richard Brice, PE

## Forward
`IfcAlignment`, and the related geometric concepts, are new to the IFC4x3 specification. By virtue of expanding the IFC specification into the infrastructure domain, an entirely new audience is summoned into the [buildingSmart](buildingsmart.org) community. I am one of those new arrivals.

The IFC specification is very technical and is written with an expectation that the reader has a high level of knowledge and experience with IFC. Being a technical specification, there is no hand-holding for the novice. Industry guidance documents are generally not available to assist those new to the infrastructure and alignment aspects of IFC4x3. 

I set out to add alignment geometry support to the [IfcOpenShell Toolkit](https://www.ifcopenshell.org). Being a bridge engineer, I am well versed in highway alignment geometry. I was completely overwhelmed and befuddled with alignment representations in the IFC specifications. Through a long and persistent struggle, I was able to figure out most all of what a developer needs to implement IFC alignment geometry in a software application.

This implementation guide captures what I have learned about IFC4x3 alignment geometry and provides guidance as to how a software developer may go about creating an implementation. I hope that other developers find this guide useful, because in the end, IFC is about interoperability. We all need a common understanding of the infrastructure alignment concepts and geometry to successfully exchange information.

## Table of Contents

1.0 [Introduction](1_Introduction.md)
2.0 [Horizontal](2_Horizontal.md)
3.0 [Vertical](3_Vertical.md)
4.0 [Cant](4_Cant.md)
5.0 [Linear Placement](5_LinearPlacement.md)
6.0 [Offset Curves](6_OffsetCurves.md)
7.0 [Referents and Stationing](7_Referents_and_Stationing.md)
8.0 [Specialized Alignment-based Infrastructure Geometry](8_Specialized_Infrastructure_Geometry.md)
9.0 [LandXML to IFC](9_LandXML.md)
10.0 [Precision and Tolerance](10_Precision_and_Tolerance.md)
11.0 [Examples and Validation Data](11_Examples_and_Validation_Data.md)
