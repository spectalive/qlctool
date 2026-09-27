"""Flash-button function ids a finger presses, not an audio bar."""

from collections.abc import Iterator

from lxml import etree

from ..find_local import find_local
from ..iter_local import iter_local
from ..vc.build_button import NO_FUNCTION
from .audio_pressed_widgets import audio_pressed_widgets
from .show_graph import ShowGraph


def hand_flash_scenes(graph: ShowGraph, console: etree._Element) -> Iterator[int]:
    """Scenes behind Flash buttons a finger presses, not an audio bar."""
    audio_pressed = audio_pressed_widgets(console)
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        if button.attrib.get("ID", "") in audio_pressed:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in seen:
            continue
        scene = graph.functions.get(function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue  # rule_flash_scene already reports that wiring
        seen.add(function_id)
        yield function_id
