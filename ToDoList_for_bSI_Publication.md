# To Do List for bSI Publication

Tasks to complete before the two-part guide is published as a buildingSMART document.

1. Settle on where the working repository lives: with buildingSMART International, at https://github.com/RickBrice/IFC-Alignment-Geometry-Implementation-Guide, or elsewhere. Transfer the repository from RickBrice if needed, then update the repository URL in `common/Notices.md`, `Part1/DocumentControl.md`, and `Part2/DocumentControl.md` and rebuild both parts.
2. Engage bSI about hosting the final documents on the IFC Implementation Guidance page: https://technical.buildingsmart.org/resources/ifcimplementationguidance/
3. Discuss with bSI how readers of the hosted documents will reach the example models and test data. Part 2 links to its IFC example models by relative path (24 links to `Part2/examples/`, 1 to `common/testset/`), and Part 1, Chapter 5 refers to test set files by repository path (`common/testset/...`). These work on GitHub but break in a PDF hosted elsewhere. Options to discuss: bSI also hosts the models (and the guide links to that location), the links point to absolute URLs in the public repository (depends on item 1), or the models are packaged as a downloadable archive alongside each PDF. Then convert the links in both parts to the agreed form and rebuild.
