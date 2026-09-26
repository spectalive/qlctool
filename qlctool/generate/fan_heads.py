"""The heads a static fan or cross spreads, in the order the caller gives.

The order is the caller's - `stage_ordered`, left to right across the stage -
because a fan only reads as one when its pans rise head by head across the
room. Taken from the patch, the Vibra 7R fanned 62, 89, 102, 75 across the
stage and the house-right head folded back into the middle (`fan_order`,
Round 2 review of the en-sala DMX audit, 2026-09-27). A spare in a flight
case takes no slot: every slot it held was a gap in the fan nobody sees.
"""

from collections.abc import Sequence

from .. import roles
from ..capabilities_of import capabilities_of
from ..capability import FixtureCapabilities
from ..library import FixtureLibrary
from ..rigged_fixture_ids import rigged_fixture_ids
from ..workspace import Workspace


def fan_heads(
    workspace: Workspace, library: FixtureLibrary, fixture_ids: Sequence[int]
) -> list[FixtureCapabilities]:
    """The rigged pan-and-tilt heads of `fixture_ids`, in `fixture_ids`' order."""
    rigged = rigged_fixture_ids(workspace.root)
    movers = {
        caps.fixture.fixture_id: caps
        for caps in capabilities_of(workspace.root, library)
        if caps.has_role(roles.PAN) and caps.has_role(roles.TILT)
    }
    return [movers[i] for i in fixture_ids if i in movers and i in rigged]
