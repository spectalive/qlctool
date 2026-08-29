"""A tap that rewrites the programmes instead of setting the tempo.

2026-08-29, the owner on the speed dials: "eso no funciona bien, nunca ha
funcionado bien ... se vuelven todos los programas locos". The mechanism is in
qmlui's own code: `VCSpeedDial::tap()` calls `setCurrentTime`, which calls
`applyFunctionsTime`, which writes the raw tap interval into the duration of
EVERY function the dial lists - tapping a 500 ms beat put wheels built for
1900 ms holds on 500 ms flat, persistently, and `ControlBPM` does not skip
that write. The working shape is the opposite: the tap dial lists no
functions and controls the global BPM, and the layers that follow the music
count in Beats.

Two rules, the two halves of that shape:

- A dial with a tap binding (a key or an external control on input 1) must
  list no functions: every listed one gets its duration stomped on the first
  tap.
- A dial that controls the BPM needs a clock to set and someone listening: a
  beat generator that is not Disabled, and at least one function in Beats
  tempo. Without either, the tap sets a number nothing reads.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "tap que pisa duraciones"
CLOCK_RULE = "tap sin reloj que gobernar"

TAP_CONTROL_ID = "1"


def check_tap_dial(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    findings: list[Finding] = []
    for dial in iter_local(console, "SpeedDial"):
        caption = dial.attrib.get("Caption", "SpeedDial")
        bound = findall_local(dial, "Function")
        if _has_tap_binding(dial) and bound:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=caption,
                message=(
                    f"tiene tap y lista {len(bound)} funciones: cada tap "
                    f"escribe el intervalo crudo como duracion en todas "
                    f"(qmlui VCSpeedDial::tap -> applyFunctionsTime) - un "
                    f"dial con tap gobierna el BPM global y no lista nada"
                ),
            ))
        if _controls_bpm(dial):
            if not _beat_generator_on(root):
                findings.append(Finding(
                    rule=CLOCK_RULE,
                    severity=ERROR,
                    function=caption,
                    message=(
                        "gobierna el BPM pero el generador de beat esta en "
                        "Disabled: el tap fija un numero que ningun reloj "
                        "lee"
                    ),
                ))
            if not _any_beats_function(graph):
                findings.append(Finding(
                    rule=CLOCK_RULE,
                    severity=ERROR,
                    function=caption,
                    message=(
                        "gobierna el BPM pero ninguna funcion del show va "
                        "en tempo Beats: el tap no mueve nada"
                    ),
                ))
    return findings


def _has_tap_binding(dial: etree._Element) -> bool:
    for source in findall_local(dial, "Input"):
        if source.attrib.get("ID") == TAP_CONTROL_ID:
            return True
    return False


def _controls_bpm(dial: etree._Element) -> bool:
    control = find_local(dial, "ControlBPM")
    return control is not None and (control.text or "").strip() == "True"


def _beat_generator_on(root: etree._Element) -> bool:
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    generator = find_local(io_map, "BeatGenerator") if io_map is not None else None
    if generator is None:
        return False
    return generator.attrib.get("BeatType", "Disabled") != "Disabled"


def _any_beats_function(graph: ShowGraph) -> bool:
    for function in graph.functions.values():
        tempo = find_local(function, "Tempo")
        if tempo is not None and (tempo.text or "").strip() == "Beats":
            return True
    return False
