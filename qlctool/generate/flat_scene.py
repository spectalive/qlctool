"""One colour on every colour-capable fixture, as a scene of the show."""

from collections.abc import Sequence

from ..capability import FixtureCapabilities
from ..fog_off import fog_off_pairs
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..names.names import Names
from ..strobe_speed import strobe_speed_pairs
from ..wheel_blade_offsets import wheel_blade_offsets
from ..workspace import Workspace
from .color_scene_values import color_scene_values
from .show_path import SHOW_PATH
from .wheel_color_values import wheel_color_values


def flat_scene(
    workspace: Workspace,
    caps: list[FixtureCapabilities],
    name: str,
    rgb: tuple[int, int, int],
    names: Names | None = None,
    wheel_color: str | None = None,
    wheel_dimmer: int | None = 255,
    strobe: float | None = None,
    dimmer_full: bool = True,
    exclude_effect_mode_fixture_ids: Sequence[int] = (),
    wheel_fixture_ids: Sequence[int] | None = None,
    pump_off: bool = True,
    blade_fixture_ids: Sequence[int] = (),
) -> int:
    """One colour on every colour-capable fixture; smoke machines excluded.

    `wheel_color` names the palette colour to put the wheel-coloured fixtures
    on - the beams, which have no RGB and are otherwise skipped. `strobe`
    additionally drives every strobe channel at that point of its slow-to-fast
    run, overriding the open-shutter values a plain look carries - which is
    what turns the work light into a flash. `names` is the vocabulary
    `wheel_color` is spelled in; `wheel_fixture_ids`, when given, limits the
    wheel colour to those fixtures. `pump_off` writes every smoke pump 0: a
    latched look is a room state and owns the pump; a held flash, forced LTP,
    must leave it alone (`rule_flash_forced_zero`). `blade_fixture_ids` are
    wheel-only heads whose colour a sibling scene of this look states: the
    look opens their blade, which goes with the colour (`wheel_blade_offsets`).
    """
    values = color_scene_values(
        caps,
        rgb,
        dimmer_full=dimmer_full,
        exclude_effect_mode_fixture_ids=exclude_effect_mode_fixture_ids,
    )
    # The pump, shut. A work light is a room state, and a room state that never
    # writes the pump is what a released smoke flash latches against. A held
    # flash neither starts nor stops smoke (ruling D1, 2026-09-26): forced LTP,
    # its zero would cut a smoke burst in progress.
    for capability in caps if pump_off else ():
        off = fog_off_pairs(capability)
        if off:
            merged = dict(values.get(capability.fixture.fixture_id, []))
            merged.update(off)
            values[capability.fixture.fixture_id] = sorted(merged.items())
    if wheel_color is not None:
        values.update(
            wheel_color_values(
                caps, wheel_color, fixture_ids=wheel_fixture_ids, dimmer=wheel_dimmer, names=names
            )
        )
    blades = set(blade_fixture_ids)
    for capability in caps:
        opened = [(o, 255) for o in wheel_blade_offsets(capability)]
        if capability.fixture.fixture_id not in blades or not opened:
            continue
        merged = dict(values.get(capability.fixture.fixture_id, []))
        merged.update(opened)
        values[capability.fixture.fixture_id] = sorted(merged.items())
    if strobe is not None:
        for capability in caps:
            # The lit columns strobe with the rig; their pump is no strobe
            # channel, so a flash never fires it (ruling D3, 2026-09-26).
            if capability.is_smoke and not capability.is_lit_smoke:
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
