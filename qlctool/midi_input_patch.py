"""The universe-0 MIDI input patch a workspace already carries, if any."""

from lxml import etree

from .find_local import find_local
from .iter_local import iter_local


def midi_input_patch(root: etree._Element) -> etree._Element | None:
    """The universe-0 MIDI input patch, or None if the show has no listener."""
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return None
    for universe in iter_local(io_map, "Universe"):
        patch = find_local(universe, "Input")
        if patch is not None:
            return patch
    return None
