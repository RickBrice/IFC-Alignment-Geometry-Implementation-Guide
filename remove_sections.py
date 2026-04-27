"""Remove sections 1.5.3, 1.5.4, 1.5.5 from 1_Introduction.md"""
import os

BASE = r"F:\IFC-Alignment-Geometry-Implementation-Guide"
path = os.path.join(BASE, "1_Introduction.md")

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove from ### 1.5.3 heading through end of 1.5.5 (just before ## 1.6)
start_marker = "\n### 1.5.3 Horizontal Alignment -- IfcCompositeCurve"
end_marker   = "\n## 1.6 Segment Mapping: Sources and Examples"

start_idx = content.find(start_marker)
end_idx   = content.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print(f"ERROR: markers not found (start={start_idx}, end={end_idx})")
else:
    new_content = content[:start_idx] + "\n" + content[end_idx:]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Done. Removed 1.5.3-1.5.5.")
