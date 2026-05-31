# Foreword

IfcAlignment, and the related geometric concepts, are new to the IFC 4x3 specification. By expanding IFC into the infrastructure domain, an entirely new audience has been summoned into the buildingSMART community. I am one of those new arrivals.

The IFC specification is highly technical and written with the expectation that the reader already has substantial IFC experience. There is no hand-holding for the newcomer, and industry guidance documents for the infrastructure and alignment aspects of IFC 4x3 are scarce.

My entry point was a practical one: I wanted to view the IFC4x3 models I was exporting from PGSuper, the prestressed concrete bridge design application at the heart of the BridgeLink software suite. No IFC viewer I could find was capable of rendering the alignment geometry correctly, so I built one by enhancing the IfcOpenShell toolkit to evaluate alignment geometry which enabled Blender/Bonsai to render alignment models.

As a bridge engineer with more than 35 years of experience at the Washington State Department of Transportation, I am well versed in highway alignment geometry as it is practiced in bridge and transportation engineering. Even so, I was completely overwhelmed by how alignment geometry is represented in the IFC specification. Things like railway alignments with cant and polynomial spiral transition curves were new to me. Developing working code required considerable research, hand calculations, and implementation experimentation across the many aspects of IFC alignment geometry.

This guide grew out of that experience. I have spent my career building tools that make complex engineering knowledge accessible and actionable — from prestressed concrete design software to recommended practices for girder stability. This document is written in that same spirit: to capture what I have learned about IFC 4x3 alignment geometry and provide practical guidance for developers implementing it in their own applications. I hope it saves others the many hours of confusion I experienced, because in the end, IFC is about interoperability. We all need a shared understanding of infrastructure alignment concepts and geometry to successfully exchange information.

Some sections of this guide were drafted with the assistance of an AI writing tool. All technical content — the mathematics, the IFC schema interpretations, and the implementation guidance — has been reviewed and verified by the author.

Richard Brice, PE
