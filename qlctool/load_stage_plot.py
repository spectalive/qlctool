"""Parse a written stage plot and check it against the patch it claims to describe."""

import json
from pathlib import Path

from lxml import etree

from .monitor_item import MonitorItem
from .patched_fixtures import patched_fixtures
from .prop_item import PropItem
from .stage_plot import StagePlot


def load_stage_plot(path: str | Path, root: etree._Element) -> StagePlot:
    """Parse a plot and check it against the patch it claims to describe."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = document["fixtures"]

    patched = {f.fixture_id: f for f in patched_fixtures(root)}
    planned = {int(entry["id"]) for entry in entries}
    missing = sorted(set(patched) - planned)
    if missing:
        raise ValueError(f"{path}: the patch has fixtures the plot does not place: {missing}")
    unknown = sorted(planned - set(patched))
    if unknown:
        raise ValueError(f"{path}: the plot places fixtures that are not patched: {unknown}")

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
        props=[
            PropItem(
                item_id=int(prop["id"]),
                resource=prop["mesh"],
                name=prop.get("name", ""),
                centre=(float(prop["cx"]), float(prop["cy"]), float(prop["cz"])),
                size=(float(prop["w"]), float(prop["h"]), float(prop["d"])),
                x_rot=float(prop.get("x_rot", 0)),
                y_rot=float(prop.get("y_rot", 0)),
                z_rot=float(prop.get("z_rot", 0)),
            )
            for prop in document.get("props", [])
        ],
        places={int(entry["id"]): entry.get("place", "") for entry in entries},
    )
