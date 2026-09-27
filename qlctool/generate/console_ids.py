"""Widget ids for the live console, handed out in order from where the workspace left off.

Moved verbatim out of `live_console` (2026-09-27 split), where it was `_Ids`.
"""

from lxml import etree

from ..vc.widget_ids import next_widget_id


class ConsoleIds:
    """Widget IDs, handed out in order from wherever the console left off."""

    def __init__(self, root: etree._Element) -> None:
        self._next = next_widget_id(root)

    def take(self) -> int:
        value = self._next
        self._next += 1
        return value
