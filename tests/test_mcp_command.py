"""2026-09-26 (ruling D-R6): without the optional extra, `qlctool mcp` names it and exits 1.

Plain qlctool never imports the MCP SDK or the websocket client; the command
that needs them says which install brings them instead of a traceback.
"""

import sys

from qlctool.cli import main


def test_without_the_extra_the_command_names_it(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "mcp", None)
    assert main(["mcp"]) == 1
    assert 'pip install "qlctool[mcp]"' in capsys.readouterr().err


def test_the_help_names_the_extra_and_the_read_only_default(capsys):
    try:
        main(["mcp", "--help"])
    except SystemExit as done:
        assert done.code == 0
    said = capsys.readouterr().out
    assert "qlctool[mcp]" in said and "--allow-live-writes" in said
