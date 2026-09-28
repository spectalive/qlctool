"""The prism wheel's inserted position, by preset or by its name."""

from ..capability import Capability


def inserted_prism(positions: tuple[Capability, ...]) -> Capability:
    for position in positions:
        preset = position.preset.lower()
        name = position.name.lower()
        if ("prism" in preset and preset.endswith("on")) or "insert" in name:
            return position
    raise ValueError("a prism wheel has no labelled inserted position")
