"""Scenes that step a wheel channel through its own labelled positions.

A gobo wheel, a colour wheel and a prism are all the same shape in a fixture
definition: one channel whose ranges are named. So one generator covers all
three - a scene per position across every fixture that has that wheel, plus a
chaser that walks them, which is what makes the beams change pattern on their
own.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.chaser import build_chaser
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace


@dataclass(frozen=True)
class GeneratedWheel:
    scene_ids: list[int]
    chaser_id: int | None


def generate_wheel_scenes(
    workspace: Workspace,
    library: FixtureLibrary,
    role: str = roles.GOBO,
    label: str = "Gobo",
    fixture_ids: Sequence[int] | None = None,
    dimmer_full: bool = True,
    hold: int = 4000,
    fade: int = 0,
    run_order: str = "Random",
    make_chaser: bool = True,
    path: str | None = None,
) -> GeneratedWheel:
    """One scene per wheel position, driven on every fixture that has the wheel.

    dimmer_full opens those fixtures' dimmers in each scene - a gobo nobody can
    see is not a check of anything. Raises when no fixture carries the role.
    """
    wanted = None if fixture_ids is None else set(fixture_ids)
    caps = [
        c for c in capabilities_of(workspace.root, library)
        if c.has_role(role) and (wanted is None or c.fixture.fixture_id in wanted)
    ]
    if not caps:
        raise ValueError(f"no fixture in this workspace has a {role} channel")

    folder = path if path is not None else f"{label} (generado)"
    # Position names come from the first fixture: they share the wheel.
    _, positions = caps[0].wheel_for_role(role)

    scene_ids: list[int] = []
    for index, position in enumerate(positions):
        values: dict[int, list[tuple[int, int]]] = {}
        for capability in caps:
            # Only the wheel itself. Every other channel that happens to share
            # the role stays where it is - see wheel_for_role.
            offset, _ = capability.wheel_for_role(role)
            pairs = [(offset, position.middle)]
            if dimmer_full:
                pairs += [
                    (offset, 255)
                    for offset in capability.offsets_for_role(roles.DIMMER)
                ]
            values[capability.fixture.fixture_id] = pairs

        function_id = next_function_id(workspace.root)
        name = position.name or f"{label} {index}"
        workspace.add_function(
            build_scene(function_id, f"{label} - {name}", values, path=folder)
        )
        scene_ids.append(function_id)

    chaser_id: int | None = None
    if make_chaser and scene_ids:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                f"{label} Animacion",
                scene_ids,
                fade_in=fade,
                hold=hold,
                fade_out=fade,
                run_order=run_order,
                path=folder,
            )
        )

    return GeneratedWheel(scene_ids=scene_ids, chaser_id=chaser_id)
