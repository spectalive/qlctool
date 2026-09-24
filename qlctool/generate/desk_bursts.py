"""Append independent SingleShot cues and their validation buttons for the desk."""

from copy import deepcopy

from ..desk_burst_duration import desk_burst_duration
from ..desk_burst_sources import desk_burst_sources
from ..desk_policy import BURST_FRAME, split_caption
from ..functions.chaser import build_chaser
from ..ids import next_function_id
from ..names.default_names import default_names
from ..vc.button import build_button
from ..vc.frame import build_frame
from ..vc.label import build_label
from ..vc.widget_ids import next_widget_id
from ..workspace import Workspace
from ..xmlutil import find_local, iter_local
from .live_console import HELP_FONT, PAGE_CONTROL, SMALL_FONT


def generate_desk_bursts(workspace: Workspace) -> list[int]:
    sources = desk_burst_sources(workspace.root)
    if not sources:
        return []
    functions = {int(f.get("ID")): f for f in workspace.engine if f.get("Type")}
    outer = next(
        f for f in iter_local(workspace.root, "Frame") if find_local(f, "Multipage") is not None
    )
    notes = build_label(
        outer,
        next_widget_id(workspace.root),
        "Tablet: ráfagas con límite; soltar las para antes. Colores pueden mezclarse.",
        8,
        68,
        524,
        22,
        font=HELP_FONT,
    )
    notes.set("Page", str(PAGE_CONTROL))
    frame = build_frame(
        outer,
        next_widget_id(workspace.root),
        BURST_FRAME,
        8,
        96,
        524,
        114,
        font=SMALL_FONT,
    )
    frame.set("Page", str(PAGE_CONTROL))
    button_ids = []
    for index, (key, source) in enumerate(sources.items()):
        duration = desk_burst_duration(source, default_names())
        if duration is None or duration <= 0:
            raise ValueError(f"burst duration must be positive: {key}")
        original = functions[source.function]
        if original.get("Type") != "Scene":
            raise ValueError(f"desk accent must drive a Scene: {key}")
        caption = split_caption(source.caption)[0]
        scene = deepcopy(original)
        scene_id = next_function_id(workspace.root)
        scene.set("ID", str(scene_id))
        scene.set("Name", f"Desk · {caption} (ráfaga)")
        scene.set("Path", "Desk")
        workspace.add_function(scene)
        chaser_id = next_function_id(workspace.root)
        chaser = build_chaser(
            chaser_id,
            f"Desk · {caption} ráfaga {duration / 1000:g} s",
            [scene_id],
            hold=duration,
            run_order="SingleShot",
            path="Desk",
        )
        find_local(chaser, "SpeedModes").set("Duration", "PerStep")
        workspace.add_function(chaser)
        widget_id = next_widget_id(workspace.root)
        build_button(
            frame,
            widget_id,
            caption,
            chaser_id,
            6 + (index % 6) * 86,
            26 + (index // 6) * 28,
            82,
            24,
            font=SMALL_FONT,
        )
        button_ids.append(widget_id)
    return button_ids
