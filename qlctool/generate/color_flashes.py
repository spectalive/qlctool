"""Held palette-colour flashes that keep Flash 100%'s safe shutter behavior."""

from collections.abc import Mapping, Sequence

from ..capability import FixtureCapabilities
from ..fog_off import fog_off_pairs
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..strobe_speed import strobe_speed_pairs
from ..workspace import Workspace
from .color_scene import color_scene_values
from .generated_color_flashes import GeneratedColorFlashes as _GeneratedColorFlashes
from .wheel_color_values import wheel_color_values


def generate_color_flashes(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    colors: Mapping[str, tuple[int, int, int]],
    strobe_fraction: float,
    path: str = "Golpes",
) -> _GeneratedColorFlashes:
    """Generate one full-output held flash per palette solid.

    The fixture footprint exactly follows `Flash 100%`: illuminated smoke
    fixtures join the colour hit, while every smoke pump stays explicitly off.
    """
    generated: dict[str, int] = {}
    for color_name, rgb in colors.items():
        values = color_scene_values(list(capabilities), rgb)
        for capability in capabilities:
            off = fog_off_pairs(capability)
            if not off:
                continue
            fixture_id = capability.fixture.fixture_id
            merged = dict(values.get(fixture_id, []))
            merged.update(off)
            values[fixture_id] = sorted(merged.items())
        for fixture_id, pairs in wheel_color_values(list(capabilities), color_name).items():
            merged = dict(values.get(fixture_id, []))
            merged.update(pairs)
            values[fixture_id] = sorted(merged.items())
        for capability in capabilities:
            if capability.is_smoke:
                continue
            strobe = strobe_speed_pairs(capability, strobe_fraction)
            if not strobe:
                continue
            fixture_id = capability.fixture.fixture_id
            merged = dict(values.get(fixture_id, []))
            merged.update(strobe)
            values[fixture_id] = sorted(merged.items())
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_scene(function_id, f"Golpe {color_name}", values, path=path))
        generated[color_name] = function_id
    return _GeneratedColorFlashes(ids=generated)
