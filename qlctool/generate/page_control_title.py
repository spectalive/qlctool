"""Which title page 3 carries: it promises only the haze and beam wheels the rig has.

The title named "BEAM wheels" on a rig whose heads mix RGB and have no colour
wheel, so no beam wheel frame is built (the small club, 2026-09-25, Plan C
Task 4), just as it named haze on a rig with no haze light (preflight D9).
"""


def page_control_title(has_haze_light: bool, has_beam_wheel: bool) -> str:
    """The catalogue identifier of page 3's title for this rig."""
    if has_beam_wheel:
        return "page_control" if has_haze_light else "page_control_no_haze"
    if has_haze_light:
        return "page_control_no_beam_wheel"
    return "page_control_no_haze_no_beam_wheel"
