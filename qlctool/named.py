"""The first capability in a channel's ranges whose name starts with a wanted word."""

from .capability import Capability


def named(ranges: tuple[Capability, ...], wanted: tuple[str, ...]) -> Capability | None:
    for capability in ranges:
        name = capability.name.strip().lower()
        if any(name.startswith(word) for word in wanted):
            return capability
    return None
