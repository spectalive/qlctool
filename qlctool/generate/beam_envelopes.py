"""The beam family's movement envelopes: sizes, durations and offsets.

Split out of generate_movement_families.py (2026-09-28) alongside
wash_envelopes.py, so each family's numbers are declared as data on their
own, not mixed with the code that assembles functions from them. See that
module's docstring for why the family split exists and what each envelope
is used for. BEAM and BEAM_TWIN_SHAPES read WASH's own duration and
algorithms, the two places this family is sized off the other one's.
"""

from .envelope import Envelope
from .movement_aim import BEAM_PAN_AIM, BEAM_PAN_SPAN, BEAM_TILT_AIM, BEAM_TILT_SPAN
from .wash_envelopes import WASH

# The beam sizes are the audience window, not a taste: the window is 41 counts
# of pan by 27 of tilt, so a figure any bigger walks out of the room. Slow is
# the same shape drawn smaller and slower, which is the only room left to vary.
BEAM_SLOW = Envelope(
    ("Circle", "Line"),
    # The slow family shares the washes' figure time for the same reason.
    28000,
    BEAM_PAN_SPAN * 2 // 3,
    BEAM_TILT_SPAN * 2 // 3,
    56000,
    pan_offset=BEAM_PAN_AIM,
    tilt_offset=BEAM_TILT_AIM,
)
BEAM = Envelope(
    ("Circle", "Eight", "Line"),
    # Half the washes' figure, so the two families rhyme instead of drifting:
    # one wash curve to two beam curves, the same 10 s hold under both ("hay
    # que mirar la sincronizacion para que tengan sentido", owner, 2026-09-22).
    WASH.duration // 2,
    BEAM_PAN_SPAN,
    BEAM_TILT_SPAN,
    10000,
    pan_offset=BEAM_PAN_AIM,
    tilt_offset=BEAM_TILT_AIM,
)
BEAM_FAST = Envelope(
    BEAM.algorithms,
    5000,
    BEAM.width,
    BEAM.height,
    6000,
    pan_offset=BEAM_PAN_AIM,
    tilt_offset=BEAM_TILT_AIM,
)
# The rig's 23 EFX all ran Rotation=0 and Parallel propagation, every shape an
# axis-aligned clone of the others (Codex A6). An Asymmetric EFX offsets each
# fixture by loopDuration/(fixtureCount+1)*serialNumber (efxfixture.cpp:
# 380-386) for a cascade down the row at no extra cost; Line's smooth cosine
# path (efx.cpp calculatePoint) makes that a wave rather than a stutter.
# These were Serial, which applies the same offset as a wait: a head writes
# nothing until its turn, so it sat at 127/127 - MAC #1 and #2 for 10 and
# 11.6 s at the start of `Ola Vertical` (en-sala DMX audit, 2026-09-26).
# Asymmetric moves every head from the first frame, in the same phases.
#
# Diamond and Leaf were wash-only shapes before this task - the beam family
# was deliberately scoped down to Circle/Eight/Line (2026-08-27 review, see
# module docstring). There is no pre-existing beam Diamond or Leaf to rotate,
# so these are new beam figures rather than a rotation on old ones; sharing
# BEAM's duration keeps them tuned for the same optics. BEAM's width and height
# are the window they must stay in, not their size: turned, each is drawn at
# the size whose reach fits it (fit_rotated) - Diamante at W20 H13 left it.
BEAM_ROTATED_SHAPES = Envelope(
    ("Diamond", "Leaf"),
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    rotation_by_algorithm={"Diamond": 90, "Leaf": 45},
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
    fit_rotated=True,
)
# Square and Lissajous were wash-only, so their buttons left the four beams
# standing still - "algunos movimientos de cabezas no incluyen las beam" (owner,
# 2026-09-22). Same shapes, the beams' own window and figure time.
BEAM_WIDE_SHAPES = Envelope(
    ("Square", "Lissajous"),
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)
BEAM_CASCADE = Envelope(
    BEAM.algorithms[:1],
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    propagation="Asymmetric",
    rotation=45,
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
    fit_rotated=True,
)
BEAM_TILT_WAVE = Envelope(
    ("Line",),
    BEAM.duration,
    0,
    BEAM.height,
    BEAM.hold,
    propagation="Asymmetric",
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)
# Every shape the washes draw, in the beams' own window and figure time. The
# plain buttons reach all seven through three envelopes (BEAM, plus the rotated
# and the wide shapes); the twins need the same seven or they repeat the fault
# the wide shapes fixed - a button that moves the washes and leaves the four
# beams standing ("algunos movimientos de cabeza no incluyen las beam", owner,
# 2026-09-22). The rotations are BEAM_ROTATED_SHAPES': a diamond and a leaf
# read on a beam only turned onto the truss.
BEAM_TWIN_SHAPES = Envelope(
    WASH.algorithms,
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    rotation_by_algorithm={"Diamond": 90, "Leaf": 45},
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
    fit_rotated=True,
)
BEAM_ALTERNATE = Envelope(
    BEAM_TWIN_SHAPES.algorithms,
    BEAM_TWIN_SHAPES.duration,
    BEAM_TWIN_SHAPES.width,
    BEAM_TWIN_SHAPES.height,
    BEAM_TWIN_SHAPES.hold,
    rotation_by_algorithm=BEAM_TWIN_SHAPES.rotation_by_algorithm,
    pan_offset=BEAM_TWIN_SHAPES.pan_offset,
    tilt_offset=BEAM_TWIN_SHAPES.tilt_offset,
    fit_rotated=True,
)
BEAM_UNISON = Envelope(
    ("Line",),
    BEAM.duration,
    BEAM.width,
    BEAM.height,
    BEAM.hold,
    pan_offset=BEAM.pan_offset,
    tilt_offset=BEAM.tilt_offset,
)
