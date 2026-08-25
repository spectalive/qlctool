"""Chases on the music's beat: the tempo switch and where the beat comes from.

In Beats tempo QLC+ stops reading the speed fields as milliseconds and reads
them as thousandths of a beat, so the same number means something else - which
is why the conversion is a pass of its own and why it is tested against the real
show rather than a fixture.
"""

from pathlib import Path

import pytest

from qlctool.beat_generator import set_beat_generator
from qlctool.generate.beat_tempo import BeatTiming, apply_beat_tempo
from qlctool.generate.unison_colors import generate_unison_colors
from qlctool.library import FixtureLibrary
from qlctool.skeleton import strip_to_skeleton
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


def _function(workspace, name):
    return next(
        f for f in workspace.engine if f.attrib.get("Name") == name
    )


def test_a_wheel_switched_to_beats_counts_in_thousandths_of_a_beat():
    ws = strip_to_skeleton(Workspace.load(SHOW))
    generate_unison_colors(ws, FixtureLibrary.load())

    changed = apply_beat_tempo(ws, {"Rueda Colores": BeatTiming(hold=8, fade=1)})

    assert changed == ["Rueda Colores"]
    wheel = _function(ws, "Rueda Colores")
    # <Tempo> is the first child, where Function::saveXML writes it.
    assert wheel[0].tag.endswith("}Tempo")
    assert wheel[0].text == "Beats"
    speed = find_local(wheel, "Speed")
    # Two bars of 4/4 held, one beat of fade: 8000 and 1000 units.
    assert speed.attrib["FadeIn"] == "1000"
    assert speed.attrib["Duration"] == "9000"
    for step in findall_local(wheel, "Step"):
        assert step.attrib["Hold"] == "8000"
        assert step.attrib["FadeIn"] == "1000"


def test_a_missing_function_is_an_error_not_a_silent_skip():
    """A layer left on the stopwatch by a typo is invisible until the venue."""
    ws = strip_to_skeleton(Workspace.load(SHOW))

    with pytest.raises(ValueError, match="Rueda Que No Existe"):
        apply_beat_tempo(ws, {"Rueda Que No Existe": BeatTiming(hold=4)})


def test_the_beat_can_come_from_the_audio_input():
    ws = strip_to_skeleton(Workspace.load(SHOW))

    set_beat_generator(ws.root, "Audio")

    io_map = find_local(ws.engine, "InputOutputMap")
    generator = find_local(io_map, "BeatGenerator")
    assert generator.attrib["BeatType"] == "Audio"
    # Zero: the source fills it in as soon as it hears something.
    assert generator.attrib["BPM"] == "0"
    assert io_map[0] is generator


def test_an_unknown_beat_source_is_refused():
    ws = strip_to_skeleton(Workspace.load(SHOW))

    with pytest.raises(ValueError, match="Microphone"):
        set_beat_generator(ws.root, "Microphone")
