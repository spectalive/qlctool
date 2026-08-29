"""Dimmer looks: two running chases and an odd/even ping-pong across the rig.

Colour is not the only thing that moves in the hand-built show - it also drives
*intensity* on its own, which is what keeps a static colour from reading as a
flood. Two shapes cover what it does, with the running shape available both
ways:

- a chase, an EFX in Dimmer mode with the fixtures spread around the path, so
  the intensity peak can run forward or backward along the rig;
- a ping-pong, two scenes that light the odd fixtures then the even ones,
  stepped by a fast chaser.

Both skip the smoke machines, and both skip any fixture whose definition has no
dimmer: an EFX in Dimmer mode drives the fixture's intensity channel, and a
fixture without one would just sit in the list doing nothing. Also skipped is
any fixture whose intensity already has another owner - the panels' dimmer
belongs to their mode cycle, which holds it at 255, and HTP means a chase
under a 255 can dip nothing: the fixture would ride along invisibly forever
("modo locura empieza todo blanco y normal", owner, 2026-08-29).
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..functions.chaser import build_chaser
from ..functions.collection import build_collection
from ..functions.efx import EFXFixture, build_efx
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..stepped_dimmer import stepped_dimmer_offsets
from ..shutter_open import shutter_open_pairs
from ..zoom_wide import zoom_wide_pairs
from ..workspace import Workspace
from .movement_efx import spread_offsets

MODE_DIMMER = 1  # EFXFixture::Mode - PanTilt, Dimmer, RGB


@dataclass(frozen=True)
class GeneratedDimmers:
    # One function per look, whatever it took to build it: when the dimmable
    # fixtures had to be split, each chase ID is a Collection over its own
    # halves, and part_ids carries the parts for both directions.
    chase_id: int
    chase2_id: int
    pingpong_id: int
    scene_ids: list[int]
    part_ids: list[int] = field(default_factory=list)


def generate_dimmer_chases(
    workspace: Workspace,
    library: FixtureLibrary,
    duration: int = 6000,
    pingpong_hold: int = 400,
    path: str = "Dimmers",
    exclude_fixture_ids: Sequence[int] = (),
) -> GeneratedDimmers:
    """Build both dimmer chases and the ping-pong; raise when nothing dims."""
    excluded = set(exclude_fixture_ids)
    # A blade dimmer is not a fader: an EFX sweeping it does not dip the beam,
    # it slides a blade across the lens and the head shows a crescent for most
    # of every pass (`stepped_dimmer`). Those fixtures stay out of the chase
    # rather than run a chase of half-moons.
    dimmable = [
        capability
        for capability in capabilities_of(workspace.root, library)
        if not capability.is_smoke
        and capability.fixture.fixture_id not in excluded
        and capability.offsets_for_role(roles.DIMMER)
        and not stepped_dimmer_offsets(capability)
    ]
    if not dimmable:
        raise ValueError("no fixture in this workspace has a dimmer")

    # The hand-built show did not run one intensity path over the whole rig: it
    # ran a *cascade per fixture family* - `Dimmer Chase CromoWash`, `... PC
    # LED`, `... Beam 7R 230W` - each a Serial Line EFX so the peak walks down
    # that family's own row, and a Collection lit them all at once. One
    # whole-rig Circle replaced that and lost the look (old-vs-new audit,
    # 2026-08-28); the family partition comes back here, by model, which is
    # the line the old EFX drew. Model families are homogeneous, so the 16-bit
    # adjacency question (see `efx_16bit`) is answered per family instead of
    # splitting one - a family whose dimmer fine channel is not adjacent runs
    # 8 bit on its own without turning it off for the rest.
    families: dict[tuple[str, str], list] = {}
    for capability in dimmable:
        fixture = capability.fixture
        families.setdefault((fixture.manufacturer, fixture.model), []).append(
            capability
        )
    parts = list(families.values())
    split = len(parts) > 1

    def _efx(name: str, members: list, folder: str, direction: str) -> int:
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_efx(
                function_id,
                name,
                [
                    EFXFixture(
                        fixture_id=capability.fixture.fixture_id,
                        mode=MODE_DIMMER,
                        direction=direction,
                        start_offset=offset,
                    )
                    for capability, offset in zip(
                        members, spread_offsets(len(members))
                    )
                ],
                # The old family EFX, verbatim in shape: Line with the pan
                # term killed (Width 0), full-height sweep, cascaded Serial
                # down the family's patch order.
                algorithm="Line",
                width=0,
                height=127,
                propagation_mode="Serial",
                duration=duration,
                path=folder,
            )
        )
        return function_id

    part_ids: list[int] = []

    def _chase(name: str, direction: str) -> int:
        if not split:
            return _efx(name, parts[0], path, direction)

        chase_part_ids: list[int] = []
        for members in parts:
            chase_part_ids.append(_efx(
                f"{name} {members[0].fixture.model}",
                members,
                f"{path}/Partes",
                direction,
            ))
        part_ids.extend(chase_part_ids)
        function_id = next_function_id(workspace.root)
        workspace.add_function(
            build_collection(function_id, name, chase_part_ids, path=path)
        )
        return function_id

    chase_id = _chase("Dimmer Chase", "Forward")
    chase2_id = _chase("Dimmer Chase 2", "Backward")

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
        chase_id=chase_id, chase2_id=chase2_id, pingpong_id=pingpong_id,
        scene_ids=scene_ids, part_ids=part_ids,
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
            pairs += zoom_wide_pairs(capability)
        values[capability.fixture.fixture_id] = pairs
    function_id = next_function_id(workspace.root)
    name = "Dimmer Impares" if remainder else "Dimmer Pares"
    workspace.add_function(build_scene(function_id, name, values, path=path))
    return function_id
