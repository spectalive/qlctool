"""A state that colours a fixture at some instant and opens its dimmer at none.

`intensidad` merges everything a state can drive and asks whether *something*
opens each coloured fixture. Merged, `AUTO` opens the four vertical fog
machines' LEDs - `Intensidad Ambiente` and `Intensidad Total` write their
dimmer at 255. But those are two of the four energy levels. `Nivel Peak` and
`Nivel Fiesta Dinamico` carry `Intensidad Peak`, which wrote the pump shut and
nothing else on those machines, and the dimmer chase has no EFX for them: for
those levels, and for the whole of `Momento Locura`, the wheel painted the
four columns and their dimmer - Intensity, zeroed every cycle - stayed at 0
(cross-audit, 2026-09-02; the montage note of 2026-08-29 wants them to "subir
y bajar con los niveles").

So the question is asked per instant, the way `unowned_instant` asks it of the
strobe channels: is there a reachable instant of this state where the fixture
is coloured and no member writes its dimmer? A fixture with no dimmer role is
`intensidad`'s business (its shutter); a fixture whose dimmer is only ever
opened by an effect counts as open, because the effect writes it every cycle.
"""

from .finding import ERROR, Finding
from .instant_dark_fixtures import instant_dark_fixtures
from .instant_evaluator import InstantEvaluator
from .show_graph import ShowGraph

RULE = "color sin dimmer en algun instante"


def check_instant_dimmer(graph: ShowGraph, groups, states: set[int]) -> list[Finding]:
    evaluator = InstantEvaluator(graph, groups)
    findings: list[Finding] = []
    for state_id in sorted(states):
        dark = instant_dark_fixtures(graph, groups, (state_id,), evaluator=evaluator)
        if not dark:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(state_id),
                fixtures=tuple(sorted(dark)),
                message=(
                    f"en algun instante suyo pone color a {len(dark)} aparatos "
                    f"y ningun miembro escribe su dimmer: el dimmer es Intensity, "
                    f"QLC+ lo pone a cero cada ciclo, y el aparato esta coloreado "
                    f"en los datos y apagado en la sala"
                ),
            )
        )
    return findings
