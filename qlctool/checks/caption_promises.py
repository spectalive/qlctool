"""What each generator-chosen caption promises the room has, by catalogue identifier.

The club's console once said "gobos, prism and dimmer follow your beat" on a
rig with neither, and spoke of "the panels' 42 built-in effects" with no panel
(2026-09-25, Plan C final review). The generator now picks a caption from what
the rig has (`tempo_help_line`, `matrices_frame_caption`, `panels_frame_caption`,
`library_help_lines`, `page_control_title`); this table is the other half,
read by `rule_caption_promise`: every identifier those five can choose, and
what its text promises.

A promise is a channel role where one exists (a gobo wheel, a prism) and
otherwise a fact about the patch: a haze machine, a beam with a colour wheel
(the fixtures the beam wheel frame is built from), a bar, a panel, a fixture
with built-in effects. `promise_kept` says how each is seen. The library's
first two lines and its sixth and seventh are one sentence each about the
built-in effects, so each line of it carries the promise, and the lines that
call them the panels' promise a panel (2026-09-25); the
other lines (AUTO, the group arrows, the wheels adding up to white) promise
nothing the rig could lack. `tests/test_caption_variants.py` holds this table
to every identifier the selectors can return.
"""

from .. import roles

GOBO = roles.GOBO
PRISM = roles.PRISM
HAZE = "haze"
BEAM_WHEEL = "beam_wheel"
BAR = "bar"
PANEL = "panel"
BUILTIN_EFFECTS = "builtin_effects"

CAPTION_PROMISES: dict[str, tuple[str, ...]] = {
    "tempo_2": (GOBO, PRISM),
    "tempo_2_no_prism": (GOBO,),
    "tempo_2_no_gobo": (PRISM,),
    "tempo_2_no_gobo_no_prism": (),
    "matrices_frame": (BAR, PANEL),
    "matrices_frame_bars": (BAR,),
    "matrices_frame_panels": (PANEL,),
    "matrices_frame_groups": (),
    "panels_frame": (PANEL,),
    "builtins_frame": (BUILTIN_EFFECTS,),
    "library_1": (BUILTIN_EFFECTS,),
    "library_2": (PANEL,),
    "library_2_no_panels": (BUILTIN_EFFECTS,),
    "library_6": (PANEL,),
    "library_6_no_panels": (BUILTIN_EFFECTS,),
    "library_7": (BUILTIN_EFFECTS,),
    "library_1_no_builtins": (),
    "library_2_no_builtins": (),
    "library_3": (),
    "library_4": (),
    "library_5": (),
    "library_8": (),
    "library_9": (),
    "page_control": (HAZE, BEAM_WHEEL),
    "page_control_no_haze": (BEAM_WHEEL,),
    "page_control_no_beam_wheel": (HAZE,),
    "page_control_no_haze_no_beam_wheel": (),
}
