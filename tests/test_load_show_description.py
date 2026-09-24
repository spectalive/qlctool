"""A show description is read from TOML and checked against its patch (2026-09-24, spec step 5)."""

from dataclasses import replace
from pathlib import Path

import pytest

from qlctool.description.controller_settings import ControllerSettings
from qlctool.description.load_show_description import load_show_description
from qlctool.description.rig_files import RigFiles
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace

TESTS = Path(__file__).resolve().parent
SETUPS = TESTS.parents[2] / "QLC+ Setups"


@pytest.fixture(scope="module")
def patch_root():
    return Workspace.load(SETUPS / "Vibra.qxw").root


def _write(tmp_path, text):
    path = tmp_path / "show.toml"
    path.write_text('[rig]\nworkspace = "Vibra.qxw"\n' + text, encoding="utf-8")
    return path


def test_vibra_toml_is_the_vibra_description(patch_root):
    loaded = load_show_description(SETUPS / "vibra.toml", patch_root)
    vibra = vibra_description()
    assert replace(loaded, rig=RigFiles()) == vibra
    assert list(loaded.colours.palette) == list(vibra.colours.palette)
    assert list(loaded.console.keys) == list(vibra.console.keys)
    assert loaded.rig == RigFiles(
        workspace=SETUPS / "Vibra.qxw",
        output=SETUPS / "Vibra.qxw",
        stage_plot=SETUPS / "vibra-stage-plot.json",
    )


@pytest.mark.parametrize(
    ("name", "workspace", "beats"),
    [("vibra-beats.toml", "Vibra.qxw", True), ("vibra-split.toml", "Vibra-split.qxw", False)],
)
def test_the_variants_differ_only_in_their_rig_and_clock(name, workspace, beats):
    loaded = load_show_description(SETUPS / name, Workspace.load(SETUPS / workspace).root)
    assert loaded.timing.beats is beats
    unrigged = replace(loaded, rig=RigFiles(), timing=replace(loaded.timing, beats=False))
    assert unrigged == vibra_description()


def test_the_smallest_description_is_a_rig(tmp_path, patch_root):
    loaded = load_show_description(_write(tmp_path, ""), patch_root)
    assert loaded.controllers == ControllerSettings()
    assert loaded.colours == vibra_description().colours
    assert loaded.rig.workspace == tmp_path / "Vibra.qxw"


def test_names_in_any_language_are_the_same_colour(tmp_path, patch_root):
    loaded = load_show_description(
        _write(tmp_path, '[palette]\nprimary = ["Rojo", "red", "AZUL"]\n'), patch_root
    )
    assert loaded.colours.primary == ("red", "red", "blue")


@pytest.mark.parametrize(
    ("text", "complaint"),
    [
        ('[palette]\nprimary = ["Roja"]\n', "Rojo"),
        (
            '[[groups.Laser.matrices]]\nscript = "Fill"\ncolors = ["red"]\n',
            "Laser.*the patch has: BarrasLed",
        ),
        ("[pallete]\n", "pallete"),
        ('[names.es]\nparty_momment = "Fiesta"\n', "party_momment.*party_moment"),
        ('[controllers]\nmidi_pad = "launchpad"\n', "smc-pad"),
        ('[show]\nlanguage = "fr"\n', "shipped"),
        ("[palette.colors]\nred = [256, 0, 0]\n", "0-255"),
        ("[timing]\nbpm = 0\n", "bpm"),
    ],
)
def test_a_bad_description_is_refused_with_what_is_wrong(tmp_path, patch_root, text, complaint):
    with pytest.raises(ValueError, match=complaint):
        load_show_description(_write(tmp_path, text), patch_root)


# Task 5 ruling (2026-09-24): identifying the names of a table must never merge
# two of its rows. "red" and "Rojo" are one colour, so a table that states both
# would lose one of them without a word - in a file a person wrote by hand.
@pytest.mark.parametrize(
    ("text", "section"),
    [
        ("[palette.colors]\nred = [255, 0, 0]\nRojo = [250, 0, 0]\n", r"\[palette\] colors"),
        ('[console.keys]\nauto = "Q"\nAUTO = "W"\n', r"\[console\] keys"),
        (
            '[timing.beat_timings]\ncolour_wheel = { hold = 8 }\n"Rueda Colores" = { hold = 4 }\n',
            r"\[timing\] beat_timings",
        ),
    ],
)
def test_two_spellings_of_one_name_in_a_table_are_refused(tmp_path, patch_root, text, section):
    path = _write(tmp_path, text)
    with pytest.raises(ValueError, match=section) as refused:
        load_show_description(path, patch_root)
    message = str(refused.value)
    assert str(path) in message
    first, second = (line.split(" = ")[0].strip('"') for line in text.splitlines()[1:3])
    assert repr(first) in message and repr(second) in message


# Ruling F7 (2026-09-24): scalar sections merge key by key, named tables replace whole.
def test_a_scalar_merges_and_a_table_replaces(tmp_path, patch_root):
    text = '[timing]\nbpm = 128\n[console.keys]\nauto = "A"\n'
    loaded = load_show_description(_write(tmp_path, text), patch_root)
    vibra = vibra_description()
    assert loaded.timing == replace(vibra.timing, bpm=128)
    assert dict(loaded.console.keys) == {"auto": "A"}
    assert loaded.console.flash_functions == vibra.console.flash_functions


def test_a_duration_table_is_stated_whole(tmp_path, patch_root):
    with pytest.raises(ValueError, match=r"\[timing\] levels: missing ambient_s"):
        load_show_description(
            _write(tmp_path, "[timing]\nlevels = { party_s = 600 }\n"), patch_root
        )


@pytest.mark.parametrize(
    "text",
    [
        "[palette]\ncolors = 3\n",
        '[palette]\nprimary = "red"\n',
        "[groups]\nBarrasLed = 1\n",
        "[groups.BarrasLed]\nmatrices = [1]\n",
        '[console]\nflash_functions = "auto"\n',
        "[controllers]\nmidi_pad = 7\n",
    ],
)
def test_a_wrongly_shaped_value_is_a_value_error(tmp_path, patch_root, text):
    with pytest.raises(ValueError, match=r"show\.toml"):
        load_show_description(_write(tmp_path, text), patch_root)


# Fix round 1 (2026-09-24, ruling F11): the generator's Spanish-only vocabulary
# (R1) is refused while the file is read, naming it, not later as a traceback.
@pytest.mark.parametrize(
    ("text", "section"),
    [
        ('[show]\nlanguage = "en"\n', r"\[show\].*language 'en'"),
        ('[names.es]\nparty_moment = "Fiesta"\n', r"\[names\].*party_moment"),
    ],
)
def test_a_vocabulary_the_generator_cannot_write_is_refused(tmp_path, patch_root, text, section):
    path = _write(tmp_path, text)
    with pytest.raises(ValueError, match=section) as refused:
        load_show_description(path, patch_root)
    assert str(path) in str(refused.value)


def test_a_beat_timing_keeps_the_default_it_does_not_state(tmp_path, patch_root):
    text = (
        "[timing]\nmatrix_beats = { fade = 2 }\n"
        "[timing.beat_timings]\ncolour_wheel = { hold = 4 }\nsimple_wheel = { hold = 4 }\n"
    )
    timing = load_show_description(_write(tmp_path, text), patch_root).timing
    vibra = vibra_description().timing
    assert (timing.matrix_beats.hold, timing.matrix_beats.fade) == (vibra.matrix_beats.hold, 2)
    assert timing.beat_timings["colour_wheel"].fade == vibra.beat_timings["colour_wheel"].fade == 1
    assert timing.beat_timings["simple_wheel"].fade == 0
    with pytest.raises(ValueError, match="simple_wheel"):
        load_show_description(
            _write(tmp_path, "[timing.beat_timings]\nsimple_wheel = { fade = 1 }\n"), patch_root
        )


def test_the_beats_variant_is_written_beside_its_patch(patch_root):
    loaded = load_show_description(SETUPS / "vibra-beats.toml", patch_root)
    assert loaded.rig.output == SETUPS / "Vibra-beats.qxw"
