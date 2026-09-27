"""What precedes a marker in a function name: the group a matrix page is labelled with.

Moved verbatim out of `live_console` (2026-09-27 split), where it was `_before`.
"""


def before_marker(name: str, marker: str) -> str:
    head, separator, _ = name.partition(marker)
    return head if separator else name
