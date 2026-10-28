"""Whether a value can root a show's OSC addresses."""

from typing import Any

# OSC reserves these in an address pattern (OSC 1.0, "OSC Address Patterns"),
# and a prefix carrying one could never be matched literally.
RESERVED = set(" #*,?[]{}")


def valid_osc_prefix(value: Any) -> bool:
    """A string such as `/desk`: a leading '/', no trailing one, no reserved characters."""
    return (
        isinstance(value, str)
        and len(value) > 1
        and value.startswith("/")
        and not value.endswith("/")
        and "//" not in value
        and not RESERVED & set(value)
    )
