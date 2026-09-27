"""The live console's fixed layout and identifier tables, in one place.

Moved verbatim out of `live_console` (2026-09-27) so the page modules the
console is split into read them from here and none of them imports another.
The numbers describe one 1440x900 screen; the tuples name, by catalogue
identifier, which functions and captions each page puts where.
"""

from ..vc.console_font import console_font

CANVAS_WIDTH = 1440
CANVAS_HEIGHT = 900
HEADER = 26  # the frame header, where the page arrows live
GAP = 6

# The console is one multipage frame filling the screen. The page arrows are in
# its header; these keys do the same without aiming a mouse in the dark.
PAGE_NEXT_KEY = "PgDown"
PAGE_PREVIOUS_KEY = "PgUp"
PAGE_SHOW, PAGE_PLAY, PAGE_CONTROL, PAGE_LIBRARY = 0, 1, 2, 3
PAGES = 4

# The panic button. Backspace because it is big, reachable without looking, and
# bound to nothing else in QLC+ or in this console.
STOP_ALL_KEY = "Backspace"
STOP_ALL_FADE_MS = 1000
# Escape, for the same reason - free everywhere else on this console.
BLACKOUT_KEY = "Escape"

OUTER_X, OUTER_Y = 4, 4
OUTER_WIDTH, OUTER_HEIGHT = 1432, 892

LEFT_X, LEFT_WIDTH = 8, 524
MIDDLE_X, MIDDLE_WIDTH = 540, 628
RIGHT_X, RIGHT_WIDTH = 1176, 256

TITLE_FONT = console_font(15)
HUGE_FONT = console_font(28)
BIG_FONT = console_font(15)
HELP_FONT = console_font(11, bold=False)
# A colour bank button is 48px wide and a mix button carries two names: at the
# console's own size the caption is cut off, and a cut-off caption is what the
# blank buttons it replaces were.
SMALL_FONT = console_font(9)
TINY_FONT = console_font(8)

# The library's Matrices frame: the recovered algorithm families (old-vs-new
# audit, 2026-08-28) push the widest group (BarrasLed) to 43 buttons (30 base
# + 13 curated). Eight columns at 40px rows fit 48 in the frame's 300px height
# (24px group label + 6 rows), so the frame still does not grow into the
# "Ruedas y ciclos" frame below it.
MATRIX_COLUMNS = 8
MATRIX_ROW_HEIGHT = 40
MATRIX_BUTTON_HEIGHT = 36

# Keys 1-0 across a colour bank, as the hand-built console has them. Every
# widget sees every key press - on any page, visible or not - so one key lights
# that colour on all three banks.
BANK_KEYS = ("1", "2", "3", "4", "5", "6", "7", "8", "9", "0")

# A colour bank button is 44px wide: the name has to survive that. Each
# colour's short form is the catalogue's `<colour>_short`.
SHORT_COLOURS = ("ultraviolet", "yellow", "magenta", "white", "orange")
# ...and a two-colour mix carries two of them, so those go to two letters
# (`<colour>_code`). One letter is what made "R/A" mean both Rojo/Azul and
# Rojo/Amarillo; Ambar joined the mixes on 2026-09-22 and shares Amarillo's
# first two letters, the same trap as Azul.
MIX_COLOURS = (
    "red",
    "green",
    "blue",
    "yellow",
    "amber",
    "cyan",
    "magenta",
    "white",
    "orange",
    "pink",
    "ultraviolet",
)
# Two wheel positions carry a sentence for a name and no button is that wide.
# The keys are fixture-definition data; the values are catalogue identifiers.
LONG_WHEEL_NAME = {
    "Rainbow effect fast to slow": "rainbow_plus",
    "Rainbow effect reverse slow to fast": "rainbow_minus",
}

# The room's state: one at a time, biggest first. Function identifier,
# caption identifier, and the geometry inside the solo frame.
ROOM_STATES: tuple[tuple[str, str, tuple[int, int, int, int], str], ...] = (
    ("auto", "room_auto", (8, 26, 690, 190), HUGE_FONT),
    ("talk_moment", "room_talk", (704, 26, 352, 92), BIG_FONT),
    ("calm_moment", "room_calm", (1062, 26, 352, 92), BIG_FONT),
    ("party_moment", "room_party", (704, 124, 352, 92), BIG_FONT),
    ("frenzy_moment", "room_frenzy", (1062, 124, 352, 92), BIG_FONT),
    ("full_white", "room_white", (8, 222, 690, 92), BIG_FONT),
    ("all_black", "room_black", (704, 222, 710, 92), BIG_FONT),
)

# The hits: they add to whatever state is running instead of replacing it, so
# they live in a plain frame. Six across one row. (function, caption) identifiers.
HITS: tuple[tuple[str, str], ...] = (
    ("flash_full", "hit_button_flash"),
    ("flash_half", "hit_button_flash_slow"),
    ("flash_colour", "hit_button_flash_colour"),
    ("smoke_on", "hit_button_smoke_now"),
    ("vertical_smoke_now", "hit_button_vertical_smoke_now"),
    ("strobe_fast", "hit_button_strobe"),
    ("strobe_medium", "hit_button_strobe_soft"),
)

# What page 1 says about itself, because nobody reads a manual at a venue.
HELP_LINES = ("help_show_1", "help_show_2", "help_show_3", "help_show_4", "help_show_5")
# The lines that speak of the haze, and what each says on a show without one:
# "AUTO is colours, haze and ..." and "HAZE NOW works while held" are false on
# a rig with no haze machine (2026-09-25, Plan C preflight D9).
HELP_WITHOUT_HAZE = {
    "help_show_1": "help_show_1_no_haze",
    "help_show_3": "help_show_3_no_haze",
}

HELP_ROW_Y = 630
# The haze row was 28px tall under SMALL_FONT while every other button on the
# page was 92 or 118 under BIG_FONT: "botones de humo pequeños comparados con el
# resto" (owner, 2026-09-22). Page 1 had 86px of dead space between the room
# states and the hits, which is what pays for this.
SMOKE_ROW_Y = 770
SMOKE_ROW_HEIGHT = 110
SMOKE_BUTTON_HEIGHT = 74
# The haze rhythms, under the help text on page 1. The captions say minutes
# because that is the question being asked - "cada cuanto" - and the first one
# carries the key the hand-built console had on the haze.
# (function, caption) identifiers.
SMOKE_RHYTHMS: tuple[tuple[str, str], ...] = (
    ("smoke_auto", "haze_every_1"),
    ("smoke_auto_2_min", "haze_every_2"),
    ("smoke_auto_4_min", "haze_every_4"),
    ("smoke_auto_8_min", "haze_every_8"),
)

# The tempo dial lives on page 1 since 2026-08-29: the owner taps the room's
# tempo often enough that it belongs where the operator is looking, on the
# hand-built console's tap key. Its time is one beat and every layer under it
# carries its own multiplier, so a tap moves them all and none of them loses
# its shape - the "se vuelven todos los programas locos" the owner reported
# was one dial writing the same raw interval into every wheel.
#
# The head movement gets a dial of its own, on page 3 and on the SAME tap key
# (a key press reaches every widget bound to it - VCPage::handleKeyEvent walks
# all matches - which is how the hand-built console had one M for three
# dials). It is separate because its numbers are: a shape is sixteen taps
# where a colour is eight, and its EFX have to be re-timed alongside their
# chaser or the figure stops being a proportion of the step.
TEMPO_TAP_KEY = "M"
TEMPO_BEAT_MS = 500  # the dial's starting beat: 120 BPM
MOVEMENT_DIAL_LINES = ("movement_dial_1", "movement_dial_2", "movement_dial_3")

# The workspace's own GrandMaster - it scales every output - had no widget
# bound to it at all. It wants to sit below "Intensidad y strobo de
# fixture", the only other widget that touches every fixture instead of one
# function, but the left column's colour banks grow with the rig - four
# groups already leave that spot off the bottom of a 900px screen - so it
# sits under the audio triggers on the right instead, where there is room.
GRAND_MASTER_WIDTH = 90
GRAND_MASTER_HEIGHT = 140
GRAND_MASTER_LINES = (
    "grand_master_1",
    "grand_master_2",
    "grand_master_3",
    "grand_master_4",
    "grand_master_5",
)

# Page 3's intensity chases and the fixture strobe, three across two rows.
# (function, caption) identifiers.
DIMMER_CHASES: tuple[tuple[str, str], ...] = (
    ("dimmer_chase", "chase_sweep"),
    ("dimmer_chase_2", "chase_reverse"),
    ("dimmer_pingpong", "chase_odd_even"),
    ("dimmer_sequence", "chase_rotation"),
    ("strobe_on", "chase_strobe_on"),
    ("strobe_off", "chase_strobe_off"),
)

# Page 4 says what it is for, because a page of 180 buttons otherwise reads as
# something somebody is supposed to be using; `library_help_lines` picks the
# lines. The "· · ·" separators are not words (ruling B6) and stay literal.
LIBRARY_SEPARATOR = "· · ·"

# The five spectrum bands. The strobe was wired to the upper mids until
# 2026-08-27: a strobe fired by whatever the PA does is a strobe nobody
# chose, and the safety cap on flash rate means nothing if a cymbal can hold
# the button - so no band reaches one (`disparador de audio vacio` checks
# that on every function the bound bars can reach, not just this one).
# Bass is bound to `Golpe Graves`, the plain white twin of the flash: a
# Scene, Flash action with override priority, in no solo frame. An audio bar
# presses on the way up and releases on the way down exactly the way
# `VCButton::pressFunction`/`releaseFunction` expect a Flash button to be
# worked, so the bass gets a momentary white hit that lets go on its own. It
# was `Blanco Total` first (shares the AUTO solo frame: the bass stopped
# AUTO), then `Flash 100%` - until that scene got its hardware strobe back,
# and a strobe fired by whatever the PA does is a strobe nobody chose.
AUDIO_BANDS: tuple[tuple[str, str | None], ...] = (
    ("band_bass", "bass_hit"),
    ("band_low_mid", None),
    ("band_mid", None),
    ("band_high_mid", None),
    ("band_high", None),
)
