"""Place every patched fixture in the 2D/3D stage view.

QLC+ keeps the preview positions in `<Monitor>`, one `<FxItem>` per fixture, in
millimetres inside a grid measured in metres. A workspace that never had them
written - which is every show this toolkit generates, because the patch it
copies only carried four of them - stacks all 27 fixtures on the same spot, and
both views come out unreadable.

This writes the whole node: a stage big enough for the rig, an explicit point of
view, and a row per band (see `band_of`) with the fixtures of that band spread
evenly across the stage width. It is a starting plot, not a survey - the rig has
never been measured - so the numbers are deliberately round and easy to drag
somewhere better in QLC+.

The point of view matters more than it looks: with none stored, QLC+ asks for
one the first time the 2D view opens and then *converts every position it has*,
which silently rewrites a layout that was already right.
"""

from ..band_of import BANDS, PARS, band_of
from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..monitor_item import MonitorItem
from ..patched_fixtures import patched_fixtures
from ..workspace import Workspace
from ..write_monitor import write_monitor
from .generated_stage import GeneratedStage
from .spread import spread

# Grid in metres (width, height, depth): a small-venue stage with a truss over
# it. QLC+ writes these as integers.
DEFAULT_STAGE = (12, 6, 8)

# Where each band sits, as a fraction of stage height and stage depth. Beams
# upstage on the high truss, washes downstage on a lower one, bars and PARs on
# the floor. The two truss heights are a stage metre apart on purpose: the 2D
# view collapses depth, so rows that differ only in Z land on top of each other
# there.
BAND_ROWS = {
    "beams": (0.80, 0.82),
    "washes": (0.58, 0.20),
    "bars": (0.02, 0.88),
    "pars": (0.06, 0.10),
    "smoke": (0.00, 0.95),
}

# Clear space kept at each end of a row, as a fraction of the stage width. A
# stored position is the fixture's *near corner*, not its centre (QLC+ adds
# half the mesh extents), so the margin has to cover the widest fixture or the
# last one in a row hangs over the edge of the grid.
SIDE_MARGIN = 0.10


def generate_stage_layout(
    workspace: Workspace,
    library: FixtureLibrary,
    stage: tuple[int, int, int] = DEFAULT_STAGE,
    point_of_view: str = "front",
) -> GeneratedStage:
    """Rewrite `<Monitor>` with a position for every patched fixture."""
    band_by_id = {
        c.fixture.fixture_id: band_of(c) for c in capabilities_of(workspace.root, library)
    }
    # A fixture whose definition the library does not have still needs a spot,
    # and the front row is where an unknown light is least in the way.
    rows: dict[str, list[int]] = {band: [] for band in BANDS}
    for fixture in patched_fixtures(workspace.root):
        rows[band_by_id.get(fixture.fixture_id, PARS)].append(fixture.fixture_id)

    width, height, depth = stage
    positions: dict[int, tuple[float, float, float]] = {}
    for band, fixture_ids in rows.items():
        y_fraction, z_fraction = BAND_ROWS[band]
        y = round(height * 1000 * y_fraction)
        z = round(depth * 1000 * z_fraction)
        for fixture_id, x in zip(
            fixture_ids,
            spread(len(fixture_ids), width * 1000, width * 1000 * SIDE_MARGIN),
            strict=True,
        ):
            positions[fixture_id] = (round(x), y, z)

    write_monitor(
        workspace,
        stage,
        point_of_view,
        [MonitorItem(fixture_id=fid, x=x, y=y, z=z) for fid, (x, y, z) in positions.items()],
    )
    return GeneratedStage(
        stage=stage,
        point_of_view=point_of_view,
        rows={band: ids for band, ids in rows.items() if ids},
    )
