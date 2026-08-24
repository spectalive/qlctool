"""Generate movement EFX across every moving head in the patch.

Finding the movers, spreading their phase so they do not all point the same way,
and repeating the whole thing per shape is exactly the clicking the owner wants
gone. Fixtures are selected by capability (they have pan and tilt), so a re-patch
does not invalidate the generator.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from .. import roles
from ..capabilities_of import capabilities_of
from ..efx_algorithms import EFX_ALGORITHMS, SPANISH_LABELS
from ..functions.chaser import build_chaser
from ..functions.efx import EFXFixture, build_efx
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..workspace import Workspace


@dataclass(frozen=True)
class GeneratedMovements:
    efx_ids: list[int]
    chaser_id: int | None


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
    chaser_hold: int = 4000,
    chaser_run_order: str = "Loop",
) -> GeneratedMovements:
    """Create one EFX per algorithm over the moving heads.

    fixture_ids overrides the automatic pan+tilt selection. Raises when no
    fixture can move - an EFX with no fixtures loads but does nothing.
    """
    ids = list(fixture_ids) if fixture_ids is not None else moving_head_ids(
        workspace, library
    )
    if not ids:
        raise ValueError("no fixture in this workspace has both pan and tilt")

    offsets = spread_offsets(len(ids))
    members = [
        EFXFixture(fixture_id=fid, start_offset=offset)
        for fid, offset in zip(ids, offsets)
    ]

    efx_ids: list[int] = []
    for algorithm in algorithms:
        fid = next_function_id(workspace.root)
        label = SPANISH_LABELS.get(algorithm, algorithm)
        workspace.add_function(
            build_efx(
                fid,
                f"Movimiento {label}",
                members,
                algorithm=algorithm,
                propagation_mode=propagation_mode,
                duration=duration,
                path=path,
            )
        )
        efx_ids.append(fid)

    chaser_id: int | None = None
    if make_chaser and efx_ids:
        chaser_id = next_function_id(workspace.root)
        workspace.add_function(
            build_chaser(
                chaser_id,
                "Movimientos Cabezas",
                efx_ids,
                hold=chaser_hold,
                run_order=chaser_run_order,
                path=path,
            )
        )

    return GeneratedMovements(efx_ids=efx_ids, chaser_id=chaser_id)
