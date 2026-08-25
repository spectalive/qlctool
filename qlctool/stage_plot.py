"""Read a written stage plot: where each fixture of a real rig actually stands.

The generated band layout guesses a readable arrangement from what fixtures can
do. A plot is the opposite - somebody measured or remembered the get-in and
wrote it down, so the toolkit's job is to apply it verbatim, not to improve it.

The plot names the model it expects at every fixture ID and the loader refuses a
workspace where they do not match, because a plot is bound to a patch: re-address
or unpatch anything and the IDs move under it. Failing loudly beats hanging a
beam where a smoke machine is.
"""

import json
from dataclasses import dataclass
from pathlib import Path

from lxml import etree

from .fixture import patched_fixtures
from .monitor_node import MonitorItem


@dataclass(frozen=True)
class StagePlot:
    name: str
    stage: tuple[int, int, int]
    point_of_view: str
    items: list[MonitorItem]
    # fixture id -> the human description of where it hangs
    places: dict[int, str]

    @property
    def rigged(self) -> list[int]:
        return [item.fixture_id for item in self.items if not item.hidden]

    @property
    def spare(self) -> list[int]:
        return [item.fixture_id for item in self.items if item.hidden]


def load_stage_plot(path: str | Path, root: etree._Element) -> StagePlot:
    """Parse a plot and check it against the patch it claims to describe."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = document["fixtures"]

    patched = {f.fixture_id: f for f in patched_fixtures(root)}
    planned = {int(entry["id"]) for entry in entries}
    missing = sorted(set(patched) - planned)
    if missing:
        raise ValueError(
            f"{path}: the patch has fixtures the plot does not place: {missing}"
        )
    unknown = sorted(planned - set(patched))
    if unknown:
        raise ValueError(
            f"{path}: the plot places fixtures that are not patched: {unknown}"
        )

    for entry in entries:
        fixture_id = int(entry["id"])
        expected = entry["model"]
        actual = patched[fixture_id].model
        if actual != expected:
            raise ValueError(
                f"{path}: fixture {fixture_id} is a {actual!r} in the patch but "
                f"the plot expects a {expected!r} - the plot is stale"
            )

    width, height, depth = document["stage"]
    return StagePlot(
        name=document.get("name", Path(path).stem),
        stage=(int(width), int(height), int(depth)),
        point_of_view=document.get("point_of_view", "front"),
        items=[
            MonitorItem(
                fixture_id=int(entry["id"]),
                x=float(entry["x"]),
                y=float(entry["y"]),
                z=float(entry["z"]),
                hidden=bool(entry.get("hidden", False)),
                x_rot=float(entry.get("x_rot", 0)),
                y_rot=float(entry.get("y_rot", 0)),
                z_rot=float(entry.get("z_rot", 0)),
            )
            for entry in entries
        ],
        places={int(entry["id"]): entry.get("place", "") for entry in entries},
    )
