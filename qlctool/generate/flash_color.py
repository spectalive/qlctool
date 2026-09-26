"""The flash that keeps the colour: dimmer and shutter only, RGB untouched.

The hand-built console had it on `.` as "Flash Colores": hold it and the rig
strobes in whatever colour is already running, because the scene raises every
dimmer and drives every strobe channel without writing a single colour value.
A Scene only touches the channels it lists, so everything not listed - the
colour bed, the wheel position, the panels' programme - carries on underneath.

The one exception is the lit smoke machines: they go white, exactly as
`Flash 100%` writes them, and their pump is left alone. "Si, el flash enciende
las maquinas de humo en blanco" (owner, 2026-09-26; `rule_flash_lit_smoke`).
"""

from .. import roles
from ..capability import FixtureCapabilities
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..names.default_names import default_names
from ..names.names import Names
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace
from ..zoom_wide import zoom_wide_pairs
from .color_scene import color_scene_values


def generate_flash_color(
    workspace: Workspace,
    capabilities: list[FixtureCapabilities],
    fraction: float,
    path: str = "Show",
    names: Names | None = None,
) -> int:
    """The strobe over the running colour, named in `names`, the show's vocabulary."""
    vocabulary = default_names() if names is None else names
    # The lit smoke machines in `Flash 100%`'s own white, minus the pump that
    # scene shuts: a held colour flash neither starts nor stops the smoke.
    values = color_scene_values(
        capabilities,
        (255, 255, 255),
        fixture_ids=[c.fixture.fixture_id for c in capabilities if c.is_lit_smoke],
    )
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
    workspace.add_function(
        build_scene(function_id, vocabulary.display("flash_colour"), values, path=path)
    )
    return function_id
