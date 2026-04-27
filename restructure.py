"""
Restructure script:
- Shifts section 2: ## 2.2+ → ## 2.3+ (to make room for new 2.2)
- Shifts section 4: ## 4.2+ → ## 4.3+ (to make room for new 4.2)
"""
import re, os

BASE = r"F:\IFC-Alignment-Geometry-Implementation-Guide"

def shift_subsections(filename, section, start_from):
    path = os.path.join(BASE, filename)
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_code = False
    out = []

    for line in lines:
        s = line.rstrip('\n').strip()
        if s.startswith('```') or s.startswith('~~~'):
            in_code = not in_code
            out.append(line)
            continue
        if in_code:
            out.append(line)
            continue

        m = re.match(r'^(#{1,6}) (\d+)\.(\d+)((?:\.\d+)*) (.+)', line)
        if m:
            hashes   = m.group(1)
            sec      = int(m.group(2))
            sub      = int(m.group(3))
            rest     = m.group(4)   # e.g. ".1.2" or ""
            title    = m.group(5).rstrip()
            if sec == section and sub >= start_from:
                new_num = f"{sec}.{sub+1}{rest}"
                out.append(f"{hashes} {new_num} {title}\n")
            else:
                out.append(line)
        else:
            out.append(line)

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(out)
    print(f"Shifted {filename}")

shift_subsections("2_Horizontal.md", 2, 2)
shift_subsections("4_Cant.md",       4, 2)
print("Done.")
