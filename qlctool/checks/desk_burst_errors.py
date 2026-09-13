"""Prove one cue has a fixed clock and exclusive ownership of its scene."""

from lxml import etree

from ..desk_widgets import DeskWidget
from ..generate.live_console import PAGE_CONTROL
from ..xmlutil import find_local, findall_local, iter_local
from .show_graph import ShowGraph


def desk_burst_errors(
    graph: ShowGraph,
    root: etree._Element,
    source: DeskWidget,
    button: DeskWidget,
    duration: int,
) -> list[str]:
    errors = []
    if button.action != "Toggle" or button.page != PAGE_CONTROL or button.solo is not None:
        errors.append("requiere un Toggle independiente en CONTROL")
    chaser = graph.functions.get(button.function)
    if chaser is None or graph.kind(button.function) != "Chaser":
        return errors + ["el boton no apunta a un Chaser"]
    for tag, expected in (("RunOrder", "SingleShot"), ("Direction", "Forward")):
        element = find_local(chaser, tag)
        if element is None or element.text != expected:
            errors.append(f"{tag} debe ser {expected}")
    modes = find_local(chaser, "SpeedModes")
    if modes is None or dict(modes.attrib) != {
        "FadeIn": "Common",
        "FadeOut": "Common",
        "Duration": "PerStep",
    }:
        errors.append("SpeedModes debe fijar Duration=PerStep y fundidos Common")
    speed = find_local(chaser, "Speed")
    if speed is None or speed.get("FadeIn") != "0" or speed.get("FadeOut") != "0":
        errors.append("los fundidos comunes deben ser cero")
    tempo = find_local(chaser, "Tempo")
    if tempo is not None and tempo.text != "Time":
        errors.append("el reloj debe contar milisegundos")
    steps = findall_local(chaser, "Step")
    if len(steps) != 1:
        return errors + ["requiere exactamente un paso"]
    step = steps[0]
    if duration <= 0 or any(
        step.get(k) != v
        for k, v in {
            "Number": "0",
            "Hold": str(duration),
            "FadeIn": "0",
            "FadeOut": "0",
        }.items()
    ):
        errors.append(f"el paso debe durar {duration} ms sin fundidos")
    try:
        scene_id = int(step.text or "")
    except ValueError:
        return errors + ["el paso no referencia una escena"]
    scene = graph.functions.get(scene_id)
    original = graph.functions.get(source.function)
    if (
        scene is None
        or original is None
        or graph.kind(scene_id) != "Scene"
        or graph.kind(source.function) != "Scene"
    ):
        return errors + ["el paso y su origen deben ser escenas"]
    scene_values = sorted((v.get("ID"), v.text) for v in findall_local(scene, "FixtureVal"))
    original_values = sorted((v.get("ID"), v.text) for v in findall_local(original, "FixtureVal"))
    if scene_id == source.function or scene_values != original_values:
        errors.append("el paso debe ser una copia privada con los mismos FixtureVal")
    parents = {fid for fid, members in graph.members.items() if scene_id in members}
    if parents != {button.function}:
        errors.append("otra funcion referencia la escena privada")
    if any(button.function in members for members in graph.members.values()):
        errors.append("otra funcion puede arrancar la rafaga automaticamente")
    console = find_local(root, "VirtualConsole")
    references = list(iter_local(console, "Function")) if console is not None else []
    # Sliders, cue lists and speed dials also carry Function references.
    # A second writer or clock must not hide outside the button-only map.
    targets = [f.get("ID", (f.text or "").strip()) for f in references]
    if str(scene_id) in targets:
        errors.append("un widget referencia directamente la escena privada")
    if targets.count(str(button.function)) != 1:
        errors.append("la rafaga debe tener un unico boton y ningun otro control")
    return errors
