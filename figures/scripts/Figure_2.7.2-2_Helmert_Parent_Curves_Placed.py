# Author: Richard Brice, PE
# Date: 2026-10-13
# Generates Figure 2.7.2-2: Helmert curve parent curves placed

from pathlib import Path
import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.ifcopenshell_wrapper
import matplotlib.pyplot as plt
import ifcopenshell.api.alignment

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ifc_path = REPO_ROOT / "figures" / "GENERATED__HorizontalAlignment_HelmertCurve_100.0_inf_300_1_Meter_Parent_Curves_Placed.ifc"
output_path = REPO_ROOT / "images" / "Figure_2.7.2-2_Helmert_Parent_Curves_Placed.svg"

model = ifcopenshell.open(str(ifc_path))

settings = geom.settings()


def sample_distances(segment, step=0.5):
    """Distances along the curve segment, every step metres from its start to its end."""
    length = abs(segment.SegmentLength.wrappedValue)
    n = int(round(length / step))
    return [length * i / n for i in range(n + 1)]


X = []
Y = []
segment = model.by_id(36)
mapped_shape = ifcopenshell.ifcopenshell_wrapper.map_shape(settings, getattr(segment, 'wrapped_data', segment))
evaluator = ifcopenshell.ifcopenshell_wrapper.function_item_evaluator(settings, mapped_shape)
for d in sample_distances(segment):
    m = evaluator.evaluate(d)
    X.append(m[0][3])
    Y.append(m[1][3])

X2 = []
Y2 = []
segment = model.by_id(48)
mapped_shape = ifcopenshell.ifcopenshell_wrapper.map_shape(settings, getattr(segment, 'wrapped_data', segment))
evaluator = ifcopenshell.ifcopenshell_wrapper.function_item_evaluator(settings, mapped_shape)
for d in sample_distances(segment):
    m = evaluator.evaluate(d)
    X2.append(m[0][3])
    Y2.append(m[1][3])

plt.plot(X, Y, label="First Half")
plt.plot(X2, Y2, label="Second Half")
plt.legend()
plt.grid()
plt.xlabel("X (m)")
plt.ylabel("Y (m)")

plt.text(X2[0] + 5, Y2[0], f"(xp,yp) = ({X2[0]},{Y2[0]})")
plt.text(X2[0] + 5, Y2[0] - 0.3, "(dxp,dyp) = (0.998457,0.05527)")

plt.savefig(str(output_path))
