"""The channels QLC+ answers `getChannelsValues` with: four fields each."""

from typing import Any


def channel_records(fields: list[str]) -> list[dict[str, Any]]:
    """Address, value, channel group and override flag of each channel.

    The group is QLC+'s channel group number, `0.#RRGGBB` for an intensity
    channel with its colour, or empty where no fixture is patched
    (`WebAccessSimpleDesk::getChannelsMessage`).
    """
    return [
        {
            "address": int(fields[index]),
            "value": int(fields[index + 1]),
            "group": fields[index + 2],
            "overridden": fields[index + 3] == "1",
        }
        for index in range(0, len(fields) - 3, 4)
    ]
