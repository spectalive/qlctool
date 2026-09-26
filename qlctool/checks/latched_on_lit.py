"""The channels a released pick leaves holding its value on a lit, rigged fixture.

An LTP channel keeps the last value written until somebody writes another one
(`Universe::write`; only HTP channels are zeroed every tick). When a pick
of a family frame is released and nothing the state still runs writes a
channel the pick wrote, that channel keeps the pick's value for the rest of the
night: the 7R wheel stayed red over a black rig, Gobo Shake kept shaking
under FIESTA (en-sala DMX audit, 2026-09-26, item 5 and concern C3). It only
shows on a fixture that is still lit, so a dark one is left alone.
"""

from collections.abc import Collection, Mapping

from .driven_channels import Driven
from .family_offsets import family_offsets
from .lit_in import lit_in
from .merged_htp import merged_htp
from .show_graph import ShowGraph, reach


def latched_on_lit(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    pick_id: int,
    families: Collection[str],
    rigged: Collection[int],
    released: Mapping[int, Mapping[int, int | None]],
) -> Driven:
    """Fixture id -> the pick's family channels no running function rewrites."""
    latched: Driven = {}
    for fixture_id, written in reach(graph, groups, pick_id).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or fixture_id not in rigged:
            continue
        still = released.get(fixture_id, {})
        htp = merged_htp(graph, fixture_id)
        family = family_offsets(capability, families)
        left = {
            offset: value
            for offset, value in written.items()
            if offset in family and offset not in htp and offset not in still
        }
        if left and lit_in(capability, still, htp):
            latched[fixture_id] = left
    return latched
