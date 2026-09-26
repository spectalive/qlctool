"""Which last line page 1's tempo help carries: it sends to page 3's heads only where there are some.

The line said "the heads do too (page 3)" on a rig with nothing that pans and
tilts, where page 3 has no movement dial (a pars-only rig, 2026-09-26, round G).
"""


def tempo_close_line(has_heads: bool) -> str:
    """The catalogue identifier of the tempo help's last line for this rig."""
    return "tempo_3" if has_heads else "tempo_3_no_heads"
