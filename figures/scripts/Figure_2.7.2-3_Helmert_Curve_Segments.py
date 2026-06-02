# Author: Richard Brice, PE
# Date: 2026-06-02
# Generates Figure 2.7.2-3: Helmert curve segments

from pathlib import Path
import ifcopenshell
import ifcopenshell.geom as geom
import ifcopenshell.ifcopenshell_wrapper
import matplotlib.pyplot as plt
import ifcopenshell.api.alignment

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ifc_path = REPO_ROOT / "figures" / "GENERATED__HorizontalAlignment_HelmertCurve_100.0_inf_300_1_Meter.ifc"
output_path = REPO_ROOT / "images" / "Figure_2.7.2-3_Helmert_Curve_Segments.svg"

model = ifcopenshell.open(str(ifc_path))

settings = geom.settings()

X = []
Y = []
segment = model.by_id(36)
mapped_shape = ifcopenshell.ifcopenshell_wrapper.map_shape(settings, segment.wrapped_data)
evaluator = ifcopenshell.ifcopenshell_wrapper.function_item_evaluator(settings, mapped_shape)
for d in evaluator.evaluation_points():
    m = evaluator.evaluate(d)
    X.append(m[0][3])
    Y.append(m[1][3])

X2 = []
Y2 = []
segment = model.by_id(48)
mapped_shape = ifcopenshell.ifcopenshell_wrapper.map_shape(settings, segment.wrapped_data)
evaluator = ifcopenshell.ifcopenshell_wrapper.function_item_evaluator(settings, mapped_shape)
for d in evaluator.evaluation_points():
    m = evaluator.evaluate(d)
    X2.append(m[0][3])
    Y2.append(m[1][3])

plt.plot(X, Y, label="First Half")
plt.plot(X2, Y2, label="Second Half")
plt.legend()
plt.grid()
plt.xlabel("X (m)")
plt.ylabel("Y (m)")

plt.savefig(str(output_path))
