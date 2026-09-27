"""Which console frames become which desk pages, and what each control is.

The tablet does not mirror the Mac's console; it reorganises the same widgets
by what the operator is thinking about. This is the one place that says how:
frames are found by catalogue identifier (`qlctool/locales`), so a frame
caption in any shipped language places the same.

A Flash button is never an enabled desk control: the map replaces held
accents with validated private bursts. Placement retains each source accent
so its caption, section and swatches survive the replacement.
"""

from dataclasses import dataclass

HELD_REASON = "held on the Mac"

# Provisional durations in milliseconds, tunable by the owner after a rig test.
BURST_MS = {
    "hit_flash": 8000,
    "hit_flash_slow": 8000,
    "hit_flash_colour": 8000,
    "hit_strobe": 4000,
    "hit_strobe_soft": 4000,
    "hit_smoke_now": 3000,
    "hit_vertical_smoke_now": 3000,
    "red": 8000,
    "green": 8000,
    "blue": 8000,
    "ultraviolet": 8000,
    "yellow": 8000,
    "cyan": 8000,
    "magenta": 8000,
    "white": 8000,
    "orange": 8000,
    "pink": 8000,
}

# Page and section titles are catalogue identifiers, displayed in the
# workspace's own language where the map is built.
PAGES = (
    ("live", "desk_page_live"),
    ("color", "family_colour"),
    ("pixels", "family_pixels"),
    ("heads", "family_heads"),
    ("gobos", "family_gobos"),
    ("prism", "family_prism"),
    ("control", "desk_page_control"),
)
FAMILY_PAGES = {
    "family_colour": "color",
    "family_pixels": "pixels",
    "family_heads": "heads",
    "family_gobos": "gobos",
    "family_prism": "prism",
}
# The order sections take on a page: what the operator reaches for first,
# and the bounded hits last.
SECTION_ORDER = ("state", "hooks", "picks", "haze", "chases", "haze-light", "accents")

# Words the tablet puts under a control where the show's own would mislead
# an operator in the dark: a black look is not a stop, and a haze rhythm
# fires the moment it starts. Keyed by the control's function identifier, or
# by role for a whole section; valued by catalogue identifier, None for no
# words at all. The show's names are never touched.
SAFETY_DETAIL_BY_FUNCTION = {
    "all_black": "desk_detail_not_stop",
    "dimmer_pingpong": None,
    "vertical_smoke": None,
}
# Names the tablet shows instead of the show's where the show's would be
# read as something else: the fog fixture's light is not fog, and a chase
# that alternates halves is one thing, not a name and a footnote.
SAFETY_CAPTION_BY_FUNCTION = {
    "vertical_smoke": "desk_caption_vertical_smoke_light",
    "dimmer_pingpong": "desk_caption_odd_even",
}
SAFETY_DETAIL_BY_ROLE = {
    "haze": "desk_detail_fire_now",
}
SECTION_TITLES = {
    "state": "desk_section_state",
    "accents": "desk_section_accents",
    "haze": "desk_section_haze",
    "hooks": "desk_section_hooks",
    "picks": "desk_section_picks",
    "chases": "desk_section_chases",
    "haze-light": "desk_section_haze_light",
}


@dataclass(frozen=True)
class Placement:
    page: str
    section: str
    role: str
    enabled: bool
    reason: str
