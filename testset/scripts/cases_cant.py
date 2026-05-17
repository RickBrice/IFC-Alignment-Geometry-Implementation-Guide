"""Cant alignment test case parameter tables.

Each case tuple:
  (h_start_r, h_end_r, h_start_label, h_end_label, scl, ecl, scr, ecr)

  h_start_r / h_end_r : horizontal IFC radius values (metres).
                         0.0 = infinite radius, positive = left, negative = right.
  scl / ecl            : start / end cant on the left  rail (metres).
  scr / ecr            : start / end cant on the right rail (metres).

Sign convention:
  Left  curves (positive radius) → right rail is the outer rail → cant on right rail.
  Right curves (negative radius) → left  rail is the outer rail → cant on left  rail.

Cant values:
  All cases use FULL_CANT (0.16 m) as the non-zero cant value.
  Entry transitions ramp from 0 → FULL_CANT; exit transitions ramp FULL_CANT → 0.
  Arc-to-arc cases treat the tighter arc (smaller radius) as the "full cant" end.
"""

SEGMENT_LENGTH = 100.0

FULL_CANT = 0.160   # 160 mm — cant value for all transition types except VienneseBend

_FC = FULL_CANT

# VienneseBend uses lower cant values because its geometry requires cant parameters
# and the test cases are already constrained by the horizontal alignment geometry.
VB_CANT_LO = 0.030   #  30 mm — low-end cant for VienneseBend transitions
VB_CANT_HI = 0.100   # 100 mm — high-end cant for VienneseBend transitions

_VL = VB_CANT_LO
_VH = VB_CANT_HI

# Eight transition cases (entry/exit spirals and arc-to-arc).
# Paired with a matching horizontal layout of the same curve type.
TRANSITION_CANT_CASES = [
    # Left curves — cant applied to right rail
    (   0.0,   300.0,   'inf',   '300',  0.0, 0.0,  0.0, _FC),   # entry: 0 → full
    ( 300.0,     0.0,   '300',   'inf',  0.0, 0.0,  _FC, 0.0),   # exit:  full → 0
    ( 300.0,  1000.0,   '300',  '1000',  0.0, 0.0,  _FC, 0.0),   # tighter → looser
    (1000.0,   300.0,  '1000',   '300',  0.0, 0.0,  0.0, _FC),   # looser → tighter
    # Right curves — cant applied to left rail
    (   0.0,  -300.0,  '-inf',  '-300',  0.0, _FC,  0.0, 0.0),   # entry: 0 → full
    (-300.0,     0.0,  '-300',  '-inf',  _FC, 0.0,  0.0, 0.0),   # exit:  full → 0
    (-300.0, -1000.0,  '-300', '-1000',  _FC, 0.0,  0.0, 0.0),   # tighter → looser
    (-1000.0, -300.0, '-1000',  '-300',  0.0, _FC,  0.0, 0.0),   # looser → tighter
]

# Four constant-cant cases using CircularArc horizontal (equal start/end radius).
CONSTANT_CANT_CASES = [
    # Left arcs — constant cant on right rail
    (  300.0,   300.0,  '300',  '300',  0.0, 0.0,  _FC, _FC),
    (-300.0,  -300.0,  '-300', '-300',  _FC, _FC,  0.0, 0.0),
    ( 1000.0,  1000.0, '1000', '1000',  0.0, 0.0,  _FC, _FC),
    (-1000.0, -1000.0,'-1000','-1000',  _FC, _FC,  0.0, 0.0),
]

# VienneseBend uses different cant values (0.03 / 0.10) because its horizontal
# geometry is parameterised by cant; the transition still follows entry/exit logic.
VIENNESEBEND_CANT_CASES = [
    # Left curves — cant applied to right rail
    (   0.0,   300.0,   'inf',   '300',  0.0, 0.0,  _VL, _VH),   # entry: low → high
    ( 300.0,     0.0,   '300',   'inf',  0.0, 0.0,  _VH, _VL),   # exit:  high → low
    ( 300.0,  1000.0,   '300',  '1000',  0.0, 0.0,  _VH, _VL),   # tighter → looser
    (1000.0,   300.0,  '1000',   '300',  0.0, 0.0,  _VL, _VH),   # looser → tighter
    # Right curves — cant applied to left rail
    (   0.0,  -300.0,  '-inf',  '-300',  _VL, _VH,  0.0, 0.0),   # entry: low → high
    (-300.0,     0.0,  '-300',  '-inf',  _VH, _VL,  0.0, 0.0),   # exit:  high → low
    (-300.0, -1000.0,  '-300', '-1000',  _VH, _VL,  0.0, 0.0),   # tighter → looser
    (-1000.0, -300.0, '-1000',  '-300',  _VL, _VH,  0.0, 0.0),   # looser → tighter
]

# (cant_ptype, h_ptype, folder_name)
# LinearTransition pairs with Clothoid horizontal (linear cant, spiral geometry).
# All other cant types pair with the same-named horizontal type.
TRANSITION_CANT_TYPES = [
    ('LINEARTRANSITION', 'CLOTHOID',     'LinearTransition'),
    ('BLOSSCURVE',       'BLOSSCURVE',   'BlossCurve'),
    ('COSINECURVE',      'COSINECURVE',  'CosineCurve'),
    ('HELMERTCURVE',     'HELMERTCURVE', 'HelmertCurve'),
    ('SINECURVE',        'SINECURVE',    'SineCurve'),
    ('VIENNESEBEND',     'VIENNESEBEND', 'VienneseBend'),
]
