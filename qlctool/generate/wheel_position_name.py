"""The name a wheel position's scene is shown under."""

from ..capability import Capability
from ..names.names import Names
from ..names.preset_identifier import preset_identifier


def wheel_position_name(position: Capability, label: str, index: int, vocabulary: Names) -> str:
    """The show's word for the position's QLC+ preset, else the definition's name for it.

    A preset says what a range is in every language ("PrismEffectOn"); the
    definition's name for it is English ("Insert Prism") and reached a Spanish
    desk as such (owner, 2026-11-01).
    """
    identifier = preset_identifier(position.preset)
    if identifier and identifier in vocabulary.identifiers("presets"):
        return vocabulary.display(identifier)
    return position.name or f"{label} {index}"
