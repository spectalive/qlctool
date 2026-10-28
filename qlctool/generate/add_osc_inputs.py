"""Give the console an OSC address on every control, when the description asks for one.

Off unless `[controllers] osc` names a prefix: an OSC input is a network port
anybody on the venue's Wi-Fi can press the show from, so a show opens one only
when it says so (2026-10-28).
"""

from ..controllers.bind_osc_inputs import bind_osc_inputs
from ..controllers.pin_osc_input import pin_osc_input
from .show_build import ShowBuild


def add_osc_inputs(build: ShowBuild) -> int:
    """Patch the OSC universe and bind the console to it; the number of bindings added."""
    prefix = build.described.controllers.osc
    if prefix is None:
        return 0
    root = build.workspace.root
    universe = pin_osc_input(root)
    if universe is None:
        return 0
    return bind_osc_inputs(root, prefix, universe)
