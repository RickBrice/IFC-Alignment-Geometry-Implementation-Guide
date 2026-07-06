from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib as mpl

mpl.rcParams['font.size'] = 11

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
output_path = REPO_ROOT / "images" / "Figure_8.2.1-1_ifcpointbydisanceexpression_offsets.svg"

# ---------------------------------------------------------------
# 1. Build an alignment that is horizontally curved, with a straight
#    (constant-grade) vertical profile -- i.e. no vertical curvature,
#    just a steep, uniform gradient, so the tilt of OffsetVertical
#    away from true global-Z is easy to see without the extra
#    complexity of a parabolic vertical curve.
# ---------------------------------------------------------------
R = 220.0                       # horizontal curve radius
L = 340.0                       # total length modeled
s = np.linspace(0, L, 400)

theta = s / R
x = R * np.sin(theta)
y = R * (1 - np.cos(theta))

# Vertical: constant, very steep grade (straight line in profile)
grade = 0.45                    # 45% constant grade -- steep, unambiguous tilt
z0 = 0.0
z = z0 + grade * s

curve = np.vstack([x, y, z]).T

# Self-check: s is defined as arc length along the HORIZONTAL projection
# (x(s), y(s)) -- not along the 3D curve. Elevation z(s) = grade * s is then
# a function of that same horizontal station, matching how DistanceAlong
# is meant to be measured (along the projected curve in the horizontal
# plane), consistent with how road/rail stationing works.
_ds_horiz = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
assert np.allclose(_ds_horiz, np.diff(s), atol=1e-6), "s must equal horizontal arc length"

def pos(sq):
    th = sq / R
    xx = R * np.sin(th)
    yy = R * (1 - np.cos(th))
    zz = z0 + grade * sq
    return np.array([xx, yy, zz])

# ---------------------------------------------------------------
# 2. Pick the reference point P (DistanceAlong = s0) and get tangent
# ---------------------------------------------------------------
s0 = L / 2.0   # midpoint of the curve
eps = 0.5
P = pos(s0)
T = (pos(s0 + eps) - pos(s0 - eps))
T = T / np.linalg.norm(T)

Zg = np.array([0, 0, 1.0])     # global vertical
Yv = Zg - np.dot(Zg, T) * T    # component of global Z perpendicular to T
Yv = Yv / np.linalg.norm(Yv)   # -> OffsetVertical direction

# Horizontal "left" direction: rotate horizontal projection of T by +90 deg in XY
Th = np.array([T[0], T[1], 0.0])
Th = Th / np.linalg.norm(Th)
Lat = np.array([-Th[1], Th[0], 0.0])   # OffsetLateral direction (left, horizontal)

# sanity check: Lat, Yv, T should be mutually orthogonal (right-handed-ish)
# print(np.dot(Lat, Yv), np.dot(Lat, T), np.dot(Yv, T))

# ---------------------------------------------------------------
# 3. Plot
# ---------------------------------------------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=20, azim=-98)
ax.set_box_aspect([1,1,0.7])
ax.set_zlim(0, 175)

# alignment curve
ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], color='#2b6cb0', lw=2.5, label='Basis curve')

# reference point (marker drawn later as a 2D overlay so it renders on top -- see section 7)
P_label_anchor = P + np.array([3, 0, -8])
ax.text(P_label_anchor[0], P_label_anchor[1], P_label_anchor[2],
        'P\n(%.1f, %.1f, %.1f)' % (P[0], P[1], P[2]),
        fontsize=9, ha='left', va='top', fontweight='bold',
        bbox=dict(facecolor='white', edgecolor='black', alpha=0.85, pad=2, linewidth=0.6))

# scale for arrows
arrow_len = 55

def draw_arrow(origin, direction, color, label, length=arrow_len, lw=3, txt_off=(0,0,0), txt_scale=1.35, ha='left', va='bottom'):
    end = origin + direction * length
    ax.plot([origin[0], end[0]], [origin[1], end[1]], [origin[2], end[2]],
             color=color, lw=lw)
    # simple arrowhead using quiver
    ax.quiver(origin[0], origin[1], origin[2],
               direction[0], direction[1], direction[2],
               length=length, color=color, lw=lw, arrow_length_ratio=0.12)
    tx, ty, tz = origin + direction * length * txt_scale + np.array(txt_off)
    ax.text(tx, ty, tz, label, color=color, fontsize=10, fontweight='bold',
            ha=ha, va=va,
            bbox=dict(facecolor='white', edgecolor=color, alpha=0.85, pad=2, linewidth=0.6))

# Longitudinal (tangent) direction -> OffsetLongitudinal
draw_arrow(P, T, '#c53030', 'OffsetLongitudinal\n(tangent T)', length=arrow_len,
           txt_off=(0, 0, 0), txt_scale=1.0, ha='left', va='bottom')

# Lateral direction (horizontal, left of travel) -> OffsetLateral
# Anchor exactly at the arrowhead tip, with the label's top-right bbox
# corner pinned there (ha='right', va='top' puts the box just left of
# and below the anchor point).
draw_arrow(P, Lat, '#2f855a', 'OffsetLateral\n(\u22a5 to T-projection)', length=arrow_len,
           txt_off=(0, 0, 0), txt_scale=1.0, ha='right', va='top')

# Vertical direction (in tangent-vertical plane, \u22a5 to T) -> OffsetVertical
draw_arrow(P, Yv, '#2b6cb0', 'OffsetVertical\n(\u22a5 to T, in vertical plane)', length=arrow_len,
           txt_off=(0, 0, 0), txt_scale=1.0, ha='right', va='bottom')

# ---------------------------------------------------------------
# 4. Shade the "vertical plane containing the tangent, perpendicular to global XY"
#    Drawn with edges along the horizontal projection of T (parallel to
#    global XY) and along global Z (perpendicular to global XY), so the
#    rectangle's edges are literally horizontal / vertical rather than
#    tilted along T and Yv (even though it's the same plane).
# ---------------------------------------------------------------
plane_half_w = 120   # along Th (horizontal, in-plane direction) -- widened
plane_top_z = 175    # absolute global Z for the plane's top edge
b_top = plane_top_z - P[2]
b_bot = -P[2]        # bottom edge exactly at z = 0, so P' lies on the plane
corners = []
for a in (-1, 1):
    for b in (b_bot, b_top):
        corners.append(P + a * plane_half_w * Th + b * Zg)
# order corners to form a proper quad
quad = [corners[0], corners[1], corners[3], corners[2]]
poly = Poly3DCollection([quad], alpha=0.15, facecolor='#63b3ed', edgecolor='#2b6cb0', linewidths=1)
ax.add_collection3d(poly)
plane_top_center = P + b_top * Zg

# ---------------------------------------------------------------
# 6. Construct and draw the actual OFFSET POINT Q.
#    Per the spec's order of application: lateral and vertical offsets
#    are applied first (relative to P), THEN the longitudinal offset
#    is applied last (moving along T from that intermediate point).
# ---------------------------------------------------------------
offset_lateral = -35.0       # negative -> to the right of travel
offset_vertical = 25.0       # positive -> up, in the tangent-vertical plane
offset_longitudinal = 15.0   # positive -> forward, along T

def draw_offset_segment(origin, vec, color, lw=1.2, ls=(0, (1, 1))):
    end = origin + vec
    ax.quiver(origin[0], origin[1], origin[2],
               vec[0], vec[1], vec[2],
               color=color, lw=lw, arrow_length_ratio=0.0, linestyle=ls)
    return end

# Step 1: lateral offset from P
Pa = draw_offset_segment(P, offset_lateral * Lat, '#2f855a')
# Step 2: vertical offset from Pa
Pb = draw_offset_segment(Pa, offset_vertical * Yv, '#2b6cb0')
# Step 3 (applied LAST): longitudinal offset from Pb -> final offset point Q
Q = draw_offset_segment(Pb, offset_longitudinal * T, '#c53030')

# Q marker drawn later as a 2D overlay so it renders on top -- see section 7
Q_label_anchor = Q + np.array([5, 5, -5])
ax.text(Q_label_anchor[0], Q_label_anchor[1], Q_label_anchor[2],
        'Q  (offset point)\nlat=%g, vert=%g, long=%g\n(%.1f, %.1f, %.1f)' %
        (offset_lateral, offset_vertical, offset_longitudinal, Q[0], Q[1], Q[2]),
        color='black', fontsize=9, fontweight='bold', ha='left', va='top',
        bbox=dict(facecolor='white', edgecolor='black', alpha=0.85, pad=2, linewidth=0.6))




ax.plot(curve[:, 0], curve[:, 1], np.zeros_like(curve[:, 2]),
        color='gray', lw=1.8, linestyle='--', alpha=0.8,
        label='Projection onto global XY (z = 0)')

# vertical dashed connector from P down to its projection at z = 0
P0 = np.array([P[0], P[1], 0.0])
ax.plot([P[0], P0[0]], [P[1], P0[1]], [P[2], P0[2]],
        color='gray', lw=1.2, linestyle=(0, (1, 1)))
ax.scatter(*P0, color='gray', s=25)
ax.text(P0[0], P0[1], P0[2] - 6, "P'  (DistanceAlong = s$_0$, z = 0)", fontsize=9, color='gray', ha='center',
        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

# start/end markers on curve for orientation
ax.scatter(*curve[0], color='#4a5568', s=20)
ax.text(*curve[0], '  s = 0', fontsize=9, color='#4a5568')
ax.scatter(*curve[-1], color='#4a5568', s=20)
ax.text(*curve[-1], '  s = L', fontsize=9, color='#4a5568')

ax.set_xlabel('Global X')
ax.set_ylabel('Global Y')
ax.set_zlabel('Global Z (elevation)')
ax.set_title('Offset directions for IfcPointByDistanceExpression', pad=20)

# clean legend for the curve only (arrows already labeled)
ax.legend(loc='upper left', fontsize=9)

# ---------------------------------------------------------------
# 7. Plane label, added last (after all data + limits are finalized)
#    so its rotation matches how the plane's top edge actually renders
#    on screen at this point/azimuth/aspect.
# ---------------------------------------------------------------
fig.canvas.draw()  # lock in autoscaled x/y limits + finalize the projection

from mpl_toolkits.mplot3d import proj3d

def project2d(pt):
    x2, y2, _ = proj3d.proj_transform(pt[0], pt[1], pt[2], ax.get_proj())
    return np.array([x2, y2])

top_left = plane_top_center - plane_half_w * Th
top_right = plane_top_center + plane_half_w * Th
_l2_px = ax.transData.transform(project2d(top_left))
_r2_px = ax.transData.transform(project2d(top_right))
plane_label_angle = np.degrees(np.arctan2(_r2_px[1] - _l2_px[1], _r2_px[0] - _l2_px[0]))

# NOTE: Axes3D.text() silently ignores the `rotation` kwarg in this
# matplotlib build (verified empirically). Use text2D pinned to the same
# screen position via axes-fraction coordinates instead, which does
# respect rotation.
_center_px = ax.transData.transform(project2d(plane_top_center + 3 * Zg))
_center_axes_frac = ax.transAxes.inverted().transform(_center_px)

ax.text2D(_center_axes_frac[0], _center_axes_frac[1],
          'plane of T \u22a5 global XY', color='#2b6cb0', fontsize=9, style='italic',
          ha='center', va='top', rotation=plane_label_angle, transform=ax.transAxes,
          bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=1))

def to_axes_frac(pt):
    px = ax.transData.transform(project2d(pt))
    return ax.transAxes.inverted().transform(px)

# P and Q markers, drawn as 2D overlays on top of everything else.
# mplot3d sorts artists by 3D depth for compositing and does NOT reliably
# honor the `zorder` kwarg across different artist types (a 3D scatter
# with a high zorder can still be drawn underneath arrows/lines/planes).
# Axes3D.scatter() doesn't accept a custom 2D transform the way text2D
# does, so we use text2D with a Unicode glyph instead, which is the
# mechanism verified to reliably draw on top (same as the plane label).
_P_frac = to_axes_frac(P)
ax.text2D(_P_frac[0], _P_frac[1], '\u25CF', color='black', fontsize=9,
          ha='center', va='center', transform=ax.transAxes, zorder=1000)

_Q_frac = to_axes_frac(Q)
ax.text2D(_Q_frac[0], _Q_frac[1], '\u2605', color='black', fontsize=18,
          ha='center', va='center', transform=ax.transAxes, zorder=1000)

plt.tight_layout()
plt.savefig(str(output_path), dpi=200, bbox_inches='tight')
print("saved")
