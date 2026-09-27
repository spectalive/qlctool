"""The wheel-coloured fixtures a scene parks on a rotation range."""

from .. import roles
from .driven_channels import Driven
from .is_rotation import is_rotation
from .show_graph import ShowGraph


def spinning_wheels(graph: ShowGraph, stated: Driven) -> set[str]:
    spinning: set[str] = set()
    for fixture_id, written in stated.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke or not written:
            continue
        if any(capability.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE)):
            continue
        wheel = capability.wheel_for_role(roles.COLOR_MACRO)
        if wheel is None:
            continue
        offset, positions = wheel
        value = written.get(offset)
        if value is None:
            continue
        if is_rotation(positions, value):
            spinning.add(capability.fixture.name)
    return spinning
