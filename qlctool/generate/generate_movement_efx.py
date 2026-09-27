"""Generate movement EFX across every moving head in the patch.

Finding the movers, spreading their phase so they do not all point the same way,
and repeating the whole thing per shape is exactly the clicking the owner wants
gone. Fixtures are selected by capability (they have pan and tilt), so a re-patch
does not invalidate the generator.
"""

from collections.abc import Collection, Sequence

from ..capabilities_of import capabilities_of
from ..efx_algorithms import EFX_ALGORITHMS
from ..efx_shape_identifiers import EFX_SHAPE_IDENTIFIERS
from ..fixture_library import FixtureLibrary
from ..functions.build_chaser import build_chaser
from ..functions.build_collection import build_collection
from ..functions.build_efx import build_efx
from ..functions.efx import EFXFixture
from ..functions.efx_axis import EFXAxis
from ..keeps_16bit import PAN_TILT_PAIRS, keeps_16bit
from ..names.default_names import default_names
from ..names.names import Names
from ..next_function_id import next_function_id
from ..workspace import Workspace
from .generated_movements import GeneratedMovements
from .moving_head_ids import moving_head_ids
from .spread_offsets import spread_offsets


def generate_movement_efx(
    workspace: Workspace,
    library: FixtureLibrary,
    algorithms: Sequence[str] = EFX_ALGORITHMS,
    fixture_ids: Sequence[int] | None = None,
    path: str | None = None,
    make_chaser: bool = True,
    propagation_mode: str = "Parallel",
    duration: int = 6848,
    width: int = 100,
    height: int = 100,
    chaser_hold: int = 4000,
    chaser_run_order: str = "Loop",
    chaser_name: str | None = None,
    label_prefix: str | None = None,
    mirrored_ids: Collection[int] = (),
    rotation: int = 0,
    rotation_by_algorithm: dict[str, int] | None = None,
    size_by_algorithm: dict[str, tuple[int, int]] | None = None,
    names: dict[str, str] | None = None,
    spread_phase: bool = True,
    pan_offset: int = 127,
    tilt_offset: int = 127,
    vocabulary: Names | None = None,
    rigged_ids: Collection[int] | None = None,
) -> GeneratedMovements:
    """Create one EFX per algorithm over the moving heads.

    fixture_ids overrides the automatic pan+tilt selection. Raises when no
    fixture can move - an EFX with no fixtures loads but does nothing.

    mirrored_ids run the path backwards, which is how a rig gets symmetry: with
    every head going the same way round, the room sweeps in parallel, and with
    one side reversed the pairs open and close together. Pass the fixtures on
    one side of the centre line - `house_right_fixture_ids` reads them off the
    plot.

    rotation applies to every algorithm in the batch; rotation_by_algorithm
    overrides it for individual shapes (e.g. Diamond and Leaf wanting
    different angles in the same call). size_by_algorithm overrides width
    and height the same way, as (width, height) per shape - a turned figure
    reaches further than its size, so it is drawn at the size that fits
    (`fit_rotated_figure`). names overrides the generated
    "{label_prefix} {label}" name for an algorithm with a literal one, for a
    figure whose name does not fit that pattern (e.g. "Ola Suave").

    pan_offset and tilt_offset are where the figure is *centred*, in raw DMX -
    the aim the whole shape is drawn around. QLC+ defaults both to 127, the
    middle of the channel, which is not an aim but the absence of one: on this
    rig it puts a beam on the floor (`movement_aim`).

    spread_phase=False puts every fixture at StartOffset 0 - the synced push,
    where the whole rig traces the same point of the path at the same instant.
    Spreading the phase is what desynchronises heads; a push is the one look
    whose point is that nobody is desynchronised (mirroring still applies, so
    the two sides push toward each other rather than in parallel).

    rigged_ids, when given, are the heads the room can see: the phase is
    spread over them alone, and the others - spares in a flight case - share
    a spread of their own, so they never take a visible head's slot. Two
    rigged MACs among six spares sat 45 degrees apart instead of opposite
    (en-sala DMX audit, 2026-09-26). None counts every head as rigged.

    `path`, `chaser_name` and `label_prefix` default to the generated movement
    folder, the head-movements chaser and the movement prefix of `vocabulary`,
    the show's vocabulary (`names` keeps its older meaning: per-shape names).
    """
    words = default_names() if vocabulary is None else vocabulary
    path = words.display("path_movement_generated") if path is None else path
    chaser_name = words.display("head_movements") if chaser_name is None else chaser_name
    label_prefix = words.display("prefix_movement") if label_prefix is None else label_prefix
    ids = list(fixture_ids) if fixture_ids is not None else moving_head_ids(workspace, library)
    if not ids:
        raise ValueError("no fixture in this workspace has both pan and tilt")

    # One EFX cannot hold both kinds of mover: a fixture whose fine channels are
    # not adjacent turns 16-bit off for the whole EFX, and the ones that *do*
    # pair then lose their coarse channels entirely. See `keeps_16bit`.
    by_id = {caps.fixture.fixture_id: caps for caps in capabilities_of(workspace.root, library)}
    groups: dict[bool, list[int]] = {True: [], False: []}
    for fid in ids:
        caps = by_id.get(fid)
        groups[True if caps is None else keeps_16bit(caps, PAN_TILT_PAIRS)].append(fid)
    parts = [(paired, members) for paired, members in groups.items() if members]

    mirrored = set(mirrored_ids)

    def _members(fixture_ids: list[int]) -> list[EFXFixture]:
        seen = [fid for fid in fixture_ids if rigged_ids is None or fid in rigged_ids]
        spares = [fid for fid in fixture_ids if fid not in seen]
        phase = {
            **dict(zip(seen, spread_offsets(len(seen)), strict=True)),
            **dict(zip(spares, spread_offsets(len(spares)), strict=True)),
        }
        return [
            EFXFixture(
                fixture_id=fid,
                start_offset=phase[fid] if spread_phase else 0,
                direction="Backward" if fid in mirrored else "Forward",
            )
            for fid in fixture_ids
        ]

    efx_ids: list[int] = []
    part_ids: list[int] = []
    split = len(parts) > 1
    part_path = words.render("path_parts", path=path) if split else path

    for algorithm in algorithms:
        label = (
            words.display(EFX_SHAPE_IDENTIFIERS[algorithm])
            if algorithm in EFX_SHAPE_IDENTIFIERS
            else algorithm
        )
        name = (names or {}).get(algorithm, f"{label_prefix} {label}")
        shape_rotation = (rotation_by_algorithm or {}).get(algorithm, rotation)
        shape_width, shape_height = (size_by_algorithm or {}).get(algorithm, (width, height))
        shape_parts: list[int] = []
        for paired, part_fixture_ids in parts:
            fid = next_function_id(workspace.root)
            suffix = f" ({'16 bit' if paired else '8 bit'})" if split else ""
            workspace.add_function(
                build_efx(
                    fid,
                    f"{name}{suffix}",
                    _members(part_fixture_ids),
                    algorithm=algorithm,
                    # The axis defaults QLC+ writes for a plain circle, with
                    # the centre moved off mid-travel onto the rig's own aim.
                    x_axis=EFXAxis(offset=pan_offset, phase=90),
                    y_axis=EFXAxis(offset=tilt_offset, frequency=3),
                    propagation_mode=propagation_mode,
                    rotation=shape_rotation,
                    duration=duration,
                    width=shape_width,
                    height=shape_height,
                    path=part_path if split else path,
                )
            )
            shape_parts.append(fid)

        if not split:
            efx_ids.append(shape_parts[0])
            continue

        # One button, one chaser step, both halves moving together.
        part_ids.extend(shape_parts)
        collection_id = next_function_id(workspace.root)
        workspace.add_function(build_collection(collection_id, name, shape_parts, path=path))
        efx_ids.append(collection_id)

    chaser_id: int | None = None
    if make_chaser and efx_ids:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                chaser_name,
                efx_ids,
                hold=chaser_hold,
                run_order=chaser_run_order,
                path=path,
            )
        )

    return GeneratedMovements(efx_ids=efx_ids, chaser_id=chaser_id, part_ids=part_ids)
