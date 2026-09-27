"""How tall each colour-bank frame may be, given how many there are.

The manual page's left column is one frame per fixture group, stacked, with the
dimmer and strobe frame under them. The number of groups is not a constant - it
grows with the rig - and the column was stacked at a hard-coded pitch until a
fifth group pushed the dimmer frame, its four chases and both strobe buttons off
the bottom of a 900px screen (2026-08-31). Nobody could press them, and the
generator's own summary still said the console fitted on one screen.

So the pitch is derived: the room between the top of the column and the dimmer
frame, divided by however many banks there are, and never more than the pitch
that reads well when there is space to spare.

There is a floor to this - squeeze enough banks in and the buttons stop being
pressable - but the floor is not this file's to guess. `qlctool check`'s
`consola` rule measures the result against the real screen, which is the honest
place to find out.
"""

# The outer frame the whole console lives in, and where the bank column starts.
OUTER_HEIGHT = 892
BANK_COLUMN_TOP = 216
DIMMER_FRAME_HEIGHT = 136
# The pitch when there is room for it: a 44px row of colour buttons under a
# 26px frame header, with air around them.
BANK_PITCH_TOP = 128


def bank_pitch_for(count: int) -> int:
    """The per-bank pitch that keeps `count` banks and the dimmer frame on screen."""
    available = OUTER_HEIGHT - BANK_COLUMN_TOP - DIMMER_FRAME_HEIGHT
    return min(BANK_PITCH_TOP, available // max(count, 1))
