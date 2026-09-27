"""Which fixtures a function colours while leaving their intensity path dark."""

from .driven_channels import Driven
from .fixture_is_coloured import fixture_is_coloured
from .reason_it_stays_dark import reason_it_stays_dark
from .show_graph import ShowGraph
from .touches_intensity_path import touches_intensity_path


def intensity_dark_fixtures(graph: ShowGraph, driven: Driven, layer: bool = False) -> set[str]:
    # A layer that states colour and nothing else rides on the state beneath
    # it, which owns the intensity (2026-08-27: colour and intensity are
    # separate owners now, so the rig-wide wheel opens nobody's dimmer). But a
    # layer that opens intensity for *some* of what it colours answers for all
    # of it - a bank that lights twenty fixtures and forgets the panels'
    # dimmer is the original panels-dark bug, and a dimmer opened behind a
    # shutter left shut is still the beams' gobo-scene bug.
    if layer and not any(
        touches_intensity_path(capability, written)
        for fixture_id, written in driven.items()
        if (capability := graph.capabilities.get(fixture_id)) is not None
        and not capability.is_smoke
    ):
        return set()
    dark: set[str] = set()
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        if not fixture_is_coloured(capability, written):
            continue
        if reason_it_stays_dark(capability, written):
            dark.add(capability.fixture.name)
    return dark
