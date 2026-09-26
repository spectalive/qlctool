"""2026-09-26 (ruling D-R6): the live tools against a real QLC+ 5, running Vibra offline.

A QLC+ of the test's own (`live_qlcplus.py`) on a free port, never the
operator's: it reads the console and the channels, is refused a press without
`--allow-live-writes`, and with it presses AUTO on and off and starts and
stops its function. Skipped where no QLC+ 5 is installed (CI).
"""

import pytest
from live_qlcplus import qml_binary, running_qlcplus
from rig_root import RIG_ROOT

pytest.importorskip("websockets")

from qlctool.mcpserver.live_channels import live_channels
from qlctool.mcpserver.live_function import live_function
from qlctool.mcpserver.live_functions import live_functions
from qlctool.mcpserver.live_press import live_press
from qlctool.mcpserver.live_status import live_status
from qlctool.mcpserver.live_widgets import live_widgets
from qlctool.mcpserver.mcp_settings import McpSettings
from qlctool.mcpserver.pressable_widget_types import PRESSABLE_WIDGET_TYPES

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"


@pytest.mark.skipif(qml_binary() is None, reason="no QLC+ 5 on this machine")
def test_the_live_tools_read_and_drive_a_real_qlcplus(tmp_path):
    with running_qlcplus(VIBRA, tmp_path) as port:
        reads = McpSettings(port=port, timeout=5.0)
        writes = McpSettings(port=port, timeout=5.0, allow_writes=True)

        status = live_status(reads, str(VIBRA))
        assert status["reachable"] and status["widgets"] > 500
        assert status["workspace"]["matches"], status

        widgets = {w["id"]: w for w in live_widgets(reads)}
        auto = widgets[4]
        assert "AUTO" in auto["caption"] and auto["state"] == "0"
        assert auto["function"] is not None
        assert len(live_functions(reads)) == status["functions"]

        channels = live_channels(reads, universe=1, start=1, count=8)
        assert [c["address"] for c in channels] == list(range(1, 9))
        assert all(0 <= c["value"] <= 255 for c in channels)

        with pytest.raises(PermissionError, match="--allow-live-writes"):
            live_press(reads, 4)
        assert (
            live_widgets(reads, detail=True)[0]["state"]
            == widgets[live_widgets(reads, detail=False)[0]["id"]]["state"]
        )

        other = next(w for w in widgets.values() if w["type"] not in PRESSABLE_WIDGET_TYPES)
        with pytest.raises(ValueError, match="buttons and sliders"):
            live_press(writes, other["id"])
        with pytest.raises(ValueError, match="no widget"):
            live_press(writes, 999999)

        pressed = live_press(writes, 4, 255)
        assert (pressed["before"], pressed["state"]) == ("0", "255")
        # A toggle flips on every message, the value notwithstanding.
        assert live_press(writes, 4, 0)["state"] == "0"

        fid = auto["function"]
        assert live_function(writes, fid, "on")["running"] is True
        assert live_function(writes, fid, "off")["running"] is False
