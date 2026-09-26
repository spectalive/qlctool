"""2026-09-26 (ruling D-R6): `qlctool mcp` serves every tool over stdio, read-only by default.

Through the MCP SDK's own client: in process for the tool calls, and once
as a real stdio subprocess, the way an agent's host starts it. Skipped where
the optional `mcp` extra is not installed (`test_mcp_command.py` holds the
command to naming it there).
"""

import sys

import pytest

pytest.importorskip("mcp")
pytest.importorskip("websockets")

from fake_qlcplus import FakeQlcPlus
from mcp import Client, StdioServerParameters
from rig_root import RIG_ROOT

from qlctool.mcpserver.build_server import build_server
from qlctool.mcpserver.mcp_settings import McpSettings

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
TOOLS = {
    "info",
    "newshow",
    "check",
    "validate",
    "deskmap",
    "pad_palette",
    "live_status",
    "live_widgets",
    "live_functions",
    "live_channels",
    "live_press",
    "live_function",
}


def _client(**settings):
    return Client(build_server(McpSettings(**settings)))


@pytest.mark.anyio
async def test_the_tools_and_their_safety_annotations():
    async with _client() as client:
        tools = {tool.name: tool for tool in (await client.list_tools()).tools}
    assert set(tools) == TOOLS
    assert tools["check"].annotations.read_only_hint is True
    assert tools["live_widgets"].annotations.read_only_hint is True
    assert tools["live_press"].annotations.destructive_hint is True


@pytest.mark.anyio
async def test_offline_tools_answer_through_the_protocol(tmp_path):
    async with _client() as client:
        info = await client.call_tool("info", {"workspace": str(VIBRA)})
        checked = await client.call_tool("check", {"workspace": str(VIBRA), "limit": 5})
        palette = await client.call_tool("pad_palette", {"workspace": str(VIBRA)})
        desk = await client.call_tool(
            "deskmap", {"workspace": str(VIBRA), "out": str(tmp_path / "d.json")}
        )
        missing = await client.call_tool("newshow", {"out": str(tmp_path / "x.qxw")})
    assert not info.is_error and len(info.structured_content["fixtures"]) == 34
    assert checked.structured_content["clean"] is True
    assert len(palette.structured_content["pads"]) == 32
    assert desk.structured_content["out"] == str(tmp_path / "d.json")
    assert missing.is_error and "workspace or a description" in missing.content[0].text


@pytest.mark.anyio
async def test_live_tools_read_and_refuse_through_the_protocol():
    with FakeQlcPlus() as qlc:
        async with _client(port=qlc.port, timeout=1.0) as client:
            status = await client.call_tool("live_status", {})
            widgets = await client.call_tool("live_widgets", {"detail": False})
            functions = await client.call_tool("live_functions", {})
            channels = await client.call_tool("live_channels", {"count": 2})
            press = await client.call_tool("live_press", {"widget_id": 3})
            start = await client.call_tool("live_function", {"function_id": 21, "state": "on"})
        assert status.structured_content["reachable"] is True
        assert "AUTO" in widgets.content[0].text and "Rojo" in str(functions.content)
        assert "0.#FF0000" in str(channels.content)
        for refused in (press, start):
            assert refused.is_error and "--allow-live-writes" in refused.content[0].text
        assert qlc.widgets[3][2] == "0" and qlc.functions[21][2] is False
        async with _client(port=qlc.port, timeout=1.0, allow_writes=True) as client:
            pressed = await client.call_tool("live_press", {"widget_id": 3})
            started = await client.call_tool("live_function", {"function_id": 21, "state": "on"})
        assert pressed.structured_content["state"] == "255"
        assert started.structured_content["running"] is True


@pytest.mark.anyio
async def test_qlctool_mcp_serves_over_stdio():
    server = StdioServerParameters(
        command=sys.executable, args=["-m", "qlctool.cli", "mcp", "--qlc-port", "1"]
    )
    async with Client(server) as client:
        names = {tool.name for tool in (await client.list_tools()).tools}
        refused = await client.call_tool("live_press", {"widget_id": 1})
    assert names == TOOLS
    assert refused.is_error and "--allow-live-writes" in refused.content[0].text
