"""Whether any channel of a definition carries a role."""

from ..definition import FixtureDefinition


def has_role(definition: FixtureDefinition, role: str) -> bool:
    return any(channel.role == role for channel in definition.channels.values())
