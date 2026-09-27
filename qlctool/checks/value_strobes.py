"""Whether a channel value strobes it, given the channel's strobing range."""

from ..definition import Capability


def value_strobes(strobing: Capability | None, value: int) -> bool:
    if strobing is None:
        return value > 0
    return strobing.minimum <= value <= strobing.maximum
