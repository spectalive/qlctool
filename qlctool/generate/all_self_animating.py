"""Whether every member of a set of fixtures runs programmes of its own."""

from collections.abc import Iterable

from ..capability import FixtureCapabilities
from ..internal_program import internal_program


def all_self_animating(caps: Iterable[FixtureCapabilities], fixture_ids: Iterable[int]) -> bool:
    """True when every colour-capable member runs programmes of its own."""
    wanted = set(fixture_ids)
    members = [c for c in caps if c.fixture.fixture_id in wanted]
    return bool(members) and all(internal_program(capability) is not None for capability in members)
