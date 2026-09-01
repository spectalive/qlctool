"""An animation the chaser cuts off before it has finished.

An RGBMatrix does not run "for a while": it walks a fixed number of frames and
starts again, and how many depends on the script *and* on the grid it paints.
Fill on an eight-wide bar is eight frames; Waves on the same bar is twelve. A
chaser holding such a matrix for less than that stops it wherever it had got
to, which on Fill means the bar lights half way, jumps to another colour, and
lights half way again, all night.

The owner found it before this check did: "la barra led empezamos con una
animacion pero nunca la terminamos" (2026-08-26). It is also half of why the
pixels read as off - an animation cut in its first half is an animation seen
mostly dark.

A function on **Beats** tempo is skipped: its numbers are thousandths of a
beat, not milliseconds, and how long a beat lasts is the room's business.
"""

from ..matrix_step_count import matrix_step_count
from ..xmlutil import find_local, findall_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "efecto cortado"
BEATS = "Beats"


def check_unfinished_effects(graph: ShowGraph, groups, entries) -> list[Finding]:
    del groups, entries
    findings: list[Finding] = []
    for function_id, function in sorted(graph.functions.items()):
        if function.attrib.get("Type") != "Chaser" or _on_beats(function):
            continue
        cut = _cut_steps(graph, function)
        if not cut:
            continue
        worst = max(cut, key=lambda item: item[2] - item[1])
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    f"corta {len(cut)} de sus efectos antes de que terminen: "
                    f"«{worst[0]}» necesita {worst[2]} ms para una pasada completa "
                    f"y solo tiene {worst[1]} ms"
                ),
            )
        )
    return findings


def _cut_steps(graph: ShowGraph, chaser) -> list[tuple[str, int, int]]:
    cut: list[tuple[str, int, int]] = []
    for step in findall_local(chaser, "Step"):
        if not (step.text or "").strip().isdigit():
            continue
        matrix = graph.functions.get(int(step.text))
        if matrix is None or matrix.attrib.get("Type") != "RGBMatrix":
            continue
        if _on_beats(matrix):
            continue
        needed = _one_pass(matrix, graph.grids)
        hold = int(step.attrib.get("Hold", 0))
        if needed and hold < needed:
            cut.append((matrix.attrib.get("Name", ""), hold, needed))
    return cut


def _one_pass(matrix, grids) -> int:
    """Milliseconds one full pass of this matrix takes on its own group."""
    speed = find_local(matrix, "Speed")
    group = find_local(matrix, "FixtureGroup")
    if speed is None or group is None or not (group.text or "").isdigit():
        return 0
    algorithm = find_local(matrix, "Algorithm")
    name = None if algorithm is None else (algorithm.text or None)
    width, height = grids.get(int(group.text), (1, 1))
    return int(speed.attrib.get("Duration", 0)) * matrix_step_count(name, width, height)


def _on_beats(function) -> bool:
    tempo = find_local(function, "Tempo")
    return tempo is not None and (tempo.text or "").strip() == BEATS
