"""2026-09-26 (ruling D-R6): the MCP server's file tools call what the CLI calls.

Each tool is held to the command it wraps - the same fixtures, the same
findings, the same bytes on disk - and to the path rules the server adds:
a path it reads must exist, a path it writes is never inside the installed
package and never replaces a file unless the caller says so.
"""

import json
from pathlib import Path

import pytest
from rig_root import RIG_ROOT

import qlctool
from qlctool.cli import main
from qlctool.mcpserver.tool_check import tool_check
from qlctool.mcpserver.tool_deskmap import tool_deskmap
from qlctool.mcpserver.tool_info import tool_info
from qlctool.mcpserver.tool_newshow import tool_newshow
from qlctool.mcpserver.tool_pad_palette import tool_pad_palette
from qlctool.mcpserver.tool_validate import tool_validate
from qlctool.validate import qlcplus_binary

SETUPS = RIG_ROOT / "QLC+ Setups"
VIBRA = SETUPS / "Vibra.qxw"
CLUB_DIR = Path(__file__).resolve().parents[1] / "examples" / "small-club"
CLUB = CLUB_DIR / "club.qxw"
CLUB_FIXTURES = [str(CLUB_DIR / "fixtures")]


def test_info_lists_every_patched_fixture_with_its_roles():
    info = tool_info(str(VIBRA))
    assert len(info["fixtures"]) == 34
    first = info["fixtures"][0]
    assert (first["model"], first["universe"], first["address"]) == ("CromoWash100", 1, 1)
    assert {"pan", "tilt", "dimmer"} <= set(first["roles"])
    assert info["groups"][0]["heads"] == 16
    assert info["unresolved"] == []


def test_info_names_the_models_it_cannot_read(tmp_path):
    info = tool_info(str(CLUB), [str(tmp_path)])
    assert info["fixtures"] == []
    assert info["unresolved"]


def test_check_of_the_shipped_shows_is_clean_in_their_own_language():
    vibra = tool_check(str(VIBRA))
    assert vibra["clean"] and vibra["findings"] == []
    assert "ningun problema" in vibra["summary"]
    club = tool_check(str(CLUB), fixtures=CLUB_FIXTURES)
    assert club["clean"] and "no problems" in club["summary"]


def test_check_returns_structured_findings(tmp_path):
    checked = tool_check(str(CLUB), fixtures=[str(tmp_path)], limit=2)
    assert not checked["clean"]
    assert checked["count"] > 2 and len(checked["findings"]) == 2
    finding = checked["findings"][0]
    assert finding["rule_id"] == "missing_fixture_definition"
    assert finding["severity"] == "error"
    assert finding["message"] and finding["rule"]
    json.dumps(checked)


def test_check_with_a_description_speaks_its_language():
    checked = tool_check(str(VIBRA), description=str(SETUPS / "vibra.toml"))
    assert checked["clean"]


def test_a_path_that_is_not_there_is_refused_by_name(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        tool_info(str(tmp_path / "nothing.qxw"))


def test_newshow_writes_the_cli_bytes_where_it_is_told(tmp_path):
    out = tmp_path / "club-new.qxw"
    built = tool_newshow(str(out), str(CLUB_DIR / "club-patch.qxw"), fixtures=CLUB_FIXTURES)
    assert built["out"] == str(out) and built["functions"] > 0 and built["buttons"] > 0
    cli_out = tmp_path / "club-cli.qxw"
    patch = str(CLUB_DIR / "club-patch.qxw")
    assert main(["--fixtures", CLUB_FIXTURES[0], "newshow", patch, "--out", str(cli_out)]) == 0
    assert out.read_bytes() == cli_out.read_bytes()


def test_newshow_from_a_description_rebuilds_vibra(tmp_path):
    out = tmp_path / "Vibra.qxw"
    tool_newshow(str(out), description=str(SETUPS / "vibra.toml"))
    assert out.read_bytes() == VIBRA.read_bytes()


def test_newshow_never_replaces_a_file_unasked(tmp_path):
    out = tmp_path / "kept.qxw"
    out.write_text("keep me")
    with pytest.raises(ValueError, match="overwrite=true"):
        tool_newshow(str(out), str(CLUB_DIR / "club-patch.qxw"), fixtures=CLUB_FIXTURES)
    assert out.read_text() == "keep me"
    tool_newshow(str(out), str(CLUB_DIR / "club-patch.qxw"), overwrite=True, fixtures=CLUB_FIXTURES)
    assert out.read_text() != "keep me"


def test_newshow_never_writes_inside_the_installed_package():
    inside = Path(qlctool.__file__).resolve().parent / "generated.qxw"
    with pytest.raises(ValueError, match="installed qlctool package"):
        tool_newshow(str(inside), str(CLUB_DIR / "club-patch.qxw"), fixtures=CLUB_FIXTURES)
    assert not inside.exists()


def test_newshow_refuses_a_folder_that_is_not_there(tmp_path):
    with pytest.raises(ValueError, match="does not exist"):
        tool_newshow(str(tmp_path / "no" / "show.qxw"), str(CLUB_DIR / "club-patch.qxw"))


def test_newshow_needs_a_patch():
    with pytest.raises(ValueError, match="workspace or a description"):
        tool_newshow("/tmp/x.qxw")


def test_newshow_passes_on_the_rig_minimum_refusal(tmp_path):
    with pytest.raises(ValueError, match="newshow"):
        tool_newshow(
            str(tmp_path / "x.qxw"), str(CLUB_DIR / "club-patch.qxw"), fixtures=[str(tmp_path)]
        )


def test_deskmap_is_the_shipped_map_byte_for_byte(tmp_path):
    shipped = SETUPS / "Vibra.desk.json"
    assert tool_deskmap(str(VIBRA)) == json.loads(shipped.read_text(encoding="utf-8"))
    out = tmp_path / "Vibra.desk.json"
    written = tool_deskmap(str(VIBRA), out=str(out))
    assert out.read_bytes() == shipped.read_bytes()
    assert written["controls"] > 0 and written["pages"]


def test_deskmap_with_a_description_uses_its_names():
    deskmap = tool_deskmap(str(VIBRA), description=str(SETUPS / "vibra.toml"))
    assert deskmap["controls"]


def test_pad_palette_matches_the_cli(tmp_path):
    cli_out = tmp_path / "cli.json"
    assert main(["pad-palette", str(VIBRA), "--out", str(cli_out)]) == 0
    out = tmp_path / "tool.json"
    written = tool_pad_palette(str(VIBRA), out=str(out))
    assert out.read_bytes() == cli_out.read_bytes()
    assert written["pads"] == 32 and written["lit"] > 0
    assert tool_pad_palette(str(VIBRA)) == json.loads(cli_out.read_text(encoding="utf-8"))


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_validate_loads_the_show_in_qlcplus():
    assert tool_validate(str(VIBRA)) == {"workspace": str(VIBRA), "ok": True, "errors": []}
