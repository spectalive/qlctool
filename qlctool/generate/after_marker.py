"""What follows a marker in a function name: the caption a library button shows.

Moved verbatim out of `live_console` (2026-09-27 split), where it was `_after`.
"""


def after_marker(name: str, marker: str) -> str:
    _, separator, tail = name.partition(marker)
    return tail if separator else name
