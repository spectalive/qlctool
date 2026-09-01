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
class PropItem:
    """A piece of scenery in the 3D view - QLC+ calls it a MeshItem.

    Given in world terms: the centre of the box, in millimetres above the floor,
    and how big it is. QLC+ stores something less friendly - it positions a
    generic mesh by a corner *and* adds half the raw mesh's extents, which for
    its own primitives is a fixed metre whatever the scale, so the stored
    position is the wanted centre minus 1000 on every axis. That conversion
    lives in `write_monitor` rather than in whoever writes a plot.
    """

    item_id: int
    resource: str
    name: str
    centre: tuple[float, float, float]
    size: tuple[float, float, float]
    x_rot: float = 0.0
    y_rot: float = 0.0
    z_rot: float = 0.0


# QLC+'s bundled primitives all span -1..1, so two metres across before scaling.
PRIMITIVE_SIZE = 2000.0


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
    # Degrees about each axis. A fixture standing on the floor and aimed at the
    # ceiling is x_rot=180: QLC+'s meshes all point down by default, because
    # that is how a light hangs.
    x_rot: float = 0.0
    y_rot: float = 0.0
    z_rot: float = 0.0


def write_monitor(
    workspace: Workspace,
    stage: tuple[int, int, int],
    point_of_view: str,
    items: list[MonitorItem],
    props: list[PropItem] | None = None,
) -> None:
    """Replace the Monitor node, keeping the DMX-monitor display settings."""
    if point_of_view not in POINTS_OF_VIEW:
        raise ValueError(
            f"unknown point of view {point_of_view!r} (known: {', '.join(sorted(POINTS_OF_VIEW))})"
        )

    engine = workspace.engine
    existing = find_local(engine, "Monitor")
    kept = {name: find_local(existing, name) for name in _DEFAULTS} if existing is not None else {}

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
        for attribute, degrees in (
            ("XRot", item.x_rot),
            ("YRot", item.y_rot),
            ("ZRot", item.z_rot),
        ):
            if degrees:
                element.set(attribute, str(round(degrees)))
        if item.hidden:
            # Presence is what QLC+ checks; the value is cosmetic.
            element.set("Hidden", "True")

    for prop in sorted(props or [], key=lambda p: p.item_id):
        element = etree.SubElement(monitor, f"{{{QLC_NS}}}MeshItem")
        element.set("ID", str(prop.item_id))
        element.set("Res", prop.resource)
        element.set("Name", prop.name)
        for attribute, value in zip(
            ("XPos", "YPos", "ZPos"),
            (c - PRIMITIVE_SIZE / 2 for c in prop.centre),
        ):
            element.set(attribute, str(round(value)))
        for attribute, wanted in zip(("XScale", "YScale", "ZScale"), prop.size):
            element.set(attribute, f"{wanted / PRIMITIVE_SIZE:g}")
        for attribute, degrees in (
            ("XRot", prop.x_rot),
            ("YRot", prop.y_rot),
            ("ZRot", prop.z_rot),
        ):
            if degrees:
                element.set(attribute, str(round(degrees)))

    if existing is not None:
        engine.replace(existing, monitor)
    else:
        engine.append(monitor)
