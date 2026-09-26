"""The fixtures whose colour is only a wheel, and which are not beams."""

from collections.abc import Sequence

from .. import roles
from ..capability import FixtureCapabilities


def wheel_only_fixture_ids(caps: Sequence[FixtureCapabilities]) -> list[int]:
    """Fixtures with a colour wheel, no red channel, no gobo, and no smoke.

    A beam (a wheel beside a gobo) takes its white from the beams' own wheel
    scenes; an RGB fixture from `color_scene_values`. These have neither.
    """
    return [
        c.fixture.fixture_id
        for c in caps
        if c.has_role(roles.COLOR_MACRO)
        and not c.has_role(roles.RED)
        and not c.has_role(roles.GOBO)
        and not c.is_smoke
    ]
