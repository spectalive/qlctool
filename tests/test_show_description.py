"""The show's own choices live in one description (2026-09-24, spec step 2)."""

from dataclasses import replace

from rig_root import RIG_ROOT

from qlctool.argb import argb_from_rgb
from qlctool.description.contrast_pairs_of import contrast_pairs_of
from qlctool.description.pastel_palette_of import pastel_palette_of
from qlctool.description.split_pairs_of import split_pairs_of
from qlctool.description.wheel_palette_of import wheel_palette_of
from qlctool.generate.beat_tempo import BeatTiming
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.generate.unison_colors import CONTRAST_PAIRS
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.pastel_palette import PASTEL_PALETTE
from qlctool.split_pairs import SPLIT_PAIRS
from qlctool.vibra.vibra_description import vibra_description
from qlctool.wheel_palette import WHEEL_PALETTE
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

REPO = RIG_ROOT
VIBRA_SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"
# DeluxeEventos2.qxw is the hand-built show and already carries a
# VirtualConsole/Properties/Size element; Vibra.qxw never gets one written
# (strip_to_skeleton does not add it, and `_set_canvas` stays a no-op without
# one - controller ruling F1, for byte identity), so only this one test reads
# the canvas back off generated XML and it uses the hand-built show instead.
CONSOLE_SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _generated(description, show=VIBRA_SHOW):
    workspace = Workspace.load(show)
    build_canonical_show(workspace, FixtureLibrary.load(), description=description)
    return workspace.root


def test_vibra_is_the_default_description():
    show = vibra_description()
    assert (show.timing.bpm, show.timing.beat_ms, show.timing.peak_ms) == (120, 500, 40_000)
    assert show.timing.beat_timings["colour_wheel"] == BeatTiming(hold=8, fade=1)
    assert show.tuning.beam_focus == 127
    assert (show.tuning.strobe_fast, show.tuning.strobe_slow) == (0.97, 0.785)
    assert show.console.canvas == (1440, 900)
    assert show.console.keys["auto"] == "Q"
    assert "stage_aim" in show.console.flash_functions
    assert [s.algorithm for s in show.matrices["Cabezas"]] == [
        "One By One",
        "Fill Unfill",
        "Noise",
        "Alternate",
        "Opposite",
        "Random Column",
    ]


def test_the_description_sets_the_console_canvas_and_the_clock():
    vibra = vibra_description()
    described = replace(
        vibra,
        console=replace(vibra.console, canvas=(1600, 1000)),
        timing=replace(vibra.timing, bpm=100),
    )
    root = _generated(described, show=CONSOLE_SHOW)
    size = find_local(find_local(find_local(root, "VirtualConsole"), "Properties"), "Size")
    assert (size.get("Width"), size.get("Height")) == ("1600", "1000")
    generator = next(e for e in root.iter() if e.tag.endswith("}BeatGenerator"))
    assert generator.get("BPM") == "100"


def test_the_derived_colour_tables_are_todays():
    # 2026-09-24: vibra_description() is now identifier-keyed (ruling F3), so
    # today's Spanish-named tables are translated to identifiers before the
    # comparison; the values and the order are still today's.
    names = default_names()

    def identify(name):
        return names.identify(name, ("colors",))

    colours = vibra_description().colours
    assert list(wheel_palette_of(colours).items()) == [
        (identify(name), rgb) for name, rgb in WHEEL_PALETTE.items()
    ]
    assert list(pastel_palette_of(colours).items()) == [
        (identify(name), rgb) for name, rgb in PASTEL_PALETTE.items()
    ]
    assert split_pairs_of(colours) == tuple((identify(a), identify(b)) for a, b in SPLIT_PAIRS)
    assert contrast_pairs_of(colours) == tuple(
        (identify(a), identify(b)) for a, b in CONTRAST_PAIRS
    )


def test_the_description_palette_colours_the_matrices():
    vibra = vibra_description()
    colours = replace(
        vibra.colours,
        palette={**vibra.colours.palette, "red": (250, 0, 0)},
        matrix_colors=("red",),
    )
    root = _generated(replace(vibra, colours=colours))
    bars = [
        f
        for f in root.iter()
        if f.tag.endswith("}Function") and f.get("Path") == "Matrices BarrasLed"
    ]
    names = [f.get("Name") for f in bars]
    assert "BarrasLed - Fill Rojo" in names
    assert "BarrasLed - Fill Verde" not in names
    red = str(argb_from_rgb((250, 0, 0)))
    assert any(e.text == red for f in bars for e in f.iter())
