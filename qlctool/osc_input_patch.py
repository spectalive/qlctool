"""The OSC input patch a workspace already carries, if any."""

from lxml import etree

from .find_local import find_local
from .iter_local import iter_local
from .osc_plugin import OSC_PLUGIN


def osc_input_patch(root: etree._Element) -> etree._Element | None:
    """The first universe's `<Input>` on QLC+'s OSC plugin, or None."""
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return None
    for universe in iter_local(io_map, "Universe"):
        patch = find_local(universe, "Input")
        if patch is not None and patch.get("Plugin") == OSC_PLUGIN:
            return patch
    return None
