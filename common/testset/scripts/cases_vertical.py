"""Vertical alignment test case parameter tables.

Each case tuple: (start_grad, end_grad, start_label, end_label)
  Gradient values are stored as percentages and used verbatim in filenames
  (e.g. 0.5 represents 0.5 %).
  For CONSTANTGRADIENT, start_grad == end_grad is required by the IFC spec.
"""

SEGMENT_LENGTH = 100.0
START_HEIGHT   = 10.0   # metres above datum

# Four cases; start gradient always equals end gradient.
CONSTANT_GRADIENT_CASES = [
    ( 0.0,  0.0,  '0.0',  '0.0'),
    ( 0.5,  0.5,  '0.5',  '0.5'),
    (-0.5, -0.5, '-0.5', '-0.5'),
    ( 1.0,  1.0,  '1.0',  '1.0'),
    (-1.0, -1.0, '-1.0', '-1.0'),
]

# Twelve cases covering sag/crest transitions, ascending, and descending profiles.
# Used for both PARABOLICARC and CIRCULARARC.
VERTICAL_TRANSITION_CASES = [
    ( 0.0,  0.5,  '0.0',  '0.5'),   # sag from flat
    ( 0.5,  0.0,  '0.5',  '0.0'),   # crest to flat
    ( 0.0, -0.5,  '0.0', '-0.5'),   # crest from flat
    (-0.5,  0.0, '-0.5',  '0.0'),   # sag to flat
    ( 0.5,  1.0,  '0.5',  '1.0'),   # sag, both ascending
    ( 1.0,  0.5,  '1.0',  '0.5'),   # crest, both ascending
    (-0.5, -1.0, '-0.5', '-1.0'),   # crest, both descending
    (-1.0, -0.5, '-1.0', '-0.5'),   # sag, both descending
    ( 0.5, -1.0,  '0.5', '-1.0'),   # crest, ascending to descending
    (-0.5,  1.0, '-0.5',  '1.0'),   # sag, descending to ascending
    ( 1.0, -0.5,  '1.0', '-0.5'),   # crest, ascending to descending
    (-1.0,  0.5, '-1.0',  '0.5'),   # sag, descending to ascending
]
