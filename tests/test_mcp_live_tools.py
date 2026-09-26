"""2026-09-26 (ruling D-R6): the live tools read a running QLC+ and write only when allowed.

Against `FakeQlcPlus`, which speaks the web API as `webaccess-qml.cpp` does and
pushes console changes in between, so this runs where no QLC+ is installed.
`test_mcp_live_qlcplus.py` holds the same tools to a real QLC+.
"""

import socket

import pytest

pytest.importorskip("websockets")

from fake_qlcplus import FakeQlcPlus

from qlctool.mcpserver.channel_records import channel_records
from qlctool.mcpserver.live_channels import live_channels
from qlctool.mcpserver.live_function import live_function
from qlctool.mcpserver.live_functions import live_functions
from qlctool.mcpserver.live_press import live_press
from qlctool.mcpserver.live_status import live_status
from qlctool.mcpserver.live_widgets import live_widgets
from qlctool.mcpserver.mcp_settings import McpSettings
from qlctool.mcpserver.qlc_link import QlcLink


@pytest.fixture
def qlc():
    with FakeQlcPlus() as fake:
        yield fake


def _settings(qlc, writes=False):
    return McpSettings(port=qlc.port, allow_writes=writes, timeout=1.0)


def test_status_reports_the_running_show(qlc):
    status = live_status(_settings(qlc))
    assert status["reachable"] and status["project_loaded"]
    assert (status["functions"], status["widgets"]) == (2, 3)
    assert status["writes_allowed"] is False


def test_status_says_when_nothing_answers():
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    status = live_status(McpSettings(port=port, timeout=0.5))
    assert status["reachable"] is False
    assert "no QLC+ web API" in status["error"]


def test_status_tells_whether_a_workspace_is_the_running_show(qlc, tmp_path):
    workspace = tmp_path / "show.qxw"
    workspace.write_text(
        '<Workspace xmlns="http://www.qlcplus.org/Workspace"><Engine>'
        '<Function ID="21" Name="Auto chase"/><Function ID="22" Name="Azul"/>'
        '<Function ID="30" Name="Extra"/></Engine></Workspace>'
    )
    compared = live_status(_settings(qlc), str(workspace))["workspace"]
    assert compared["matches"] is False
    assert (compared["only_in_file"], compared["only_running"], compared["renamed"]) == (1, 0, 1)


def test_widgets_carry_type_state_and_function(qlc):
    widgets = {w["id"]: w for w in live_widgets(_settings(qlc))}
    assert widgets[3] == {
        "id": 3,
        "caption": "AUTO",
        "type": "Button",
        "state": "0",
        "function": 21,
        "function_name": "Auto chase",
    }
    assert widgets[4]["function"] is None
    assert live_widgets(_settings(qlc), detail=False)[0] == {"id": 3, "caption": "AUTO"}


def test_functions_with_and_without_detail(qlc):
    assert live_functions(_settings(qlc)) == [
        {"id": 21, "name": "Auto chase"},
        {"id": 22, "name": "Rojo"},
    ]
    detailed = live_functions(_settings(qlc), detail=True)
    assert detailed[1] == {"id": 22, "name": "Rojo", "type": "Scene", "running": False}


def test_channels_are_read_four_fields_each(qlc):
    channels = live_channels(_settings(qlc), universe=1, start=1, count=3)
    assert channels[0] == {"address": 1, "value": 1, "group": "0.#FF0000", "overridden": False}
    assert [c["address"] for c in channels] == [1, 2, 3]
    assert qlc.received[-1] == "QLC+API|getChannelsValues|1|1|3"


def test_channel_records_parse_an_override():
    assert channel_records(["5", "200", "4", "1"]) == [
        {"address": 5, "value": 200, "group": "4", "overridden": True}
    ]


@pytest.mark.parametrize(
    ("universe", "start", "count"), [(0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 500, 20)]
)
def test_channels_out_of_range_are_refused_before_sending(qlc, universe, start, count):
    with pytest.raises(ValueError, match="must be between"):
        live_channels(_settings(qlc), universe, start, count)
    assert qlc.received == []


def test_writes_are_refused_without_the_flag(qlc):
    with pytest.raises(PermissionError, match="--allow-live-writes"):
        live_press(_settings(qlc), 3)
    with pytest.raises(PermissionError, match="--allow-live-writes"):
        live_function(_settings(qlc), 21, "on")
    assert qlc.received == []
    assert qlc.widgets[3][2] == "0" and qlc.functions[21][2] is False


def test_press_and_release_with_writes_allowed(qlc):
    pressed = live_press(_settings(qlc, writes=True), 3, 255)
    assert pressed == {"widget": 3, "sent": 255, "before": "0", "state": "255"}
    assert "3|255" in qlc.received
    assert live_press(_settings(qlc, writes=True), 3, 0)["state"] == "0"


def test_press_refuses_a_widget_the_console_does_not_have(qlc):
    with pytest.raises(ValueError, match="no widget 99"):
        live_press(_settings(qlc, writes=True), 99)
    assert "99|255" not in qlc.received
    with pytest.raises(ValueError, match="between 0 and 255"):
        live_press(_settings(qlc, writes=True), 3, 256)


def test_function_on_and_off_with_writes_allowed(qlc):
    started = live_function(_settings(qlc, writes=True), 22, "on")
    assert started == {"function": 22, "name": "Rojo", "running": True}
    assert "QLC+API|setFunctionStatus|22|1" in qlc.received
    assert live_function(_settings(qlc, writes=True), 22, "off")["running"] is False
    with pytest.raises(ValueError, match="no function 5"):
        live_function(_settings(qlc, writes=True), 5, "on")


def test_a_silent_qlcplus_is_a_timeout_not_a_hang(qlc):
    qlc.silent = True
    with pytest.raises(TimeoutError, match="did not answer getFunctionsList"):
        live_functions(McpSettings(port=qlc.port, timeout=0.3))


def test_the_link_is_only_used_inside_its_block(qlc):
    link = QlcLink(_settings(qlc))
    with pytest.raises(AssertionError):
        link.send("POLL")
