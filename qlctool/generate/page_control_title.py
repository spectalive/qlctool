"""Which title page 3 carries: it promises only the haze and beam wheels the rig has.

The title named "BEAM wheels" on a rig whose heads mix RGB and have no colour
wheel, so no beam wheel frame is built (the small club, 2026-09-25, Plan C
Task 4), just as it named haze on a rig with no haze light (preflight D9),
and it names no heads on a rig with nothing that pans and tilts (a pars-only
rig, 2026-09-26, round G), where no beam wheel is built either. Nor does it
name intensity where no intensity frame is drawn (an RGB-only rig, round G
review).
"""


def page_control_title(
    has_haze_light: bool,
    has_beam_wheel: bool,
    has_heads: bool = True,
    has_intensity: bool = True,
) -> str:
    """The catalogue identifier of page 3's title for this rig."""
    suffix = "" if has_intensity else "_no_intensity"
    if not has_heads:
        key = "page_control_no_heads" if has_haze_light else "page_control_no_haze_no_heads"
    elif has_beam_wheel:
        key = "page_control" if has_haze_light else "page_control_no_haze"
    elif has_haze_light:
        key = "page_control_no_beam_wheel"
    else:
        key = "page_control_no_haze_no_beam_wheel"
    return key + suffix
