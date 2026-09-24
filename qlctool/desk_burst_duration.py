"""How long a desk burst runs, from its source accent's identifier."""

from .desk_burst_identifier import desk_burst_identifier
from .desk_policy import BURST_MS
from .desk_widgets import DeskWidget
from .names.names import Names


def desk_burst_duration(source: DeskWidget, names: Names) -> int | None:
    """Milliseconds for this accent's burst, or None when the desk has no duration for it."""
    identifier = desk_burst_identifier(source.caption, names)
    return None if identifier is None else BURST_MS.get(identifier)
