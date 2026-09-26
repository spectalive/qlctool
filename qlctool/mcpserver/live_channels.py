"""The `live_channels` tool: the DMX values a running QLC+ is sending."""

from typing import Any

from .channel_records import channel_records
from .in_range import in_range
from .mcp_settings import McpSettings
from .qlc_link import QlcLink

UNIVERSE_SIZE = 512


def live_channels(
    settings: McpSettings, universe: int = 1, start: int = 1, count: int = 16
) -> list[dict[str, Any]]:
    """`count` channels of `universe` from address `start`, all 1-based as the console numbers them."""
    in_range("universe", universe, 1, 64)
    in_range("start", start, 1, UNIVERSE_SIZE)
    in_range("count", count, 1, UNIVERSE_SIZE - start + 1)
    with QlcLink(settings) as link:
        return channel_records(link.ask("getChannelsValues", universe, start, count))
