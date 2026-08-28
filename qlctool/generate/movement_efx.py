"""Generate movement EFX across every moving head in the patch.

Finding the movers, spreading their phase so they do not all point the same way,
and repeating the whole thing per shape is exactly the clicking the owner wants
gone. Fixtures are selected by capability (they have pan and tilt), so a re-patch
does not invalidate the generator.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..efx_algorithms import EFX_ALGORITHMS, SPANISH_LABELS
from ..functions.chaser import build_chaser
from ..functions.efx import EFXFixture, build_efx
from ..ids import next_function_id
from ..functions.collection import build_collection
from ..library import FixtureLibrary
from ..efx_16bit import PAN_TILT_PAIRS, keeps_16bit
from ..workspace import Workspace


@dataclass(frozen=True)
class GeneratedMovements:
    # What the console and the chaser see: one function per shape. When the
    # movers had to be split it is a Collection running both halves at once.
    efx_ids: list[int]
    chaser_id: int | None
    # The EFX underneath, when a split happened. Empty when there was none.
    part_ids: list[int] = field(default_factory=list)


def moving_head_ids(workspace: Workspace, library: FixtureLibrary) -> list[int]:
    """Fixture IDs that can be driven by an EFX: they have both pan and tilt."""
    return [
        caps.fixture.fixture_id
        for caps in capabilities_of(workspace.root, library)
        if caps.has_role(roles.PAN) and caps.has_role(roles.TILT)
    ]


def spread_offsets(count: int) -> list[int]:
    """Phase offsets spreading `count` fixtures evenly around the path."""
    if count <= 0:
        return []
    return [round(360 * index / count) % 360 for index in range(count)]


def generate_movement_efx(
    workspace: Workspace,
    library: FixtureLibrary,
    algorithms: Sequence[str] = EFX_ALGORITHMS,
    fixture_ids: Sequence[int] | None = None,
    path: str = "Movimiento (generado)",
    make_chaser: bool = True,
    propagation_mode: str = "Parallel",
    duration: int = 6848,
    width: int = 100,
    height: int = 100,
    chaser_hold: int = 4000,
    chaser_run_order: str = "Loop",
    chaser_name: str = "Movimientos Cabezas",
    label_prefix: str = "Movimiento",
    mirrored_ids: Sequence[int] = (),
    rotation: int = 0,
    rotation_by_algorithm: dict[str, int] | None = None,
    names: dict[str, str] | None = None,
    spread_phase: bool = True,
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
    different angles in the same call). names overrides the generated
    "{label_prefix} {label}" name for an algorithm with a literal one, for a
    figure whose name does not fit that pattern (e.g. "Ola Suave").

    spread_phase=False puts every fixture at StartOffset 0 - the synced push,
    where the whole rig traces the same point of the path at the same instant.
    Spreading the phase is what desynchronises heads; a push is the one look
    whose point is that nobody is desynchronised (mirroring still applies, so
    the two sides push toward each other rather than in parallel).
    """
    ids = list(fixture_ids) if fixture_ids is not None else moving_head_ids(
        workspace, library
    )
    if not ids:
        raise ValueError("no fixture in this workspace has both pan and tilt")

    # One EFX cannot hold both kinds of mover: a fixture whose fine channels are
    # not adjacent turns 16-bit off for the whole EFX, and the ones that *do*
    # pair then lose their coarse channels entirely. See `efx_16bit`.
    by_id = {
        caps.fixture.fixture_id: caps
        for caps in capabilities_of(workspace.root, library)
    }
    groups: dict[bool, list[int]] = {True: [], False: []}
    for fid in ids:
        caps = by_id.get(fid)
        groups[True if caps is None else keeps_16bit(caps, PAN_TILT_PAIRS)].append(fid)
    parts = [(paired, members) for paired, members in groups.items() if members]

    mirrored = set(mirrored_ids)

    def _members(fixture_ids: list[int]) -> list[EFXFixture]:
        offsets = (
            spread_offsets(len(fixture_ids))
            if spread_phase
            else [0] * len(fixture_ids)
        )
        return [
            EFXFixture(
                fixture_id=fid,
                start_offset=offset,
                direction="Backward" if fid in mirrored else "Forward",
            )
            for fid, offset in zip(fixture_ids, offsets)
        ]

    efx_ids: list[int] = []
    part_ids: list[int] = []
    split = len(parts) > 1
    part_path = f"{path}/Partes" if split else path

    for algorithm in algorithms:
        label = SPANISH_LABELS.get(algorithm, algorithm)
        name = (names or {}).get(algorithm, f"{label_prefix} {label}")
        shape_rotation = (rotation_by_algorithm or {}).get(algorithm, rotation)
        shape_parts: list[int] = []
        for paired, fixture_ids in parts:
            fid = next_function_id(workspace.root)
            suffix = f" ({'16 bit' if paired else '8 bit'})" if split else ""
            workspace.add_function(
                build_efx(
                    fid,
                    f"{name}{suffix}",
                    _members(fixture_ids),
                    algorithm=algorithm,
                    propagation_mode=propagation_mode,
                    rotation=shape_rotation,
                    duration=duration,
                    width=width,
                    height=height,
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
        workspace.add_function(
            build_collection(collection_id, name, shape_parts, path=path)
        )
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

    return GeneratedMovements(
        efx_ids=efx_ids, chaser_id=chaser_id, part_ids=part_ids
    )
