"""Write the `<Monitor>` node: where QLC+ draws every fixture in 2D and 3D."""

from lxml import etree

from .constants import QLC_NS
from .find_local import find_local
from .monitor_item import MonitorItem
from .prop_item import POINTS_OF_VIEW, PRIMITIVE_SIZE, PropItem
from .workspace import Workspace

_DEFAULTS = {
    "Font": "Arial,12,-1,5,50,0,0,0,0,0",
    "ChannelStyle": "1",
    "ValueStyle": "1",
}


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
            strict=True,
        ):
            element.set(attribute, str(round(value)))
        for attribute, wanted in zip(("XScale", "YScale", "ZScale"), prop.size, strict=True):
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
