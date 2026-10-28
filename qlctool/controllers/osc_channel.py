"""The input channel QLC+'s OSC plugin files an address under.

QLC+ does not keep OSC addresses in a workspace: the plugin hashes each path it
receives with `Utils::getChecksum` (plugins/interfaces/utils.h, a 16-entry
table CRC-16) and reports that number as the channel
(plugins/osc/osccontroller.cpp, `OSCController::getHash`). A widget bound to
`/desk/33` therefore carries `Channel="32623"`, and only this function can say
which address that was. Vectors checked against dmxdesk's own port,
`core/qlc_osc_channel.c`, on 2026-10-28.
"""

TABLE = (
    0x0000, 0x1081, 0x2102, 0x3183,
    0x4204, 0x5285, 0x6306, 0x7387,
    0x8408, 0x9489, 0xA50A, 0xB58B,
    0xC60C, 0xD68D, 0xE70E, 0xF78F,
)  # fmt: skip


def osc_channel(path: str) -> int:
    """The channel QLC+ reports for an OSC message sent to `path`."""
    crc = 0xFFFF
    for byte in path.encode("utf-8"):
        crc = ((crc >> 4) & 0x0FFF) ^ TABLE[(crc ^ byte) & 15]
        crc = ((crc >> 4) & 0x0FFF) ^ TABLE[(crc ^ (byte >> 4)) & 15]
    return ~crc & 0xFFFF
