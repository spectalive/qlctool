"""The fixtures this EFX drives on pan and tilt, by name."""

from lxml import etree

from ..find_local import find_local
from ..findall_local import findall_local
from .efx_driven import EFX_PAN_TILT
from .show_graph import ShowGraph


def efx_pan_tilt_fixture_names(graph: ShowGraph, function: etree._Element) -> set[str]:
    heads: set[str] = set()
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or not (identifier_text := (identifier.text or "").strip()).isdigit():
            continue
        mode = find_local(element, "Mode")
        mode_value = int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
        if mode_value != EFX_PAN_TILT:
            continue
        capability = graph.capabilities.get(int(identifier_text))
        if capability is None:
            continue
        heads.add(capability.fixture.name)
    return heads
