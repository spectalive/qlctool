"""Result of generating the held palette-colour flashes."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedColorFlashes:
    """The generated hit Scene ID for each palette colour."""

    ids: dict[str, int] = field(default_factory=dict)
