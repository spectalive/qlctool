"""A chaser counting beats while its steps count milliseconds.

2026-08-29: "las cabezas van super rapido a 120bpm y no completan los giros".
The movement chasers had been switched to Beats tempo, so their crossfade read
`10000` - ten beats. A chaser hands that number straight to whatever it starts
(`ChaserRunner::startNewStep` -> `Function::start(..., overrideFadeIn, ...)`),
and an EFX subtracts it from its own duration to get the loop it draws:

    EFX::loopDuration() = duration() - overrideFadeInSpeed()

The EFX counts milliseconds and knows nothing about beats, so a 16 s head
sweep became 16000 - 10000 = 6 s. Two and a half times too fast, and the shape
never closed.

The rule: a function in Beats tempo with a non-zero fade may only drive steps
that have no clock of their own. A Scene is safe - it is a set of values. An
EFX draws a figure over a duration in milliseconds and an RGBMatrix runs an
animation on a millisecond frame clock; handing either a number that means
beats corrupts it silently, and the room is the only place it shows.

Tempo is read off the function's own `<Tempo>`, never off a name, and the step
kinds off the graph.
"""

from ..xmlutil import find_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "unidades de tempo cruzadas"
COLLECTION_RULE = "tempo en una coleccion"

TEMPO_BEATS = "Beats"
# Function kinds that time themselves in milliseconds whatever their parent
# is counting in.
SELF_TIMED = ("EFX", "RGBMatrix")


def check_tempo_units(graph: ShowGraph) -> list[Finding]:
    findings: list[Finding] = []
    for function_id in sorted(graph.functions):
        function = graph.functions[function_id]
        tempo = find_local(function, "Tempo")
        if tempo is None or (tempo.text or "").strip() != TEMPO_BEATS:
            continue

        if function.attrib.get("Type") == "Collection":
            findings.append(
                Finding(
                    rule=COLLECTION_RULE,
                    severity=ERROR,
                    function=graph.name(function_id),
                    message=(
                        "es una coleccion y lleva <Tempo>: una coleccion no tiene "
                        "tempo propio, arranca a sus miembros y ya - QLC+ lo dice "
                        "al cargar («Unknown collection tag: Tempo») y lo ignora, "
                        "asi que esa capa se queda en el reloj sin avisar"
                    ),
                )
            )
            continue

        fade = _fade(function)
        if fade == 0:
            continue
        hurt = sorted(
            {
                graph.name(member)
                for member in graph.members.get(function_id, ())
                if graph.kind(member) in SELF_TIMED
            }
        )
        if not hurt:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                fixtures=tuple(hurt),
                message=(
                    f"va en Beats con un fundido de {fade} y arranca "
                    f"{len(hurt)} funciones que se cronometran en milisegundos: "
                    f"el chaser les pasa ese numero tal cual y un EFX se lo resta "
                    f"a su duracion (EFX::loopDuration), asi que dibujan su "
                    f"figura mucho mas rapido y no la cierran"
                ),
            )
        )
    return findings


def _fade(function) -> int:
    speed = find_local(function, "Speed")
    if speed is None:
        return 0
    return max(int(speed.attrib.get("FadeIn", 0)), int(speed.attrib.get("FadeOut", 0)))
