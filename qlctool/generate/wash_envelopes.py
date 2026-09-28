"""The wash family's movement envelopes: sizes, durations and offsets.

Split out of generate_movement_families.py (2026-09-28) alongside
beam_envelopes.py, so each family's numbers are declared as data on their
own, not mixed with the code that assembles functions from them. See that
module's docstring for why the family split exists and what each envelope
is used for.
"""

from .envelope import Envelope
from .movement_aim import WASH_PAN_AIM, WASH_PAN_SPAN, WASH_TILT_AIM, WASH_TILT_SPAN

# Sizes and durations are QLC+ raw EFX values, not degrees: a starting
# envelope for on-site tuning, not a universal standard.
# Both families are sized by their own measured window, not by taste: a figure
# bigger than the window is a head pointing out of the room, whatever the
# optics. Slow draws the same shape smaller, which is the room left to vary.
WASH_SLOW = Envelope(
    ("Circle", "Line"),
    28000,
    WASH_PAN_SPAN * 2 // 3,
    WASH_TILT_SPAN * 2 // 3,
    56000,
    pan_offset=WASH_PAN_AIM,
    tilt_offset=WASH_TILT_AIM,
)
WASH = Envelope(
    ("Circle", "Eight", "Line", "Diamond", "Square", "Leaf", "Lissajous"),
    16000,
    WASH_PAN_SPAN,
    WASH_TILT_SPAN,
    10000,
    pan_offset=WASH_PAN_AIM,
    tilt_offset=WASH_TILT_AIM,
)
WASH_FAST = Envelope(
    WASH.algorithms,
    5000,
    WASH.width,
    WASH.height,
    6000,
    pan_offset=WASH_PAN_AIM,
    tilt_offset=WASH_TILT_AIM,
)
WASH_CASCADE = Envelope(
    ("Line",),
    WASH_SLOW.duration,
    WASH_SLOW.width,
    WASH_SLOW.height,
    WASH_SLOW.hold,
    propagation="Asymmetric",
    pan_offset=WASH_SLOW.pan_offset,
    tilt_offset=WASH_SLOW.tilt_offset,
)
# The classic club wave: tilt only. QLC+'s Line traces x=y - a diagonal, and
# no rotation makes it vertical (efx.cpp calculatePoint / rotateAndScale mix
# both axes through width and height) - so the pan term is killed by Width 0
# and the wave lives on the tilt alone, cascaded down the row. Per
# family, like every other figure: same shape, each family's own size.
WASH_TILT_WAVE = Envelope(
    ("Line",),
    WASH.duration,
    0,
    WASH.height,
    WASH.hold,
    propagation="Asymmetric",
    pan_offset=WASH.pan_offset,
    tilt_offset=WASH.tilt_offset,
)
# The synced push: every head at the same phase (spread_phase=False in the
# EFX), so the rig traces one motion together - with the house-right mirror
# kept, the two sides push toward each other and open apart, which is what a
# "push" means on a truss. Slow and wide: the drama is the unison, not speed.
WASH_UNISON = Envelope(
    ("Line",),
    WASH_SLOW.duration,
    WASH_SLOW.width,
    WASH_SLOW.height,
    WASH_SLOW.hold,
    pan_offset=WASH_SLOW.pan_offset,
    tilt_offset=WASH_SLOW.tilt_offset,
)
# Same figure, alternate heads reversed: the contrast to the unison push. Every
# shape gets the twin, so the tablet offers the same figure both ways round
# instead of only where somebody thought to define it.
WASH_ALTERNATE = Envelope(
    WASH.algorithms,
    WASH.duration,
    WASH.width,
    WASH.height,
    WASH.hold,
    pan_offset=WASH.pan_offset,
    tilt_offset=WASH.tilt_offset,
)
