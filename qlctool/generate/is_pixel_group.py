"""Whether a fixture group is made of pixels a matrix can draw across."""

from collections.abc import Iterable

from .. import roles
from ..capability import FixtureCapabilities


def is_pixel_group(caps: Iterable[FixtureCapabilities], fixture_ids: Iterable[int]) -> bool:
    """True when a member really has pixels: more than one red channel.

    An 8-segment bar has eight of them and a matrix can draw across it; a PAR
    or a wash head has one, and every algorithm on it collapses to a colour.
    """
    wanted = set(fixture_ids)
    return any(
        len(c.offsets_for_role(roles.RED)) > 1 for c in caps if c.fixture.fixture_id in wanted
    )
