"""Spec step 6 (2026-09-25): the toolkit finds a rig's fixtures without this repo.

`library.REPO_ROOT` was three folders above the package; a copy of the package
anywhere else found no definition, and `capabilities_of` skipped every fixture
in silence ("no fixture has both pan and tilt" in a scratch copy, 2026-09-24).
"""

import hashlib
import json
import os
import re
import shutil
from pathlib import Path

import pytest
from rig_root import RIG_ROOT

from qlctool.cli import main
from qlctool.definition import load_definition
from qlctool.fixture_dirs import fixture_dirs
from qlctool.library import FixtureLibrary
from qlctool.read_toolkit_config import read_toolkit_config
from qlctool.toolkit_config import ToolkitConfig

REPO = RIG_ROOT
BASELINE = json.loads((Path(__file__).with_name("vibra_baseline.json")).read_text("utf-8"))


def _config(folder: Path, fixtures: str) -> Path:
    (folder / fixtures).mkdir(parents=True, exist_ok=True)
    (folder / "qlctool.toml").write_text(f'fixtures = ["{fixtures}"]\n', encoding="utf-8")
    return folder / fixtures


def test_the_repo_config_names_its_three_folders():
    config = read_toolkit_config(REPO / "qlctool.toml")
    assert config == ToolkitConfig(
        fixtures=(REPO / "QLC+ Fixtures",),
        input_profiles=(REPO / "QLC+ InputProfiles",),
        gobos=(REPO / "QLC+ Setups" / "Gobos",),
    )


def test_an_unknown_key_is_refused(tmp_path):
    (tmp_path / "qlctool.toml").write_text('fixture = ["x"]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="fixture"):
        read_toolkit_config(tmp_path / "qlctool.toml")


def test_the_nearest_config_walking_up_is_the_last_resort(tmp_path):
    found = _config(tmp_path, "defs")
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert fixture_dirs(environ={}, start=nested / "show.qxw") == (found,)
    assert fixture_dirs(environ={}, start=tmp_path.parent / "elsewhere") == ()


def test_each_source_beats_the_ones_after_it(tmp_path):
    _config(tmp_path, "from-config")
    env = {"QLCTOOL_FIXTURES": os.pathsep.join([str(tmp_path / "env1"), str(tmp_path / "env2")])}
    described = [tmp_path / "described"]
    assert fixture_dirs(["cli"], described, env, tmp_path) == (Path("cli"),)
    assert fixture_dirs([], described, env, tmp_path) == tuple(described)
    assert fixture_dirs([], [], env, tmp_path) == (tmp_path / "env1", tmp_path / "env2")


def test_the_first_directory_wins_a_model_clash(tmp_path):
    # Same manufacturer and model in both folders, told apart by <Type>: the
    # second copy says something the first does not, so the winner is visible.
    one = sorted((REPO / "QLC+ Fixtures").glob("*.qxf"))[0]
    first, second = tmp_path / "first", tmp_path / "second"
    for folder in (first, second):
        folder.mkdir()
    shutil.copy(one, first / one.name)
    text = one.read_text(encoding="utf-8")
    kind = re.search(r"<Type>(.*?)</Type>", text).group(1)
    (second / one.name).write_text(
        text.replace(f"<Type>{kind}</Type>", "<Type>Other</Type>"), encoding="utf-8"
    )
    defined = load_definition(one)
    library = FixtureLibrary.load([first, second])
    assert library.sources == (first, second)
    assert library.get(defined.manufacturer, defined.model).fixture_type == kind != "Other"
    reversed_library = FixtureLibrary.load([second, first])
    assert reversed_library.get(defined.manufacturer, defined.model).fixture_type == "Other"


def test_a_rig_outside_the_repo_regenerates_vibra(tmp_path, monkeypatch):
    rig = tmp_path / "rig"
    rig.mkdir()
    for name in ("Vibra.qxw", "vibra-stage-plot.json", "vibra.toml"):
        shutil.copy(REPO / "QLC+ Setups" / name, rig / name)
    shutil.copytree(REPO / "QLC+ Fixtures", rig / "fixtures")
    toml = rig / "vibra.toml"
    text = toml.read_text(encoding="utf-8")
    toml.write_text(
        text.replace(
            'stage_plot = "vibra-stage-plot.json"',
            'stage_plot = "vibra-stage-plot.json"\nfixtures = ["fixtures"]',
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("QLCTOOL_FIXTURES", raising=False)
    out = tmp_path / "out.qxw"
    assert main(["newshow", "--description", str(toml), "--out", str(out)]) == 0
    assert hashlib.sha256(out.read_bytes()).hexdigest() == BASELINE["Vibra.qxw"]["sha256"]


@pytest.mark.parametrize(
    "command",
    [
        ["info"],
        ["check"],
        ["palette", "--out", "out.qxw"],
        ["movement", "--out", "out.qxw"],
        ["deskmap", "--out", "desk.json"],
    ],
    ids=lambda command: command[0],
)
def test_a_patch_with_no_definition_says_so(tmp_path, monkeypatch, capsys, command):
    # Copied out of the repo: walking up from the original would find qlctool.toml.
    shutil.copy(REPO / "QLC+ Setups" / "Vibra.qxw", tmp_path / "Vibra.qxw")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("QLCTOOL_FIXTURES", raising=False)
    argv = [command[0], str(tmp_path / "Vibra.qxw"), *command[1:]]
    if command[0] == "movement":
        # The 2026-09-24 failure itself: with no definition nothing has pan and
        # tilt. The warning now comes first and says why.
        with pytest.raises(ValueError, match="pan and tilt"):
            main(argv)
    else:
        main(argv)
    assert "no fixture definition" in capsys.readouterr().err
