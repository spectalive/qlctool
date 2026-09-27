"""Where along the range a capability preset names, this look sits, or None."""

from ..fixture_capabilities import FixtureCapabilities


def preset_value(
    capability: FixtureCapabilities, role: str, preset: str, fraction: float
) -> int | None:
    for _, ranges in capability.capabilities_for_role(role):
        for item in ranges:
            if (item.preset or "") == preset:
                span = item.maximum - item.minimum
                return item.minimum + round(span * fraction)
    return None
