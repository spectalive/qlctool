"""A show that is not Vibra's, built from a description, passes every check (final review, 2026-09-24).

The spec's promise is that anyone can write a description. Every other test
builds Vibra; this one builds a palette Vibra never had, with no [groups] and no
[controllers], and asks `qlctool check` whether the result is a working show.
"""

import shutil

from rig_root import RIG_ROOT

from qlctool.checks.run import check_workspace
from qlctool.cli import main
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace

SETUPS = RIG_ROOT / "QLC+ Setups"
# Vibra's default matrices still apply (no [groups]), so every colour they use
# is here; magenta and ultraviolet are gone, and most values move.
DESCRIPTION = """
[show]
name = "Otra Sala"

[rig]
workspace = "Vibra.qxw"
output = "Otra.qxw"

[palette]
primary = ["red", "green", "blue", "yellow", "cyan", "orange", "pink", "white"]
simple = ["red", "yellow", "green", "cyan", "blue"]
white = "white"
matrix_colors = ["red", "green", "blue", "amber", "cyan"]
analogous_pairs = [["red", "yellow"], ["cyan", "blue"], ["green", "cyan"]]
key_split_pairs = [["blue", "red"], ["red", "blue"]]
complementary_pairs = [["amber", "blue"], ["red", "cyan"]]

[palette.colors]
red = [250, 10, 0]
fire_red = [255, 40, 0]
orange = [255, 110, 0]
amber = [255, 170, 0]
yellow = [255, 240, 0]
green = [10, 255, 20]
mint_green = [0, 255, 150]
cyan = [0, 240, 255]
light_blue = [0, 190, 255]
sky_blue = [0, 120, 255]
blue = [0, 10, 255]
deep_blue = [0, 50, 255]
purple = [100, 0, 255]
fuchsia = [255, 0, 160]
pink = [255, 0, 120]
white = [255, 255, 255]
"""


def test_a_non_vibra_description_builds_a_show_with_no_findings(tmp_path):
    shutil.copyfile(SETUPS / "Vibra.qxw", tmp_path / "Vibra.qxw")
    description = tmp_path / "otra.toml"
    description.write_text(DESCRIPTION, encoding="utf-8")
    assert main(["newshow", "--description", str(description)]) == 0
    built = Workspace.load(tmp_path / "Otra.qxw")
    assert check_workspace(built, FixtureLibrary.load()) == []
