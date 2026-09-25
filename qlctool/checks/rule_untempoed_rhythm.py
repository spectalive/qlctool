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

from .. import roles
from ..xmlutil import find_local, findall_local, iter_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE_ID = "untempoed_rhythm"
EFX_DIMMER_MODE = "1"  # EFXFixture::Mode - PanTilt, Dimmer, RGB
BEATS = "Beats"  # Function::TempoType
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
    dialled = _dialled_functions(root)
    findings: list[Finding] = []
    reported: set[int] = set()
    for function_id, caption in sorted(entries.items()):
        for member in sorted(graph.descendants(function_id)):
            if member in reported or member in dialled:
                continue
            function = graph.functions.get(member)
            if function is None or _on_beats(function):
                continue
            kind = function.attrib.get("Type")
            if kind == "EFX":
                if not _sweeps_dimmer(function):
                    continue
                pulsed = _efx_fixtures(graph, groups, member)
            elif kind == "Chaser":
                if _longest_hold(function) > BEAT_CEILING_MS:
                    continue
                pulsed = _pulsed_fixtures(graph, groups, member)
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
                    message=(
                        f"«{graph.name(member)}» mueve la intensidad de "
                        f"{len(pulsed)} aparatos y no esta bajo ningun dial de "
                        f"tempo: su paso no cambia cuando cambia el de la sala"
                    ),
                )
            )
    return findings


def _on_beats(function: etree._Element) -> bool:
    """Whether this function already counts in beats of the show's own BPM."""
    tempo = find_local(function, "Tempo")
    return tempo is not None and tempo.attrib.get("Type") == BEATS


def _sweeps_dimmer(function: etree._Element) -> bool:
    """An EFX running any of its fixtures in Dimmer mode."""
    for fixture in iter_local(function, "Fixture"):
        mode = find_local(fixture, "Mode")
        if mode is not None and (mode.text or "").strip() == EFX_DIMMER_MODE:
            return True
    return False


def _efx_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[str]:
    function = graph.functions[function_id]
    return {
        graph.capabilities[fixture_id].fixture.name
        for fixture_id in driven_channels(function, graph.capabilities, groups)
        if fixture_id in graph.capabilities
    }


def _longest_hold(function: etree._Element) -> int:
    """The longest a step of this chaser holds, in milliseconds."""
    holds = [int(step.attrib.get("Hold", 0) or 0) for step in findall_local(function, "Step")]
    return max(holds, default=0)


def _dialled_functions(root: etree._Element) -> set[int]:
    """Function ids some speed dial can re-time, and that can answer one."""
    console = find_local(root, "VirtualConsole")
    if console is None:
        return set()
    dialled: set[int] = set()
    for dial in iter_local(console, "SpeedDial"):
        for function in findall_local(dial, "Function"):
            text = (function.text or "").strip()
            if text.isdigit():
                dialled.add(int(text))
    return dialled


def _pulsed_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], chaser_id: int
) -> set[str]:
    """The fixtures whose dimmer this chaser's steps put at different levels."""
    levels: dict[int, set[int | None]] = {}
    for step in graph.members.get(chaser_id, ()):
        for leaf in graph.descendants(step):
            function = graph.functions.get(leaf)
            if function is None:
                continue
            for fixture_id, pairs in driven_channels(function, graph.capabilities, groups).items():
                capability = graph.capabilities.get(fixture_id)
                if capability is None:
                    continue
                for offset in capability.offsets_for_role(roles.DIMMER):
                    if offset in pairs:
                        levels.setdefault(fixture_id, set()).add(pairs[offset])
    return {
        graph.capabilities[fixture_id].fixture.name
        for fixture_id, seen in levels.items()
        if len(seen) > 1
    }
