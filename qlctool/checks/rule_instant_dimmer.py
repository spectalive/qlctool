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

from .. import roles
from .color_roles import COLOUR
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit, reach
from .unowned_instant import unowned_while_lit

RULE = "color sin dimmer en algun instante"


def check_instant_dimmer(graph: ShowGraph, groups, states: set[int]) -> list[Finding]:
    findings: list[Finding] = []
    for state_id in sorted(states):
        dark: list[str] = []
        for fixture_id, written in reach(graph, groups, state_id).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or (capability.is_smoke and not capability.is_lit_smoke):
                continue
            dimmers = capability.offsets_for_role(roles.DIMMER)
            coloured = tuple(
                offset
                for role in COLOUR
                for offset in capability.offsets_for_role(role)
                if offset in written and lit(written[offset])
            )
            if not dimmers or not coloured:
                continue
            if unowned_while_lit(
                graph, groups, state_id, fixture_id, frozenset(dimmers), coloured
            ):
                dark.append(capability.fixture.name)
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
