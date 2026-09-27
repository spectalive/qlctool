"""Scene id -> the longest fade-in it is started with, its own included."""

from ..findall_local import findall_local
from .chaser_speed_mode import chaser_speed_mode
from .own_fade_in import own_fade_in
from .scenes_under import scenes_under
from .show_graph import ShowGraph


def fade_of_every_scene(graph: ShowGraph) -> dict[int, int]:
    fades: dict[int, int] = {}
    for function_id, function in graph.functions.items():
        kind = function.attrib.get("Type")
        if kind == "Scene":
            fades[function_id] = max(fades.get(function_id, 0), own_fade_in(function))
        elif kind == "Chaser":
            common = own_fade_in(function)
            per_step = chaser_speed_mode(function) == "PerStep"
            for step in findall_local(function, "Step"):
                if not (step.text and step.text.strip().isdigit()):
                    continue
                target = int(step.text)
                fade = int(step.attrib.get("FadeIn", "0")) if per_step else common
                # A Collection in between changes nothing: `Collection::write`
                # hands the chaser's override fade to every member.
                for scene_id in scenes_under(graph, target):
                    fades[scene_id] = max(fades.get(scene_id, 0), fade)
    return fades
