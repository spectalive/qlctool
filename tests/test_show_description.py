"""The show's own choices live in one description (2026-09-24, spec step 2)."""

from dataclasses import replace
from pathlib import Path

from qlctool.generate.beat_tempo import BeatTiming
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

REPO = Path(__file__).resolve().parents[3]
# DeluxeEventos2.qxw is the hand-built show and already carries a
# VirtualConsole/Properties/Size element; Vibra.qxw never gets one written
# (strip_to_skeleton does not add it, and `_set_canvas` stays a no-op without
# one - controller ruling F1, for byte identity), so only this one test reads
# the canvas back off generated XML and it uses the hand-built show instead.
CONSOLE_SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _generated(show, description):
    workspace = Workspace.load(show)
    build_canonical_show(workspace, FixtureLibrary.load(), description=description)
    return workspace.root


def test_vibra_is_the_default_description():
    show = vibra_description()
    assert (show.timing.bpm, show.timing.beat_ms, show.timing.peak_ms) == (120, 500, 40_000)
    assert show.timing.beat_timings["Rueda Colores"] == BeatTiming(hold=8, fade=1)
    assert show.tuning.beam_focus == 127
    assert (show.tuning.strobe_fast, show.tuning.strobe_slow) == (0.97, 0.785)
    assert show.console.canvas == (1440, 900)
    assert show.console.keys["AUTO"] == "Q"
    assert "Escenario" in show.console.flash_functions
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
    root = _generated(CONSOLE_SHOW, described)
    size = find_local(find_local(find_local(root, "VirtualConsole"), "Properties"), "Size")
    assert (size.get("Width"), size.get("Height")) == ("1600", "1000")
    generator = next(e for e in root.iter() if e.tag.endswith("}BeatGenerator"))
    assert generator.get("BPM") == "100"
