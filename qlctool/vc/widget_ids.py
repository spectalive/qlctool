"""Allocate unique Virtual Console widget IDs.

Every VC widget carries an ID unique within the console. An unassigned button
reference stores QLC+'s invalid-ID sentinel 4294967295, so it is excluded here -
counting it would push the next ID out of the range QLC+ stores, the same trap
the Function allocator hit.
"""

from lxml import etree

from ..constants import ALL_FIXTURES_GROUP
from ..xmlutil import find_local

WIDGET_TAGS = {
    "Frame", "SoloFrame", "Button", "Label", "Slider", "XYPad", "SpeedDial",
    "Matrix", "AudioTriggers", "Clock", "Cue",
}


def existing_widget_ids(root: etree._Element) -> set[int]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return set()
    ids = set()
    for element in console.iter():
        tag = element.tag
        if not isinstance(tag, str):
            continue
        if tag.rsplit("}", 1)[-1] not in WIDGET_TAGS:
            continue
        raw = element.attrib.get("ID")
        if raw is None:
            continue
        value = int(raw)
        if value < ALL_FIXTURES_GROUP:
            ids.add(value)
    return ids


def next_widget_id(root: etree._Element) -> int:
    ids = existing_widget_ids(root)
    return max(ids) + 1 if ids else 0
