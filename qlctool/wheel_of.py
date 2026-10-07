"""A fixture's wheel for a role it is already known to carry."""

from typing import cast

from .capability import Capability
from .fixture_capabilities import FixtureCapabilities


def wheel_of(capability: FixtureCapabilities, role: str) -> tuple[int, tuple[Capability, ...]]:
    """Return ``wheel_for_role(role)`` for a fixture the caller filtered on that role.

    Every caller selects its fixtures by the role first, so the ``None`` that
    ``wheel_for_role`` returns for a fixture without the role cannot reach here;
    this only states that to the type checker and adds no check of its own.
    """
    return cast("tuple[int, tuple[Capability, ...]]", capability.wheel_for_role(role))
