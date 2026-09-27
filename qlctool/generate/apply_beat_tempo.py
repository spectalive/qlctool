"""Put the chases on the music's beat instead of on a stopwatch.

Every console manual counts a chase in beats and bars - one step per bar, a
colour every two - because a light change that lands off the beat reads as a
mistake to a room that is dancing. QLC+ has the same idea built in:
`Function::TempoType` is `Time` or `Beats`, and in Beats the speed fields are no
longer milliseconds but **thousandths of a beat**, quantised to eighths
(`Function::timeToBeats` floors to 125). So one bar of 4/4 is 4000 and half a
beat is 500.

What ticks the beat is the workspace's beat generator - see `set_beat_generator` -
and until something does, a function in Beats tempo does not advance. That is
why this is applied to the layers that should feel the music (colour, matrices,
gobos) and never to the energy cycle, which measures the night in minutes and
must keep running whether or not anything is playing.
"""

from ..workspace import Workspace
from .beat_timing import BeatTiming
from .to_beats import to_beats


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
        to_beats(by_name[name], timing)
    return sorted(timings)
