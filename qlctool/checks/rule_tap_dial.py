"""A tap that flattens every programme to one length.

2026-08-29, the owner on the speed dials: "eso no funciona bien, nunca ha
funcionado bien ... se vuelven todos los programas locos". A tap dial writes
`dial time x multiplier` into each function it lists
(`VCSpeedDial::applyFunctionsTime`), so the multiplier is where a layer states
how long it is in taps. Give every layer the same multiplier and one tap makes
the colour wheel, the prism and the dimmer pulse exactly as long as each
other - the show collapses to one length, which is what "locos" looked like.

The rule reads the wiring: a dial that can be tapped and gives one multiplier
to everything under it is flattening the show. Two functions may honestly share
a multiplier; a whole console cannot.

The second half is the tap that does nothing at all. A dial with a tap key and
no functions under it re-times nothing on this QLC+: the `ControlBPM` tap that
would drive the global BPM instead is not in 5.2.2 - it says so when it loads
one ("Unknown speed dial tag: ControlBPM", read out of the show Mac's own log
the same night) - so a bound tap key needs functions to write into.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local
from .finding import ERROR, Finding

RULE = "tap que aplana los programas"
EMPTY_RULE = "tap que no re-tempa nada"

TAP_CONTROL_ID = "1"
# Below this many functions, one shared multiplier is a coincidence rather
# than a flattened console.
FLATTENING_FROM = 3


def check_tap_dial(root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for dial in iter_local(console, "SpeedDial"):
        if not _has_tap_binding(dial):
            continue
        caption = dial.attrib.get("Caption", "SpeedDial")
        multipliers = [
            function.attrib.get("Duration", "0")
            for function in findall_local(dial, "Function")
        ]
        if not multipliers and _controls_bpm(dial):
            continue  # the `--bpm-tap` build: its tap drives the global BPM
        if not multipliers:
            findings.append(Finding(
                rule=EMPTY_RULE,
                severity=ERROR,
                function=caption,
                message=(
                    "tiene tecla de tap y no lista ninguna funcion: en QLC+ "
                    "5.2.2 el tap solo escribe en las funciones del dial "
                    "(«Unknown speed dial tag: ControlBPM» al cargar), asi "
                    "que asi no re-tempa nada"
                ),
            ))
            continue
        if len(multipliers) >= FLATTENING_FROM and len(set(multipliers)) == 1:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=caption,
                message=(
                    f"re-tempa {len(multipliers)} funciones con el mismo "
                    f"multiplicador: un tap las deja a todas de la misma "
                    f"duracion (VCSpeedDial::applyFunctionsTime escribe "
                    f"tiempo x multiplicador) - cada capa tiene que decir "
                    f"cuantos taps dura"
                ),
            ))
    return findings


def _has_tap_binding(dial: etree._Element) -> bool:
    return any(
        source.attrib.get("ID") == TAP_CONTROL_ID
        for source in findall_local(dial, "Input")
    )


def _controls_bpm(dial: etree._Element) -> bool:
    """The dial taps the global BPM rather than writing into functions.

    Only a QLC+ newer than the 5.2.2 this show runs honours it, which is why
    `qlctool newshow --bpm-tap` is a build of its own rather than the default.
    """
    control = find_local(dial, "ControlBPM")
    return control is not None and (control.text or "").strip() == "True"
