"""Held palette-colour flashes that keep Flash 100%'s safe shutter behavior."""

from collections.abc import Mapping, Sequence

from ..fixture_capabilities import FixtureCapabilities
from ..functions.scene import build_scene
from ..names.default_names import default_names
from ..names.names import Names
from ..next_function_id import next_function_id
from ..strobe_speed_pairs import strobe_speed_pairs
from ..workspace import Workspace
from .color_scene_values import color_scene_values
from .generated_color_flashes import GeneratedColorFlashes as _GeneratedColorFlashes
from .wheel_color_values import wheel_color_values


def generate_color_flashes(
    workspace: Workspace,
    capabilities: Sequence[FixtureCapabilities],
    colors: Mapping[str, tuple[int, int, int]],
    strobe_fraction: float,
    path: str | None = None,
    names: Names | None = None,
) -> _GeneratedColorFlashes:
    """Generate one full-output held flash per palette solid.

    The fixture footprint exactly follows `Flash 100%`: illuminated smoke
    fixtures join the colour hit, and no smoke pump is written. The hit is held
    with ForceLTP, so a pump zero would cut a smoke burst in progress; a held
    flash neither starts nor stops smoke (ruling D1, 2026-09-26).
    `names` is the show's vocabulary; `path` defaults to its hits folder.
    """
    vocabulary = default_names() if names is None else names
    path = vocabulary.display("path_hits") if path is None else path
    generated: dict[str, int] = {}
    for color_name, rgb in colors.items():
        values = color_scene_values(list(capabilities), rgb)
        for fixture_id, pairs in wheel_color_values(
            list(capabilities), color_name, names=vocabulary
        ).items():
            merged = dict(values.get(fixture_id, []))
            merged.update(pairs)
            values[fixture_id] = sorted(merged.items())
        for capability in capabilities:
            # `Flash 100%`'s footprint, strobe included: the lit columns strobe
            # their LED, the pump is untouched (ruling D3, 2026-09-26).
            if capability.is_smoke and not capability.is_lit_smoke:
                continue
            strobe = strobe_speed_pairs(capability, strobe_fraction)
            if not strobe:
                continue
            fixture_id = capability.fixture.fixture_id
            merged = dict(values.get(fixture_id, []))
            merged.update(strobe)
            values[fixture_id] = sorted(merged.items())
        function_id = next_function_id(workspace.root)
        name = vocabulary.render("colour_hit", colour=color_name)
        workspace.add_function(build_scene(function_id, name, values, path=path))
        generated[color_name] = function_id
    return _GeneratedColorFlashes(ids=generated)
