"""One colour on every colour-capable fixture, as a scene of the show."""

from collections.abc import Sequence

from ..capability import FixtureCapabilities
from ..fog_off import fog_off_pairs
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..names.names import Names
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace
from .color_scene import color_scene_values
from .show_path import SHOW_PATH
from .wheel_color_values import wheel_color_values


def flat_scene(
    workspace: Workspace,
    caps: list[FixtureCapabilities],
    name: str,
    rgb: tuple[int, int, int],
    names: Names | None = None,
    wheel_color: str | None = None,
    wheel_dimmer: int = 255,
    strobe: float | None = None,
    dimmer_full: bool = True,
    exclude_effect_mode_fixture_ids: Sequence[int] = (),
) -> int:
    """One colour on every colour-capable fixture; smoke machines excluded.

    `wheel_color` names the palette colour to put the wheel-coloured fixtures
    on - the beams, which have no RGB and are otherwise skipped. `strobe`
    additionally drives every strobe channel at that point of its slow-to-fast
    run, overriding the open-shutter values a plain look carries - which is
    what turns the work light into a flash. `names` is the vocabulary
    `wheel_color` is spelled in.
    """
    values = color_scene_values(
        caps,
        rgb,
        dimmer_full=dimmer_full,
        exclude_effect_mode_fixture_ids=exclude_effect_mode_fixture_ids,
    )
    # The pump, shut. A work light is a room state, and a room state that never
    # writes the pump is what a released smoke flash latches against.
    for capability in caps:
        off = fog_off_pairs(capability)
        if off:
            merged = dict(values.get(capability.fixture.fixture_id, []))
            merged.update(off)
            values[capability.fixture.fixture_id] = sorted(merged.items())
    if wheel_color is not None:
        values.update(wheel_color_values(caps, wheel_color, dimmer=wheel_dimmer, names=names))
    if strobe is not None:
        for capability in caps:
            if capability.is_smoke:
                continue
            strobing = strobe_speed_pairs(capability, strobe)
            if not strobing:
                continue
            fixture_id = capability.fixture.fixture_id
            merged = dict(values.get(fixture_id, []))
            merged.update(strobing)
            values[fixture_id] = sorted(merged.items())
    function_id = next_function_id(workspace.root)
    workspace.add_function(build_scene(function_id, name, values, path=SHOW_PATH))
    return function_id
