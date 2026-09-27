"""The fixtures an EFX moves, grouped by the window their family lives in.

Told apart the way `rule_movement_families` tells them: a mover with a gobo
wheel is a beam, one without is a wash. They are different windows because
a raw pan or tilt value means nothing across models.
"""

from lxml import etree

from .. import roles
from ..audience_window import BEAM_WINDOW, WASH_WINDOW, Window
from ..xmlutil import find_local, findall_local
from .efx_driven import EFX_PAN_TILT
from .show_graph import ShowGraph


def heads_by_family(graph: ShowGraph, function: etree._Element) -> dict[Window, set[str]]:
    moved: dict[Window, set[str]] = {}
    for element in findall_local(function, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or not (identifier_text := (identifier.text or "").strip()).isdigit():
            continue
        mode = find_local(element, "Mode")
        mode_value = int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT
        if mode_value != EFX_PAN_TILT:
            continue
        capability = graph.capabilities.get(int(identifier_text))
        if capability is None or capability.is_smoke:
            continue
        window = BEAM_WINDOW if capability.has_role(roles.GOBO) else WASH_WINDOW
        moved.setdefault(window, set()).add(capability.fixture.name)
    return moved
