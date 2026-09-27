"""The widget ids the live console put up, by kind, for the checks and the desk.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedConsole:
    frame_ids: list[int] = field(default_factory=list)
    button_ids: list[int] = field(default_factory=list)
    widget_ids: list[int] = field(default_factory=list)
