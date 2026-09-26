"""The `live_press` tool: press or release a button, or set a slider, of the running console."""

import time
from typing import Any

from .in_range import in_range
from .mcp_message import mcp_message
from .mcp_settings import McpSettings
from .pressable_widget_types import PRESSABLE_WIDGET_TYPES
from .qlc_link import QlcLink
from .refuse_live_writes import refuse_live_writes
from .settle_seconds import SETTLE_SECONDS
from .unknown_widget_types import UNKNOWN_WIDGET_TYPES


def live_press(settings: McpSettings, widget_id: int, value: int = 255) -> dict[str, Any]:
    """Send `<widget_id>|<value>` as the web console does, and read the widget's state back.

    The widget is asked its type first: an id the console lacks is refused,
    and so is any widget but a button or a slider. A flash button takes 255
    as a press and 0 as a release, and stays lit until released. A toggle
    button flips on every message, 255 or 0 alike, and a blackout button
    toggles the blackout the same way (`VCButton::requestStateChange`, QLC+
    5), so read `before` and send once. A slider takes the value as its level.
    Refused unless the server was started with `--allow-live-writes`.
    """
    refuse_live_writes(settings, "live_press")
    in_range("value", value, 0, 255)
    with QlcLink(settings) as link:
        kind = link.ask("getWidgetType", widget_id)[-1]
        if kind in UNKNOWN_WIDGET_TYPES:
            raise ValueError(mcp_message("mcp_live_no_widget", widget=widget_id))
        if kind not in PRESSABLE_WIDGET_TYPES:
            raise ValueError(mcp_message("mcp_live_not_pressable", widget=widget_id, kind=kind))
        before = link.ask("getWidgetStatus", widget_id)
        link.send(f"{widget_id}|{value}")
        time.sleep(SETTLE_SECONDS)
        after = link.ask("getWidgetStatus", widget_id)
    return {
        "widget": widget_id,
        "type": kind,
        "sent": value,
        "before": "|".join(before[1:]),
        "state": "|".join(after[1:]),
    }
