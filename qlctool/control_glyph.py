"""One glyph per control, so a button says what it does before it is read.

"Ni un solo icono en los botones" (owner, 2026-09-22), looking at a console of
593 buttons whose only non-text mark was the flash hits' colour. QLC+ can carry
a real icon per button - `<Icon>` is a file path - but a path is a promise about
the show Mac's disk, and a missing file is a silently blank button on the one
machine that matters. A glyph travels inside the caption: it survives the
workspace, the tablet desk reading the same map, and a fresh install.

The map is by control, not by kind, because that is what a person recognises: a
haze rhythm and a haze burst are the same cloud, and the four room states are
four different rooms. Anything not named here keeps a plain caption - a glyph
nobody can decode is worse than none.

Keys are catalogue identifiers; the show localises them to its display names
where it builds the console (`localised_keys`).
"""

GLYPHS: dict[str, str] = {
    # The room states.
    "auto": "▶",
    "talk_moment": "🎤",
    "calm_moment": "🌙",
    "party_moment": "🎉",
    "frenzy_moment": "🔥",
    "full_white": "💡",
    "all_black": "⏹",
    # The hits.
    "flash_full": "⚡",
    "flash_half": "⚡",
    "flash_colour": "🎨",
    "smoke_on": "☁",
    "vertical_smoke_now": "⇧",
    "vertical_smoke": "⇧",
    "strobe_fast": "✳",
    "strobe_medium": "✳",
    # The haze rhythms, all one family.
    "smoke_auto": "☁",
    "smoke_auto_2_min": "☁",
    "smoke_auto_4_min": "☁",
    "smoke_auto_8_min": "☁",
    # The layers of the JUGAR page.
    "colour_wheel": "🎨",
    "simple_wheel": "🎨",
    "pastel_wheel": "🎨",
    "multicolour_wheel": "🎨",
    "mix_wheel": "🎨",
    "talk_light": "🎤",
    "head_movements": "↔",
    "soft_movements": "↔",
    "fast_movements": "↔",
    "heads_centre": "◎",
    "gobo_animation": "❋",
    "prism_animation": "✧",
    "rainbow_together": "🌈",
    "rainbow_steps": "🌈",
    "dimmer_chase": "◐",
    "dimmer_chase_2": "◑",
    "dimmer_sequence": "◒",
    "dimmer_pingpong": "◓",
    "strobe_on": "✳",
    "strobe_off": "✳",
}


def glyph(identifier: str) -> str:
    """The glyph for this control's catalogue identifier, or "" when it has none."""
    return GLYPHS.get(identifier, "")
