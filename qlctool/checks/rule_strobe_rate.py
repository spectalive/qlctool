"""A strobe flashing faster than a public room is allowed to flash.

`Strobo Rapido` shipped for weeks alternating the whole rig between white and
black every 50 ms - ten flashes a second, found in the Codex review of
2026-08-27, and nobody had asked whether that was safe. It is not: repetitive
flashing between 3 and 30 Hz is the photosensitive-epilepsy trigger band, and
UK guidance for public performance caps effect lighting at four flashes per
second. A generator can produce any rate with equal ease, so the cap has to be
a rule, not a habit.

The rate is read off the function's shape by `strobe_shape` - what it writes
and how fast it alternates - never off its name, and the cap applies to every
function in the file: a strobe nobody wired to a button today is one somebody
wires tomorrow.
"""

from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .strobe_shape import strobe_flash_rate

RULE = "estrobo demasiado rapido"
MAX_FLASH_HZ = 4.0


def check_strobe_rate(graph: ShowGraph, groups, entries) -> list[Finding]:
    del entries
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        rate = strobe_flash_rate(graph, groups, function_id)
        if rate is None or rate <= MAX_FLASH_HZ:
            continue
        findings.append(Finding(
            rule=RULE,
            severity=ERROR,
            function=graph.name(function_id),
            message=(
                f"parpadea a {rate:.1f} Hz; por encima de {MAX_FLASH_HZ:.0f} Hz "
                f"entra en la banda de riesgo de epilepsia fotosensible - la "
                f"guia britanica de espectaculos corta en 4 por segundo"
            ),
        ))
    return findings
