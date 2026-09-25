"""Whether any patched fixture drives a role - the question before a wheel generator."""

from collections.abc import Iterable

from ..capability import FixtureCapabilities


def rig_has_role(capabilities: Iterable[FixtureCapabilities], role: str) -> bool:
    """True when at least one fixture has a channel for `role`."""
    return any(capability.has_role(role) for capability in capabilities)
