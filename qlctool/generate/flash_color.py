"""The flash that keeps the colour: dimmer and shutter only, RGB untouched.

The hand-built console had it on `.` as "Flash Colores": hold it and the rig
strobes in whatever colour is already running, because the scene raises every
dimmer and drives every strobe channel without writing a single colour value.
A Scene only touches the channels it lists, so everything not listed - the
colour bed, the wheel position, the panels' programme - carries on underneath.
"""

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace
from ..zoom_wide import zoom_wide_pairs

NAME = "Flash Color"


def generate_flash_color(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    fraction: float,
    path: str = "Show",
) -> int:
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in capabilities:
        if capability.is_smoke:
            continue
        pairs = dict(strobe_speed_pairs(capability, fraction))
        # The dimmer after the strobe: on a combined dimmer/strobe channel the
        # strobing value *is* the intensity, so it must not be overwritten by
        # a flat 255 that the definition labels "Open".
        for offset in capability.offsets_for_role(roles.DIMMER):
            pairs.setdefault(offset, 255)
        # It flashes whatever colour is running, but the beam's width is not
        # part of "whatever is running" until some look has stated it: on a
        # cold desk a zoom nobody wrote is the narrowest the head has.
        for offset, value in zoom_wide_pairs(capability):
            pairs.setdefault(offset, value)
        if pairs:
            values[capability.fixture.fixture_id] = sorted(pairs.items())
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, NAME, values, path=path))
    return function_id
