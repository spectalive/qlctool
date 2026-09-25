"""Which caption page 4's built-in effects frame carries: "panels" only where they are panels.

The frame said "Panels - their N built-in effects" on any rig with built-in
effects; since the owner's delegated decision (2026-09-25) it names panels only
where a fixture is one (`is_panel`), and otherwise the effects without a noun.
"""


def panels_frame_caption(has_panels: bool) -> str:
    """The catalogue identifier of the built-in effects frame's caption for this rig."""
    return "panels_frame" if has_panels else "builtins_frame"
