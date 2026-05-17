"""Generate cover image for IFC Alignment Geometry Implementation Guide.

Renders a 3D perspective of a railway alignment: straight tangent →
clothoid transition → banked circular arc, with cross-section slices
showing cant banking and a local coordinate frame (RefDirection,
Cross-track, Axis) at a point on the arc.
"""
import numpy as np
import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   # noqa: F401

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = '#0B1929'
C_LINE  = '#7EC8E3'   # centerline — light blue
C_SECT  = '#4A90C4'   # cross-sections — mid blue
C_T     = '#FF6B6B'   # RefDirection — coral
C_Y     = '#6BCB77'   # Cross-track — green
C_Z     = '#FFD93D'   # Axis — yellow
C_TEXT  = '#E8F4F8'   # body text — near-white
C_SUB   = '#7EC8E3'   # subtitle — light blue

# ── Geometry parameters ───────────────────────────────────────────────────────
R        = 300.0   # circular arc radius (m)
L_tan    = 100.0   # tangent run (m)
L_cl     = 120.0   # clothoid length (m)
L_arc    = 180.0   # circular arc length (m)
A_cl     = np.sqrt(L_cl * R)   # clothoid parameter

cant_max = 0.15    # m  (full cant on arc)
rail_hw  = 0.75    # m  (half of 1.5 m gauge)
N        = 250     # points per segment

# ── Clothoid via midpoint integration ────────────────────────────────────────
def clothoid_pts(s_arr, A):
    xs, ys, ts = [0.0], [0.0], [0.0]
    for i in range(1, len(s_arr)):
        ds    = s_arr[i] - s_arr[i - 1]
        t_mid = 0.5 * (s_arr[i - 1]**2 + s_arr[i]**2) / (2 * A**2)
        xs.append(xs[-1] + ds * np.cos(t_mid))
        ys.append(ys[-1] + ds * np.sin(t_mid))
        ts.append(s_arr[i]**2 / (2 * A**2))
    return np.array(xs), np.array(ys), np.array(ts)

# Tangent
s_tan = np.linspace(0, L_tan, N // 2)
x_tan, y_tan, t_tan = s_tan.copy(), np.zeros_like(s_tan), np.zeros_like(s_tan)

# Clothoid
s_cl       = np.linspace(0, L_cl, N)
xc, yc, tc = clothoid_pts(s_cl, A_cl)
xc += L_tan

# Circular arc
t_end  = tc[-1]
s_arc  = np.linspace(0, L_arc, N)
x_arc  = xc[-1] + R * (np.sin(t_end + s_arc / R) - np.sin(t_end))
y_arc  = yc[-1] + R * (np.cos(t_end) - np.cos(t_end + s_arc / R))
t_arc  = t_end + s_arc / R

# Concatenate
all_x  = np.concatenate([x_tan, xc[1:], x_arc[1:]])
all_y  = np.concatenate([y_tan, yc[1:], y_arc[1:]])
all_t  = np.concatenate([t_tan, tc[1:], t_arc[1:]])
Ntot   = len(all_x)
Ntan   = len(x_tan)
Ncl    = len(xc) - 1

# Cant profile (0 on tangent, linear ramp through clothoid, constant on arc)
cant   = np.zeros(Ntot)
cant[Ntan:Ntan + Ncl] = np.linspace(0, cant_max, Ncl)
cant[Ntan + Ncl:]     = cant_max

# ── Scaling ───────────────────────────────────────────────────────────────────
sc_xy = 1 / 300.0   # plan scale
sc_z  = 1 / 3.0     # cant exaggeration relative to plan scale

X = all_x * sc_xy
Y = all_y * sc_xy
Z = cant   * sc_z

hw = rail_hw * sc_xy

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(8.5, 11), facecolor=BG)
ax  = fig.add_subplot(111, projection='3d')
ax.set_facecolor(BG)

# ── Centerline ────────────────────────────────────────────────────────────────
ax.plot(X, Y, Z, color=C_LINE, lw=2.5, solid_capstyle='round', zorder=10)

# ── Cross-section slices ──────────────────────────────────────────────────────
n_sl    = 24
sl_idx  = np.linspace(0, Ntot - 1, n_sl, dtype=int)

for i in sl_idx:
    th  = all_t[i]
    c   = cant[i]

    cx  = np.array([-np.sin(th), np.cos(th)])   # cross-track unit vector
    p0  = np.array([X[i], Y[i], Z[i]])

    dz      = c * sc_z * 0.5          # half-cant Z offset
    p_hi    = np.array([p0[0] + cx[0] * hw, p0[1] + cx[1] * hw, p0[2] + dz])
    p_lo    = np.array([p0[0] - cx[0] * hw, p0[1] - cx[1] * hw, p0[2] - dz])

    alpha   = 0.30 + 0.45 * (c / cant_max)   # more opaque where canted

    ax.plot([p_lo[0], p_hi[0]], [p_lo[1], p_hi[1]], [p_lo[2], p_hi[2]],
            color=C_SECT, lw=1.1, alpha=alpha)
    ax.scatter([p_lo[0], p_hi[0]], [p_lo[1], p_hi[1]], [p_lo[2], p_hi[2]],
               color=C_SECT, s=6, alpha=min(alpha + 0.2, 1.0), zorder=8)

# ── Local coordinate frame ────────────────────────────────────────────────────
fi   = Ntan + Ncl + (Ntot - Ntan - Ncl) // 3
fi   = min(fi, Ntot - 1)

p_f  = np.array([X[fi], Y[fi], Z[fi]])
th_f = all_t[fi]
c_f  = cant[fi]
fl   = 0.22   # arrow length

# RefDirection: forward tangent
T_vec = np.array([np.cos(th_f), np.sin(th_f), 0.0])

# Cross-track: lateral (perpendicular to tangent in plan)
Y_vec = np.array([-np.sin(th_f), np.cos(th_f), 0.0])

# Axis: banked up vector — tilt Y_vec toward Z by cant angle
phi   = np.arctan2(c_f, 2 * rail_hw)
A_vec = -np.sin(phi) * Y_vec + np.cos(phi) * np.array([0.0, 0.0, 1.0])
A_vec = A_vec / np.linalg.norm(A_vec)

for vec, col, lbl in [
    (T_vec, C_T, 'RefDirection'),
    (Y_vec, C_Y, 'Cross-track'),
    (A_vec, C_Z, 'Axis'),
]:
    ax.quiver(*p_f, *(vec * fl), color=col, linewidth=2.5,
              arrow_length_ratio=0.22, zorder=20)
    tp = p_f + vec * (fl * 1.55)
    ax.text(tp[0], tp[1], tp[2], lbl, color=col,
            fontsize=7.5, fontfamily='monospace', ha='center', va='center',
            zorder=21)

# ── Axes appearance ───────────────────────────────────────────────────────────
ax.set_axis_off()
for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
    pane.fill = False
    pane.set_edgecolor('none')
ax.grid(False)

# View angle
ax.view_init(elev=28, azim=-52)

# Aspect — equal in XY, compressed in Z
r = max(X.max() - X.min(), Y.max() - Y.min()) / 2.0
mx, my = (X.max() + X.min()) / 2, (Y.max() + Y.min()) / 2
mz = (Z.max() + Z.min()) / 2
ax.set_xlim(mx - r, mx + r)
ax.set_ylim(my - r, my + r)
ax.set_zlim(mz - r * 0.25, mz + r * 0.25)

# Position the 3D axes to use upper 70 % of the figure
ax.set_position([0.0, 0.12, 1.0, 0.72])

# ── Title block ───────────────────────────────────────────────────────────────
fig.text(0.50, 0.895, 'IFC 4x3 ADD 2',
         ha='center', color=C_SUB, fontsize=13, fontfamily='monospace')
fig.text(0.50, 0.855, 'Alignment Geometry',
         ha='center', color=C_TEXT, fontsize=26, fontfamily='monospace',
         fontweight='bold')
fig.text(0.50, 0.815, 'Implementation Guide',
         ha='center', color=C_TEXT, fontsize=23, fontfamily='monospace',
         fontweight='bold')

# Divider line
fig.add_artist(plt.Line2D([0.08, 0.92], [0.80, 0.80],
                          transform=fig.transFigure,
                          color=C_SUB, linewidth=0.8, alpha=0.5))

# Author / bottom
fig.text(0.50, 0.06, 'Richard Brice, PE',
         ha='center', color=C_SUB, fontsize=12, fontfamily='monospace')

# ── Save ──────────────────────────────────────────────────────────────────────
out = 'D:/IFC-Alignment-Geometry-Implementation-Guide/images/cover.svg'
plt.savefig(out, format='svg', facecolor=BG, bbox_inches='tight')
print(f'Saved {out}')
