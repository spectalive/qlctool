"""Which caption page 4's matrices frame carries: bars and panels only where the rig has them.

The frame said "patterns on the bars and panels" on a rig whose matrices run
over pars and heads: no group is made of pixels and nothing has built-in
effects (the small club, 2026-09-25, Plan C final review).
"""


def matrices_frame_caption(has_pixel_groups: bool, has_builtin_effects: bool) -> str:
    """The catalogue identifier of the matrices frame's caption for this rig."""
    if has_pixel_groups and has_builtin_effects:
        return "matrices_frame"
    return "matrices_frame_groups"
