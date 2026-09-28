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

from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..functions.build_chaser import build_chaser
from ..functions.build_collection import build_collection
from ..functions.build_efx import build_efx
from ..functions.efx_fixture import EFXFixture
from ..names.default_names import default_names
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .fader_dimmed import fader_dimmed
from .generated_dimmers import GeneratedDimmers
from .half_lit import half_lit
from .spread_offsets import spread_offsets

MODE_DIMMER = 1  # EFXFixture::Mode - PanTilt, Dimmer, RGB


def generate_dimmer_chases(
    workspace: Workspace,
    library: FixtureLibrary,
    duration: int = 6000,
    pingpong_hold: int = 400,
    path: str = "Dimmers",
    exclude_fixture_ids: Sequence[int] = (),
    names: Names | None = None,
) -> GeneratedDimmers | None:
    """Build both dimmer chases and the ping-pong; None when nothing dims.

    A washes-only rig has no fader dimmer to chase (2026-09-26, round G): it
    gets no dimmer chase and every caller leaves the chase out.
    """
    vocabulary = default_names() if names is None else names
    excluded = set(exclude_fixture_ids)
    # A blade dimmer is not a fader: an EFX sweeping it does not dip the beam,
    # it slides a blade across the lens and the head shows a crescent for most
    # of every pass (`stepped_dimmer_offsets`). Those fixtures stay out of the chase
    # rather than run a chase of half-moons.
    dimmable = [
        capability
        for capability in capabilities_of(workspace.root, library)
        if capability.fixture.fixture_id not in excluded and fader_dimmed(capability)
    ]
    if not dimmable:
        return None

    # The hand-built show did not run one intensity path over the whole rig: it
    # ran a *cascade per fixture family* - `Dimmer Chase CromoWash`, `... PC
    # LED`, `... Beam 7R 230W` - each a Serial Line EFX so the peak walks down
    # that family's own row, and a Collection lit them all at once. One
    # whole-rig Circle replaced that and lost the look (old-vs-new audit,
    # 2026-08-28); the family partition comes back here, by model, which is
    # the line the old EFX drew. Model families are homogeneous, so the 16-bit
    # adjacency question (see `keeps_16bit`) is answered per family instead of
    # splitting one - a family whose dimmer fine channel is not adjacent runs
    # 8 bit on its own without turning it off for the rest.
    families: dict[tuple[str, str], list] = {}
    for capability in dimmable:
        fixture = capability.fixture
        families.setdefault((fixture.manufacturer, fixture.model), []).append(capability)
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
                        members, spread_offsets(len(members)), strict=True
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
            chase_part_ids.append(
                _efx(
                    f"{name} {members[0].fixture.model}",
                    members,
                    vocabulary.render("path_parts", path=path),
                    direction,
                )
            )
        part_ids.extend(chase_part_ids)
        function_id = next_function_id(workspace.root)
        workspace.add_function(build_collection(function_id, name, chase_part_ids, path=path))
        return function_id

    chase_id = _chase(vocabulary.display("dimmer_chase"), "Forward")
    chase2_id = _chase(vocabulary.display("dimmer_chase_2"), "Backward")

    # The ping-pong needs an odd half: with one dimmable fixture its odd step
    # lights nothing, and the chaser is a looping strobe hung from a button
    # (`latched_strobe`, `strobe_black`; the lone fixture, 2026-09-27).
    scene_ids: list[int] = []
    pingpong_id: int | None = None
    if len(dimmable) >= 2:
        scene_ids = [
            half_lit(workspace, dimmable, remainder, path, vocabulary) for remainder in (0, 1)
        ]
        pingpong_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                pingpong_id,
                vocabulary.display("dimmer_pingpong"),
                scene_ids,
                hold=pingpong_hold,
                path=path,
            )
        )
    return GeneratedDimmers(
        chase_id=chase_id,
        chase2_id=chase2_id,
        pingpong_id=pingpong_id,
        scene_ids=scene_ids,
        part_ids=part_ids,
    )
