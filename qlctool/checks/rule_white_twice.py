"""A tinted colour whose white share is paid twice: by the RGB and by the White.

`rule_white_emitter` made every colour scene speak to the white LED. It did not
say what to say, and the first answer - `min(r, g, b)` beside an untouched RGB -
put the achromatic part of the colour on four emitters instead of one. The
fixture then adds them: a warm (255, 214, 170) plus W170 leaves the tint
somewhere under a wall of white, which is how `Luz Charla` and `Blanco Total`
became the same light to the eye ("charla y blanco son lo mismo", owner,
2026-09-22), and why the colour hits read as "mezclados con blanco".

The rule reasons about the values, never about a function's name: on a fixture
with a white emitter, a scene that drives White above zero must have taken that
share out of red, green and blue - so the minimum of the three is zero. The one
colour allowed to keep all four emitters up is the one that has no hue to lose:
r == g == b, the greys and the full white the work light and the flashes are
for. Anything in between is a tint being washed out.
"""

from .. import roles
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE_ID = "white_twice"
RGB = (roles.RED, roles.GREEN, roles.BLUE)


def check_white_twice(graph: ShowGraph, groups: dict[int, tuple[int, ...]]) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") != "Scene":
            continue
        washed: list[str] = []
        for fixture_id, written in driven_channels(function, graph.capabilities, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            # A Scene writes a number to every channel it names: no None here.
            whites = [
                value
                for offset in capability.offsets_for_role(roles.WHITE)
                if offset in written and (value := written[offset]) is not None
            ]
            if not whites or max(whites) == 0:
                continue
            stated = []
            for role in RGB:
                values = [
                    value
                    for offset in capability.offsets_for_role(role)
                    if offset in written and (value := written[offset]) is not None
                ]
                if values:
                    stated.append(max(values))
            if len(stated) < 3:
                continue
            if min(stated) == 0 or len(set(stated)) == 1:
                continue
            washed.append(capability.fixture.name)
        if not washed:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=graph.name(function_id),
                fixtures=tuple(sorted(set(washed))),
                message=(
                    f"manda el emisor White y deja el blanco tambien dentro del RGB "
                    f"en {len(set(washed))} aparatos: la parte acromatica del color "
                    f"sale por cuatro LED en vez de uno y el tinte se lava"
                ),
            )
        )
    return findings
