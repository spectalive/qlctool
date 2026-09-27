"""A rhythm nobody can re-time: an intensity chase outside every speed dial.

The tap dial exists so one hand can put the show on the room's tempo, and
`rule_tap_dial` guards how it is wired. What neither guarded is what is *not*
on it. A chaser that pulses the rig's dimmers keeps its own hold whatever the
music does, so the room gets two tempos: "los barridos de intensidad van a su
bola" (owner, 2026-09-22).

A rhythm here is read off the structure, never a name. Two shapes carry one: a
Chaser whose steps put a fixture's dimmer at different levels, and an EFX whose
fixtures run in Dimmer mode - the sweeps of the rig's intensity are the second
kind (`Dimmer Chase`, four EFX in one Collection). Both have a duration a
`<SpeedDial>` can write, where a tap sets `dial time x multiplier`
(`VCSpeedDial::applyFunctionsTime`), so both belong under one.

A function already carrying `<Tempo Type="Beats">` is clocked by the show's BPM
(`Function::timeToBeats`) and needs no dial: that is the whole point of the
beats build, whose tempo comes from the audio input instead of from a thumb.
A workspace with no dial at all *is* that build - it hands the whole show to
the beat generator, and its EFX layers deliberately stay on milliseconds
because a chaser in Beats passes its fade to each step as a raw number and an
EFX subtracts it from its own duration (`EFX::loopDuration`, the 16 s head
sweep that became 6 s on 2026-08-29). There is nothing for this rule to ask
there, so it stands down.

Putting such a chaser on a dial also means giving it `SpeedModes
Duration="Common"`: in `PerStep`, `ChaserRunner::stepDuration` reads the step and
ignores the chaser, and `Chaser::tap()` refuses outright. That is the fix's
business, not the rule's - a chaser in `PerStep` is unreachable by any dial, so
it is a finding either way.

A chaser whose steps hold one dimmer level is not a rhythm - it is a rotation of
looks that happen to be lit, and its pace is a design choice rather than a beat.
Neither is a chaser whose own steps last longer than a bar of music: the energy
cycle changes level every four minutes and the haze fires every one, and putting
either on the room's tap would be a category error. The line is
`BEAT_CEILING_MS` - above it the chaser is a rotation, below it the room hears
it as a pulse.
"""

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local
from .chaser_longest_hold import chaser_longest_hold
from .dialled_functions import dialled_functions
from .efx_fixture_names import efx_fixture_names
from .efx_sweeps_dimmer import efx_sweeps_dimmer
from .finding import ERROR, Finding
from .pulsed_dimmer_fixtures import pulsed_dimmer_fixtures
from .show_graph import ShowGraph
from .tempo_type_is_beats import tempo_type_is_beats

RULE_ID = "untempoed_rhythm"
# Longest step a room still reads as a beat rather than as a section. Two bars
# at 60 BPM; the dimmer sweeps sit far below it and the energy cycle far above.
BEAT_CEILING_MS = 8000


def check_untempoed_rhythm(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    entries: dict[int, str],
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None or not list(iter_local(console, "SpeedDial")):
        return []
    dialled = dialled_functions(root)
    findings: list[Finding] = []
    reported: set[int] = set()
    for function_id, caption in sorted(entries.items()):
        for member in sorted(graph.descendants(function_id)):
            if member in reported or member in dialled:
                continue
            function = graph.functions.get(member)
            if function is None or tempo_type_is_beats(function):
                continue
            kind = function.attrib.get("Type")
            if kind == "EFX":
                if not efx_sweeps_dimmer(function):
                    continue
                pulsed = efx_fixture_names(graph, groups, member)
            elif kind == "Chaser":
                if chaser_longest_hold(function) > BEAT_CEILING_MS:
                    continue
                pulsed = pulsed_dimmer_fixtures(graph, groups, member)
            else:
                continue
            if not pulsed:
                continue
            reported.add(member)
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=caption,
                    fixtures=tuple(sorted(pulsed)),
                    message_id="untempoed_rhythm_no_dial",
                    fields={"member": graph.name(member), "count": len(pulsed)},
                )
            )
    return findings
