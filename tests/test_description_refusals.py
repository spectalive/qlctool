"""A description the generator would crash on is refused while it is read (final review, 2026-09-24).

Each case here once passed the loader and failed later inside
`build_canonical_show`, or failed with a message about a section the user never
wrote.
"""

from pathlib import Path

import pytest

from qlctool.description.load_show_description import load_show_description
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace

SETUPS = Path(__file__).resolve().parents[3] / "QLC+ Setups"
SMALL = (
    "[palette]\n"
    'primary = ["red", "green", "blue", "white"]\n'
    'simple = ["red", "green", "blue"]\n'
    'white = "white"\n'
    'matrix_colors = ["red", "green", "blue"]\n'
    'analogous_pairs = [["red", "blue"]]\n'
    'key_split_pairs = [["blue", "red"]]\n'
    'complementary_pairs = [["red", "green"]]\n'
    "[palette.colors]\n"
    "red = [255, 0, 0]\ngreen = [0, 255, 0]\nblue = [0, 0, 255]\nwhite = [255, 255, 255]\n"
)


def _vibra_colours_without(*dropped):
    palette = vibra_description().colours.palette
    rows = "".join(
        f"{name} = [{r}, {g}, {b}]\n" for name, (r, g, b) in palette.items() if name not in dropped
    )
    return "[palette.colors]\n" + rows


def _write(tmp_path, text):
    path = tmp_path / "show.toml"
    path.write_text('[rig]\nworkspace = "Vibra.qxw"\n' + text, encoding="utf-8")
    return path


def _patch_without(group):
    root = Workspace.load(SETUPS / "Vibra.qxw").root
    for element in list(root.iter("{*}FixtureGroup")):
        name = element.find("{*}Name")
        if name is not None and name.text == group:
            element.getparent().remove(element)
    return root


@pytest.fixture(scope="module")
def patch_root():
    return Workspace.load(SETUPS / "Vibra.qxw").root


# Item 1: `[palette] colors = {red, green, blue, white}` loaded, and the build
# then died on `KeyError: 'Amarillo'` in the four-colour rig scenes.
def test_a_palette_without_the_dealt_colours_is_refused(tmp_path, patch_root):
    path = _write(tmp_path, SMALL + "[groups]\n")
    with pytest.raises(ValueError, match=r"\[palette\] colors lacks yellow") as refused:
        load_show_description(path, patch_root)
    assert str(path) in str(refused.value)


def test_a_small_palette_with_the_dealt_colours_loads(tmp_path, patch_root):
    text = SMALL.replace(
        "white = [255, 255, 255]\n", "white = [255, 255, 255]\nyellow = [255, 255, 0]\n"
    )
    loaded = load_show_description(_write(tmp_path, text + "[groups]\n"), patch_root)
    assert set(loaded.colours.palette) == {"red", "green", "blue", "white", "yellow"}
    assert loaded.matrices == {}


# Item 2: without [groups], Vibra's default matrices apply only to the groups of
# the same name the patch has, and a colour they need is explained as theirs.
def test_default_matrices_follow_the_patch(tmp_path):
    loaded = load_show_description(
        _write(tmp_path, _vibra_colours_without("fire_red", "sky_blue")), _patch_without("PAR")
    )
    assert set(loaded.matrices) == {"BarrasLed", "Cabezas"}
    assert loaded.matrices["Cabezas"] == vibra_description().matrices["Cabezas"]


def test_a_default_matrix_colour_the_palette_lacks_is_explained(tmp_path, patch_root):
    path = _write(tmp_path, _vibra_colours_without("fire_red"))
    with pytest.raises(ValueError) as refused:
        load_show_description(path, patch_root)
    message = str(refused.value)
    assert "Vibra's default matrices for group PAR" in message and "fire_red" in message
    assert "state [groups]" in message and "empty [groups] means no curated matrices" in message
    assert str(path) in message


def test_an_empty_groups_table_means_no_curated_matrices(tmp_path, patch_root):
    text = _vibra_colours_without("fire_red") + "[groups]\n"
    assert load_show_description(_write(tmp_path, text), patch_root).matrices == {}


# Item 4: `[names.en] blue = "red"` loaded, and the build then raised
# `NameResolutionError: 'red' is ambiguous`.
@pytest.mark.parametrize(
    ("text", "other"),
    [
        ('[names.en]\nblue = "red"\n', "red"),
        ('[names.en]\nblue = "Rojo"\n', "red"),
        ('[names.en]\nblue = "green"\n', "green"),
    ],
)
def test_an_override_that_names_another_identifier_is_refused(tmp_path, patch_root, text, other):
    path = _write(tmp_path, text)
    with pytest.raises(
        ValueError, match=r"\[names\.en\] blue = .* already a name of " + other
    ) as refused:
        load_show_description(path, patch_root)
    assert str(path) in str(refused.value)


def test_an_override_may_respell_its_own_identifier(tmp_path, patch_root):
    loaded = load_show_description(_write(tmp_path, '[names.en]\nblue = "Blue"\n'), patch_root)
    assert loaded.names == {"en": {"blue": "Blue"}}
