"""One DMX channel a fixture definition exposes, with its capabilities."""

from dataclasses import dataclass

from .capability import Capability


@dataclass(frozen=True)
class Channel:
    name: str
    role: str | None
    capabilities: tuple[Capability, ...] = ()
    # The QLC+ channel group, verbatim. It is not decoration: QLC+ resets the
    # channels in the Intensity group every cycle and leaves every other group
    # holding its last value (`Universe::processFaders`), which is the whole
    # difference between a Flash that releases and one that latches.
    group: str = ""
