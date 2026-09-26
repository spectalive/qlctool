"""Which middle line page 1's tempo help carries: it names only the layers the tap re-times.

The line said "gobos, prism and dimmer follow your beat" on a rig whose heads
have no gobo or prism wheel, so neither animation is built and the dial has
neither to re-time (the small club, 2026-09-25, Plan C final review). A
rig with no dimmer chase has no dimmer to name either (a washes-only rig,
2026-09-26, round G).
"""


def tempo_help_line(
    has_gobo_animation: bool, has_prism_animation: bool, has_dimmer_chase: bool = True
) -> str:
    """The catalogue identifier of the tempo help's second line for this rig."""
    if has_gobo_animation:
        key = "tempo_2" if has_prism_animation else "tempo_2_no_prism"
    elif has_prism_animation:
        key = "tempo_2_no_gobo"
    else:
        key = "tempo_2_no_gobo_no_prism"
    return key if has_dimmer_chase else f"{key}_no_dimmer"
