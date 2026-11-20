"""Horizontal alignment test case parameter tables.

Each case tuple: (start_r, end_r, start_label, end_label)
  start_r / end_r  : IFC value in metres; 0.0 = infinite radius (straight),
                     positive = left curve, negative = right curve.
  start_label / end_label : tokens used in the output filename.
"""

SEGMENT_LENGTH = 100.0

TRANSITION_TYPES = [
    'CLOTHOID',
    'BLOSSCURVE',
    'COSINECURVE',
    'HELMERTCURVE',
    'SINECURVE',
]

# Eight cases covering entry/exit spirals and arc-to-arc transitions,
# for both left-curving (positive radius) and right-curving (negative radius).
TRANSITION_CASES = [
    (   0.0,    300.0,   'inf',   '300'),   # entry spiral, straight → left arc
    ( 300.0,      0.0,   '300',   'inf'),   # exit spiral,  left arc → straight
    (   0.0,   -300.0,  '-inf',  '-300'),   # entry spiral, straight → right arc
    (-300.0,      0.0,  '-300',  '-inf'),   # exit spiral,  right arc → straight
    ( 300.0,   1000.0,   '300',  '1000'),   # loosening,    tighter → looser (left)
    (1000.0,    300.0,  '1000',   '300'),   # tightening,   looser → tighter (left)
    (-300.0,  -1000.0,  '-300', '-1000'),   # loosening,    tighter → looser (right)
    (-1000.0,  -300.0, '-1000',  '-300'),   # tightening,   looser → tighter (right)
]

# One case: a straight line with infinite radius at both ends.
LINE_CASES = [
    (0.0, 0.0, 'inf', 'inf'),
]

# Four cases: left and right circular arcs at two radii.
# inf/inf and -inf/-inf excluded (infinite radius is a line, not an arc).
CIRCULAR_ARC_CASES = [
    (  300.0,   300.0,  '300',  '300'),
    ( -300.0,  -300.0, '-300', '-300'),
    ( 1000.0,  1000.0, '1000', '1000'),
    (-1000.0, -1000.0,'-1000','-1000'),
]
