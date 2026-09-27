"""A colour *animation* that leaves the wheel-coloured fixtures on one colour.

`rule_wheel_colour` asks whether a look ever states a colour on the beams, and
it counts only Scenes, for a good reason: a matrix paints a group's pixels and
can say nothing about a member that has none. An EFX is different. It lists the
fixtures it drives, one `<Fixture>` each, so a fixture it omits is a decision
nobody made - and nothing was checking those. The two rainbows are relative EFX
in RGB mode over "every RGB head" (`rainbow_efx.py` counts red channels and
finds none on a 7R), so `Arcoiris Simultaneo` sweeps the whole room through the
spectrum with the four beams nailed to whatever colour they had: "el arcoiris
no funciona con los beam, no hace el color arcoiris" (owner, 2026-09-22).

The claim is read per fixture group, exactly as `rule_wheel_colour` reads it: a
look that animates the colour of a group has made a claim about that group, and
the four beams are *in* Cabezas beside the washes. That the state underneath
keeps stepping their wheel every 2,5 s is no defence - the room then shows a
spectrum sweeping over four fixtures walking a different clock, which is the
"no hace el color arcoiris" the owner saw.

A fixture whose colour is a wheel can animate colour - the BEAM 230W 7R carries
a continuous rainbow spin at 128-191 of its colour channel, and a chaser can
step the wheel detent by detent. So the rule is not "the wheel was written": it
is that a look which animates colour on the RGB fixtures must animate it on the
wheel ones too, by a rotation range or by more than one value across the look.
A single static detent under a running rainbow is the bug, not the fix.
"""

from .animated_rgb_fixtures import animated_rgb_fixtures
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .wheel_animated import wheel_animated
from .wheel_coloured_fixture import wheel_coloured_fixture

RULE_ID = "colour_animation_wheel"


def check_colour_animation_wheel(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        animated = animated_rgb_fixtures(graph, groups, function_id)
        if not animated:
            continue
        claimed: set[int] = set()
        for members in groups.values():
            if animated & set(members):
                claimed |= set(members)
        stuck = sorted(
            graph.capabilities[fixture_id].fixture.name
            for fixture_id in claimed
            if wheel_coloured_fixture(graph, fixture_id)
            and not wheel_animated(graph, groups, function_id, fixture_id)
        )
        if not stuck:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=caption,
                fixtures=tuple(stuck),
                message_id="colour_animation_wheel_stuck",
                fields={"animated": len(animated), "stuck": len(stuck)},
            )
        )
    return findings
