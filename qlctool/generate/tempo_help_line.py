"""Which middle line page 1's tempo help carries: it names only the layers the tap re-times.

The line said "gobos, prism and dimmer follow your beat" on a rig whose heads
have no gobo or prism wheel, so neither animation is built and the dial has
neither to re-time (the small club, 2026-09-25, Plan C final review).
"""


def tempo_help_line(has_gobo_animation: bool, has_prism_animation: bool) -> str:
    """The catalogue identifier of the tempo help's second line for this rig."""
    if has_gobo_animation:
        return "tempo_2" if has_prism_animation else "tempo_2_no_prism"
    if has_prism_animation:
        return "tempo_2_no_gobo"
    return "tempo_2_no_gobo_no_prism"
