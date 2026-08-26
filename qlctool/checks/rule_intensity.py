"""Colour with no way out of the fixture: the check for a light that stays dark.

Two of this show's bugs were the same bug wearing different clothes. A matrix
painted the panels beautifully and never touched their master dimmer, so they
were the right colour and off. The beams' gobo scenes opened a dimmer on a
fixture whose mechanical shutter was still shut, so they were aimed and off.

The rule is one sentence: **if a button puts colour on a fixture, something that
same button starts has to open that fixture's intensity path** - its dimmer if
it has one, its shutter if the definition labels one. Anything else is a button
that promises light and does not deliver it.
"""

from .. import roles
from ..shutter_open import shutter_open_ranges
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach

RULE = "intensidad"
# What a DMX channel reads as when no function has written to it.
UNTOUCHED = 0
# A Scene states a colour. A matrix paints one group's pixels and an EFX moves
# a head: those are layers, and a layer answers to the state beneath it.
STATES_COLOUR = ("Scene", "Sequence")


def check_intensity(
    graph: ShowGraph, groups, entries: dict[int, str], states: set[int] | None = None
) -> list[Finding]:
    """Every button, judged by what it is responsible for.

    A **state** of the room - AUTO, a moment, the work light - runs with
    nothing underneath it, so it answers for every fixture it colours by any
    means at all, its matrices included. That is the check the panels failed:
    AUTO painted them and nothing opened them.

    Everything else is a **layer**, pressed on top of whatever state is
    running, and answers only for the colour it states itself, in a Scene. A
    matrix on the library page is not asked to open a dimmer, because it is
    incapable of it and the state beneath it already has.
    """
    states = states or set()
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        kinds = None if function_id in states else STATES_COLOUR
        dark = _dark(graph, reach(graph, groups, function_id, kinds=kinds))
        if not dark:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(function_id),
            message=(
                f"pone color pero no abre la intensidad, asi que "
                f"{'ese fixture se queda' if len(dark) == 1 else 'esos fixtures se quedan'} "
                f"a oscuras (boton: {caption})"
            ),
            fixtures=tuple(sorted(dark)),
        ))
    return findings


def _dark(graph: ShowGraph, driven) -> set[str]:
    dark: set[str] = set()
    for fixture_id, written in driven.items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        if not _colours(capability, written):
            continue
        if _reason_it_stays_dark(capability, written):
            dark.add(capability.fixture.name)
    return dark


def _colours(capability, written: dict[int, int | None]) -> bool:
    """Whether this function is putting a colour on the fixture at all."""
    coloured = {
        offset for role in COLOUR for offset in capability.offsets_for_role(role)
    }
    wheel = capability.wheel_for_role(roles.COLOR_MACRO)
    if wheel is not None:
        coloured.add(wheel[0])
    return any(lit(written[o]) for o in coloured if o in written)


def _reason_it_stays_dark(capability, written: dict[int, int | None]) -> bool:
    dimmers = capability.offsets_for_role(roles.DIMMER)
    if dimmers and not any(lit(written.get(o, 0)) for o in dimmers):
        return True
    return any(
        _shut(written.get(offset, UNTOUCHED), opening)
        for offset, opening in shutter_open_ranges(capability)
    )


def _shut(value: int | None, opening) -> bool:
    """Whether the shutter is somewhere other than its open range.

    An untouched DMX channel is 0, which on one fixture is "no strobe, open"
    and on the next is "closed". A value nobody can predict - an effect driving
    the shutter - is not reported: strobing is what that fixture was asked to
    do.
    """
    if value is None:
        return False
    return not opening.minimum <= value <= opening.maximum
