"""`newshow --description` builds a show from a description, and never overwrites a patch unasked."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from rig_root import RIG_ROOT

from qlctool.cli import main
from qlctool.names.load_catalogue import load_catalogue

TESTS = Path(__file__).resolve().parent
SETUPS = RIG_ROOT / "QLC+ Setups"
BASELINE = json.loads((TESTS / "vibra_baseline.json").read_text(encoding="utf-8"))


def _digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rig(tmp_path, text, *files):
    """A description beside copies of `files`, its [rig] naming the copied Vibra.qxw."""
    for name in files:
        shutil.copyfile(SETUPS / name, tmp_path / name)
    path = tmp_path / "show.toml"
    path.write_text('[rig]\nworkspace = "Vibra.qxw"\n' + text, encoding="utf-8")
    return path


def test_newshow_writes_vibra_from_its_description(tmp_path):
    out = tmp_path / "Vibra.qxw"
    assert main(["newshow", "--description", str(SETUPS / "vibra.toml"), "--out", str(out)]) == 0
    assert _digest(out) == BASELINE["Vibra.qxw"]["sha256"]


def test_newshow_reports_a_bad_description_without_a_traceback(tmp_path):
    path = _rig(tmp_path, "[pallete]\n", "Vibra.qxw")
    with pytest.raises(SystemExit, match="pallete"):
        main(["newshow", "--description", str(path), "--out", str(tmp_path / "out.qxw")])


def test_newshow_reports_a_missing_patch_without_a_traceback(tmp_path):
    path = _rig(tmp_path, "")
    with pytest.raises(SystemExit, match=r"Vibra\.qxw"):
        main(["newshow", "--description", str(path), "--out", str(tmp_path / "out.qxw")])


def test_newshow_writes_an_english_show(tmp_path):
    """2026-09-25: the Spanish-only gate is gone; `language = "en"` builds."""
    path = _rig(tmp_path, '[show]\nlanguage = "en"\n', "Vibra.qxw")
    out = tmp_path / "out.qxw"
    assert main(["newshow", "--description", str(path), "--out", str(out)]) == 0
    title = load_catalogue("en")["frames"]["room_states"]
    assert f'Caption="{title}"' in out.read_text(encoding="utf-8")


def test_newshow_without_out_writes_the_rig_output(tmp_path, capsys):
    for name in ("Vibra.qxw", "vibra-stage-plot.json", "vibra-beats.toml"):
        shutil.copyfile(SETUPS / name, tmp_path / name)
    assert main(["newshow", "--description", str(tmp_path / "vibra-beats.toml")]) == 0
    assert _digest(tmp_path / "Vibra-beats.qxw") == BASELINE["Vibra-beats.qxw"]["sha256"]
    assert "Press AUTO (key Q)." in capsys.readouterr().out


# Final review of Plan A (2026-09-24): a description without [rig] output used
# to regenerate its own patch in place. The patch is the one file that must not
# change by accident, so neither --out nor [rig] output is now a refusal.
def test_newshow_refuses_to_guess_where_to_write(tmp_path):
    path = _rig(tmp_path, "", "Vibra.qxw")
    before = _digest(tmp_path / "Vibra.qxw")
    with pytest.raises(SystemExit, match=r"\[rig\] output.*--out") as refused:
        main(["newshow", "--description", str(path)])
    assert str(path) in str(refused.value)
    assert _digest(tmp_path / "Vibra.qxw") == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["Vibra.qxw", "show.toml"]


def test_an_output_equal_to_the_workspace_regenerates_it_in_place(tmp_path):
    for name in ("Vibra.qxw", "vibra-stage-plot.json", "vibra.toml"):
        shutil.copyfile(SETUPS / name, tmp_path / name)
    assert main(["newshow", "--description", str(tmp_path / "vibra.toml")]) == 0
    assert _digest(tmp_path / "Vibra.qxw") == BASELINE["Vibra.qxw"]["sha256"]


def test_a_positional_workspace_must_be_the_described_one(tmp_path):
    path = _rig(tmp_path, 'output = "out.qxw"\n', "Vibra.qxw")
    with pytest.raises(SystemExit) as refused:
        main(["newshow", str(SETUPS / "Vibra-split.qxw"), "--description", str(path)])
    message = str(refused.value)
    assert str(tmp_path / "Vibra.qxw") in message and "Vibra-split.qxw" in message
    assert not (tmp_path / "out.qxw").exists()


def test_a_positional_workspace_equal_to_the_described_one_is_accepted(tmp_path):
    path = _rig(tmp_path, "", "Vibra.qxw")
    out = tmp_path / "out.qxw"
    assert (
        main(
            ["newshow", str(tmp_path / "Vibra.qxw"), "--description", str(path), "--out", str(out)]
        )
        == 0
    )
    assert out.exists()
