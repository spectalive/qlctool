"""A Flash scene's fixtures that strobe, and the ones its wiring leaves dark."""

from lxml import etree

from .raises_light import raises_light
from .show_graph import ShowGraph
from .states_rig_colour import states_rig_colour
from .strobe_capable_offsets import strobe_capable_offsets
from .value_strobes import value_strobes


def flash_strobe_writes(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], scene: etree._Element
) -> tuple[list[str], bool]:
    """(fixtures written but not strobed, whether anything strobes at all)."""
    dark: list[str] = []
    strobing_anywhere = False
    driven = graph.driven_of(scene, groups)
    colours_rig = states_rig_colour(graph, driven)
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or (capability.is_smoke and not capability.is_lit_smoke):
            continue
        if capability.is_lit_smoke and not colours_rig:
            continue
        capable = strobe_capable_offsets(capability)
        if not capable:
            continue
        # Only a flash that *raises light* on the fixture is a hit that owes
        # the strobe. A held colour bank, a gobo pick or the stage aim
        # (Flash buttons since 2026-09-02) state a wheel, a position or an
        # RGB triple and leave every dimmer and shutter to the state beneath:
        # they are accents, and an accent that strobed would be the bug.
        if not raises_light(capability, written):
            continue
        strobed = any(
            (value := written.get(offset)) is not None and value_strobes(strobing, value)
            for offset, strobing in capable.items()
        )
        if strobed:
            strobing_anywhere = True
        else:
            dark.append(capability.fixture.name or str(fixture_id))
    return dark, strobing_anywhere
