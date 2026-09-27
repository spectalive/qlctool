"""The prism wheel's parked (out) position, by preset, by name, or its first."""

from ..definition import Capability


def parked_prism(positions: tuple[Capability, ...]) -> Capability:
    for position in positions:
        preset = position.preset.lower()
        if ("prism" in preset and preset.endswith("off")) or position.name.lower() == "none":
            return position
    if positions:
        return positions[0]
    raise ValueError("a prism wheel has no positions")
