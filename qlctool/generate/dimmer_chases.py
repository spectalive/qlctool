"""Dimmer looks: a running chase and an odd/even ping-pong across the rig.

Colour is not the only thing that moves in the hand-built show - it also drives
*intensity* on its own, which is what keeps a static colour from reading as a
flood. Two shapes cover what it does:

- a chase, an EFX in Dimmer mode with the fixtures spread around the path, so
  the intensity peak runs along the rig;
- a ping-pong, two scenes that light the odd fixtures then the even ones,
  stepped by a fast chaser.

Both skip the smoke machines, and both skip any fixture whose definition has no
dimmer: an EFX in Dimmer mode drives the fixture's intensity channel, and a
fixture without one would just sit in the list doing nothing.
"""

from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..efx_16bit import INTENSITY_PAIRS, keeps_16bit
from ..functions.chaser import build_chaser
from ..functions.collection import build_collection
from ..functions.efx import EFXFixture, build_efx
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..shutter_open import shutter_open_pairs
from ..workspace import Workspace
from .movement_efx import spread_offsets

MODE_DIMMER = 1  # EFXFixture::Mode - PanTilt, Dimmer, RGB


@dataclass(frozen=True)
class GeneratedDimmers:
    # One function per look, whatever it took to build it: when the dimmable
    # fixtures had to be split, chase_id is a Collection over the halves.
    chase_id: int
    pingpong_id: int
    scene_ids: list[int]
    part_ids: list[int] = field(default_factory=list)


def generate_dimmer_chases(
    workspace: Workspace,
    library: FixtureLibrary,
    duration: int = 6000,
    pingpong_hold: int = 400,
    path: str = "Dimmers",
) -> GeneratedDimmers:
    """Build the dimmer chase and the ping-pong; raises when nothing dims."""
    dimmable = [
        capability
        for capability in capabilities_of(workspace.root, library)
        if not capability.is_smoke and capability.offsets_for_role(roles.DIMMER)
    ]
    if not dimmable:
        raise ValueError("no fixture in this workspace has a dimmer")

    # Same trap as the movement EFX, on the intensity channel instead: a fixture
    # whose dimmer fine channel is not adjacent turns 16 bit off for the whole
    # EFX. Nothing in this rig has one, so this is usually a single group - but
    # patch a fixture that does and it will be split rather than break the rest.
    # See `efx_16bit`.
    groups: dict[bool, list] = {True: [], False: []}
    for capability in dimmable:
        groups[keeps_16bit(capability, INTENSITY_PAIRS)].append(capability)
    parts = [members for members in groups.values() if members]
    split = len(parts) > 1

    def _efx(name: str, members: list, folder: str) -> int:
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_efx(
                function_id,
                name,
                [
                    EFXFixture(
                        fixture_id=capability.fixture.fixture_id,
                        mode=MODE_DIMMER,
                        start_offset=offset,
                    )
                    for capability, offset in zip(
                        members, spread_offsets(len(members))
                    )
                ],
                duration=duration,
                path=folder,
            )
        )
        return function_id

    part_ids: list[int] = []
    if not split:
        chase_id = _efx("Dimmer Chase", parts[0], path)
    else:
        for members in parts:
            paired = keeps_16bit(members[0], INTENSITY_PAIRS)
            part_ids.append(_efx(
                f"Dimmer Chase ({'16 bit' if paired else '8 bit'})",
                members,
                f"{path}/Partes",
            ))
        chase_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(chase_id, "Dimmer Chase", part_ids, path=path)
        )

    scene_ids = [
        _half_lit(workspace, dimmable, remainder, path) for remainder in (0, 1)
    ]
    pingpong_id = next_function_id(workspace.root)
    workspace.add_function(
        build_chaser(
            pingpong_id,
            "Dimmer PingPong",
            scene_ids,
            hold=pingpong_hold,
            path=path,
        )
    )
    return GeneratedDimmers(
        chase_id=chase_id, pingpong_id=pingpong_id, scene_ids=scene_ids,
        part_ids=part_ids,
    )


def _half_lit(workspace: Workspace, dimmable, remainder: int, path: str) -> int:
    """Every other fixture at full, the rest at zero.

    The lit half opens its shutter too - a beam at full dimmer behind a closed
    shutter shows nothing. The dark half is left alone: its dimmer at zero is
    already black, and closing the shutter as well only adds a second thing to
    reopen.
    """
    values = {}
    for index, capability in enumerate(dimmable):
        lit = index % 2 == remainder
        pairs = [
            (offset, 255 if lit else 0)
            for offset in capability.offsets_for_role(roles.DIMMER)
        ]
        if lit:
            pairs += shutter_open_pairs(capability)
        values[capability.fixture.fixture_id] = pairs
    function_id = next_function_id(workspace.root)
    name = "Dimmer Impares" if remainder else "Dimmer Pares"
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
