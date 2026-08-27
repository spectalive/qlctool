"""Which of a fixture's channels can strobe, and whether a written value does.

Shared by the strobe rules the way `strobe_shape` is shared by the rate rules:
one answer to "is this channel a strobe" and one to "does this value strobe
it", both read off the definition's capabilities - never off a name.

Two kinds of channel qualify. One carries a labelled strobing range (found by
`strobe_range`); a value strobes it only inside that range, because the
neighbours are "Open", "Closed" and "No function". The other has the role
`strobe` and no labelled ranges at all - the Vortex PC-64's channel 5, the
HYULIGHTS panels' channel 5 - a bare speed channel where anything above zero
strobes.
"""

from .. import roles
from ..capability import FixtureCapabilities
from ..definition import Capability
from ..strobe_range import strobe_range


def strobe_capable_offsets(
    capabilities: FixtureCapabilities,
) -> dict[int, Capability | None]:
    """offset -> its strobing range, or None for a bare speed channel."""
    found: dict[int, Capability | None] = {}
    for offset, ranges in capabilities.capabilities_for_role(roles.STROBE):
        if not ranges:
            found[offset] = None
            continue
        strobing = strobe_range(ranges)
        if strobing is not None:
            found[offset] = strobing
    return found


def value_strobes(strobing: Capability | None, value: int) -> bool:
    if strobing is None:
        return value > 0
    return strobing.minimum <= value <= strobing.maximum
