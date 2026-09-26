"""A workspace with no way out of the machine: its universes kept, their I/O patches gone.

QLC+ opens every `<Input>`, `<Output>` and `<Feedback>` a universe names the
moment it loads the file - the DMX interface, Art-Net, the MIDI pad and its
LED bridge - and QLC+ 5 has no flag to load a workspace without them
(`qmlui/main.cpp`). A copy without those three elements loads everything
else the same way and touches no hardware. Used by validation and by the
suite's live QLC+ (2026-09-26, review of round D6).
"""

from pathlib import Path

from lxml import etree

from .xmlutil import iter_local, localname

IO_PATCHES = ("Input", "Output", "Feedback")


def offline_workspace(source: Path, target: Path) -> Path:
    """Write `source` to `target` without any universe's I/O patches; return `target`."""
    tree = etree.parse(str(source))
    for universe in list(iter_local(tree.getroot(), "Universe")):
        parent = universe.getparent()
        if parent is None or localname(parent) != "InputOutputMap":
            continue
        for element in [child for child in universe if localname(child) in IO_PATCHES]:
            universe.remove(element)
    tree.write(str(target), xml_declaration=True, encoding="UTF-8")
    return target
