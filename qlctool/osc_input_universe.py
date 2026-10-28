"""The universe an OSC surface's bindings arrive on."""

from lxml import etree

from .osc_input_patch import osc_input_patch


def osc_input_universe(root: etree._Element) -> int | None:
    """The id of the universe carrying the OSC input patch, or None without one."""
    patch = osc_input_patch(root)
    universe = patch.getparent() if patch is not None else None
    if universe is None:
        return None
    return int(universe.get("ID", "0"))
