"""Which caption page 4's matrices frame carries: bars and panels only where the rig has them.

The frame said "patterns on the bars and panels" on a rig whose matrices run
over pars and heads: no group is made of pixels and nothing has built-in
effects (the small club, 2026-09-25, Plan C final review). It then said it on
any rig with pixel groups and built-in effects, whatever those fixtures were;
since the owner's delegated decision (2026-09-25) the nouns come from the
fixtures themselves: `is_bar` and `is_panel`.
"""


def matrices_frame_caption(has_bars: bool, has_panels: bool) -> str:
    """The catalogue identifier of the matrices frame's caption for this rig."""
    if has_bars and has_panels:
        return "matrices_frame"
    if has_bars:
        return "matrices_frame_bars"
    if has_panels:
        return "matrices_frame_panels"
    return "matrices_frame_groups"
