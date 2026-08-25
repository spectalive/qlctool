"""Write the `<Monitor>` node: where QLC+ draws every fixture in 2D and 3D.

Shared by the two things that can decide a rig's positions - the generated
band layout and a written stage plot - because the node itself is the same
either way. Child order follows `MonitorProperties::saveXML`: Font,
ChannelStyle, ValueStyle, Grid, StageItem, then one FxItem per fixture.

Two details QLC+ does not forgive:

- **The grid is in metres and the positions in millimetres**, and a position is
  the fixture's near corner, not its centre - QLC+ adds half the mesh extents
  when it draws, so `y=0` is standing on the floor.
- **The point of view is written even though it is optional.** With none
  stored, the 2D view asks for one on first open and then converts every
  position it has into it, silently rewriting a layout that was already right.
"""

from dataclasses import dataclass

from lxml import etree

from .constants import QLC_NS
from .workspace import Workspace
from .xmlutil import find_local

# MonitorProperties::PointOfView in the QLC+ source, by name.
POINTS_OF_VIEW = {"top": 1, "front": 2, "right": 3, "left": 4}

_DEFAULTS = {
    "Font": "Arial,12,-1,5,50,0,0,0,0,0",
    "ChannelStyle": "1",
    "ValueStyle": "1",
}


@dataclass(frozen=True)
class MonitorItem:
    """One fixture's spot on the plot, in millimetres.

    `hidden` is QLC+'s own flag for a fixture that is patched but not drawn -
    a spare that stays in the workspace without cluttering the views.
    """

    fixture_id: int
    x: float
    y: float
    z: float
    hidden: bool = False


def write_monitor(
    workspace: Workspace,
    stage: tuple[int, int, int],
    point_of_view: str,
    items: list[MonitorItem],
) -> None:
    """Replace the Monitor node, keeping the DMX-monitor display settings."""
    if point_of_view not in POINTS_OF_VIEW:
        raise ValueError(
            f"unknown point of view {point_of_view!r} "
            f"(known: {', '.join(sorted(POINTS_OF_VIEW))})"
        )

    engine = workspace.engine
    existing = find_local(engine, "Monitor")
    kept = {
        name: find_local(existing, name) for name in _DEFAULTS
    } if existing is not None else {}

    monitor = etree.Element(f"{{{QLC_NS}}}Monitor")
    monitor.set(
        "DisplayMode",
        existing.get("DisplayMode", "0") if existing is not None else "0",
    )
    monitor.set(
        "ShowLabels",
        existing.get("ShowLabels", "1") if existing is not None else "1",
    )

    for name, fallback in _DEFAULTS.items():
        element = etree.SubElement(monitor, f"{{{QLC_NS}}}{name}")
        source = kept.get(name)
        element.text = source.text if source is not None else fallback

    width, height, depth = stage
    grid = etree.SubElement(monitor, f"{{{QLC_NS}}}Grid")
    grid.set("Width", str(width))
    grid.set("Height", str(height))
    grid.set("Depth", str(depth))
    grid.set("Units", "0")  # metres
    grid.set("POV", str(POINTS_OF_VIEW[point_of_view]))

    etree.SubElement(monitor, f"{{{QLC_NS}}}StageItem").text = "0"

    for item in sorted(items, key=lambda i: i.fixture_id):
        element = etree.SubElement(monitor, f"{{{QLC_NS}}}FxItem")
        element.set("ID", str(item.fixture_id))
        element.set("XPos", str(round(item.x)))
        element.set("YPos", str(round(item.y)))
        element.set("ZPos", str(round(item.z)))
        if item.hidden:
            # Presence is what QLC+ checks; the value is cosmetic.
            element.set("Hidden", "True")

    if existing is not None:
        engine.replace(existing, monitor)
    else:
        engine.append(monitor)
