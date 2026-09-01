"""Put the chases on the music's beat instead of on a stopwatch.

Every console manual counts a chase in beats and bars - one step per bar, a
colour every two - because a light change that lands off the beat reads as a
mistake to a room that is dancing. QLC+ has the same idea built in:
`Function::TempoType` is `Time` or `Beats`, and in Beats the speed fields are no
longer milliseconds but **thousandths of a beat**, quantised to eighths
(`Function::timeToBeats` floors to 125). So one bar of 4/4 is 4000 and half a
beat is 500.

What ticks the beat is the workspace's beat generator - see `beat_generator` -
and until something does, a function in Beats tempo does not advance. That is
why this is applied to the layers that should feel the music (colour, matrices,
gobos) and never to the energy cycle, which measures the night in minutes and
must keep running whether or not anything is playing.
"""

from dataclasses import dataclass

from lxml import etree

from ..constants import QLC_NS
from ..workspace import Workspace
from ..xmlutil import find_local, findall_local

TEMPO_BEATS = "Beats"
# QLC+ quantises a beat into eighths; 1000 units is one beat.
UNITS_PER_BEAT = 1000
QUANTUM = 125


@dataclass(frozen=True)
class BeatTiming:
    """A function's step timing in beats: how long it fades, how long it holds."""

    hold: float
    fade: float = 0.0


def apply_beat_tempo(workspace: Workspace, timings: dict[str, BeatTiming]) -> list[str]:
    """Switch the named functions to Beats tempo. Returns the names it changed.

    A name the workspace does not carry raises: the timings are written against
    a generated show, so a miss means the show changed and the mapping did not,
    which would otherwise leave that layer silently on the stopwatch.
    """
    by_name = {
        function.attrib.get("Name"): function
        for function in workspace.engine
        if function.attrib.get("Name")
    }
    missing = sorted(set(timings) - set(by_name))
    if missing:
        raise ValueError(f"no function named: {', '.join(missing)}")

    # A Collection has no tempo and no speed: it starts its members and they
    # keep their own. QLC+ says so out loud when it loads one that carries a
    # <Tempo> - "Unknown collection tag: Tempo", read out of the show Mac's
    # log on 2026-08-29 - and ignores it, which is a layer silently left on
    # the stopwatch.
    tempoless = sorted(name for name in timings if by_name[name].attrib.get("Type") == "Collection")
    if tempoless:
        raise ValueError(f"a Collection has no tempo to set: {', '.join(tempoless)}")

    for name, timing in timings.items():
        _to_beats(by_name[name], timing)
    return sorted(timings)


def _to_beats(function, timing: BeatTiming) -> None:
    hold, fade = _units(timing.hold), _units(timing.fade)

    if find_local(function, "Tempo") is None:
        # First child, where Function::saveXML writes it: after the attributes
        # saveXMLCommon carries and before <Speed>.
        tempo = etree.Element(f"{{{QLC_NS}}}Tempo")
        tempo.text = TEMPO_BEATS
        function.insert(0, tempo)

    speed = find_local(function, "Speed")
    if speed is not None:
        speed.set("FadeIn", str(fade))
        speed.set("FadeOut", str(fade))
        speed.set("Duration", str(fade + hold))

    for step in findall_local(function, "Step"):
        step.set("FadeIn", str(fade))
        step.set("Hold", str(hold))
        step.set("FadeOut", str(fade))


def _units(beats: float) -> int:
    """Beats to QLC+'s thousandths, on its own eighth-of-a-beat grid."""
    return round(beats * UNITS_PER_BEAT / QUANTUM) * QUANTUM
