"""Generate a channel walk for one fixture: what does each DMX channel do?

Five of this rig's fixtures are generic units with no manual and no reliable
chart online - the same model ships with different channel layouts. The only way
to settle it is on site: drive one channel at a time and watch. This builds
exactly that, one scene per channel plus a chaser stepping through them, so the
check is "press play and write down what moves" instead of an evening of
clicking.
"""

from dataclasses import dataclass

from ..fixture import patched_fixtures
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..workspace import Workspace


@dataclass(frozen=True)
class GeneratedProbe:
    fixture_id: int
    scene_ids: list[int]
    chaser_id: int | None


def generate_channel_probe(
    workspace: Workspace,
    fixture_id: int,
    value: int = 255,
    base_values: dict[int, int] | None = None,
    hold: int = 3000,
    make_chaser: bool = True,
    path: str = "Probe (generado)",
) -> GeneratedProbe:
    """One scene per channel of this fixture, each driving that channel alone.

    base_values holds other channels steady while probing - a moving head with a
    mechanical shutter shows nothing until its dimmer is open, so pass e.g.
    {6: 255}. Offsets are 0-based within the fixture, as everywhere in the API.
    """
    fixture = next(
        (f for f in patched_fixtures(workspace.root) if f.fixture_id == fixture_id),
        None,
    )
    if fixture is None:
        raise KeyError(f"no patched fixture with ID {fixture_id}")

    base = dict(base_values or {})
    scene_ids: list[int] = []
    for offset in range(fixture.channels):
        pairs = [(o, v) for o, v in base.items() if o != offset]
        pairs.append((offset, value))
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_scene(
                function_id,
                f"{fixture.name} CH{offset + 1:02d} = {value}",
                {fixture_id: pairs},
                path=path,
            )
        )
        scene_ids.append(function_id)

    chaser_id: int | None = None
    if make_chaser and scene_ids:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                f"Probe {fixture.name}",
                scene_ids,
                hold=hold,
                run_order="SingleShot",
                path=path,
            )
        )

    return GeneratedProbe(fixture_id=fixture_id, scene_ids=scene_ids, chaser_id=chaser_id)
