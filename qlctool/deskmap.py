"""The tablet desk's map, assembled from the saved workspace.

The desk validates this map against the console the master actually serves
before it enables a single control, so the map has to name what the console
will show: widget ids, function ids, action types, the solo frame each
button sits in. The rest - pages, captions, swatches, roles - is what the
desk draws, decided here beside the generator rather than by hand in the
desk's own repository, where it would drift from the show.
"""

import hashlib
from pathlib import Path

from .capabilities_of import capabilities_of
from .checks.show_graph import build_show_graph, group_fixtures
from .desk_policy import PAGES, SECTION_ORDER, SECTION_TITLES, place, split_caption
from .desk_swatch import swatches
from .desk_widgets import desk_widgets
from .library import FixtureLibrary
from .slug import slugify
from .speed_multiplier import multiplier
from .workspace import Workspace
from .xmlutil import find_local, findall_local

SCHEMA = 2
GENERATOR = "qlctool deskmap"
TARGET_QLC = "5.2.2"


def build_deskmap(workspace: Workspace, library: FixtureLibrary, path: str | Path) -> dict:
    root = workspace.root
    capabilities = capabilities_of(root, library)
    graph = build_show_graph(root, capabilities)
    groups = group_fixtures(root)
    widgets = desk_widgets(root)
    frames = {w.id: w for w in widgets if w.kind in ("Frame", "SoloFrame")}

    controls: dict[str, dict] = {}
    sections: dict[tuple[str, str], list[str]] = {}
    section_solo: dict[tuple[str, str], int | None] = {}
    for widget in widgets:
        function_name = graph.name(widget.function) if widget.function is not None else None
        placement = place(widget, frames, function_name, graph.kind(widget.function))
        if placement is None:
            continue
        caption, detail = split_caption(widget.caption)
        key = _unique_key(controls, caption, widget.id)
        controls[key] = {
            "widget": widget.id,
            "function": widget.function,
            "functionType": graph.kind(widget.function),
            "action": "toggle" if widget.action == "Toggle" else "flash",
            "caption": caption,
            "detail": detail,
            "role": placement.role,
            "solo": widget.solo,
            "key": widget.key,
            "swatches": swatches(graph, groups, widget.function),
            "enabled": placement.enabled,
            "reason": placement.reason,
        }
        where = (placement.page, placement.section)
        sections.setdefault(where, []).append(key)
        section_solo.setdefault(where, widget.solo)

    pages = []
    for page_key, title in PAGES:
        page_sections = sorted(
            (
                {
                    "key": section,
                    "title": SECTION_TITLES[section],
                    "solo": section_solo[(page_key, section)],
                    "controls": keys,
                }
                for (page, section), keys in sections.items()
                if page == page_key
            ),
            key=lambda s: SECTION_ORDER.index(s["key"]),
        )
        if page_sections:
            pages.append({"key": page_key, "title": title, "sections": page_sections})

    stop_all = next((w for w in widgets if w.kind == "Button" and w.action == "StopAll"), None)
    grand_master = next(
        (w for w in widgets if w.kind == "Slider" and w.slider_mode == "GrandMaster"), None
    )
    dials = {}
    for widget in widgets:
        if widget.kind != "SpeedDial":
            continue
        dials[_unique_key(dials, widget.caption, widget.id)] = _dial(root, widget)

    path = Path(path)
    return {
        "schema": SCHEMA,
        "generator": GENERATOR,
        "qlcVersion": TARGET_QLC,
        "show": {
            "key": slugify(path.stem),
            "workspace": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else "",
        },
        "grandMaster": {"widget": grand_master.id} if grand_master else None,
        "stopAll": {"widget": stop_all.id, "fadeOutMs": stop_all.fade_out_ms} if stop_all else None,
        "pages": pages,
        "controls": controls,
        "dials": dials,
    }


def _unique_key(existing: dict, caption: str, widget_id: int) -> str:
    key = slugify(caption)
    if key in existing:
        key = f"{key}-{widget_id}"
    return key


def _dial(root, widget) -> dict:
    element = next(
        (e for e in root.iter() if e.attrib.get("ID") == str(widget.id) and e.tag.endswith("SpeedDial")),
        None,
    )
    members = []
    time_ms = 0
    if element is not None:
        time_element = find_local(element, "Time")
        time_ms = int((time_element.text or "0").strip()) if time_element is not None else 0
        for function in findall_local(element, "Function"):
            members.append(
                {
                    "function": int((function.text or "-1").strip()),
                    "fadeIn": multiplier(int(function.attrib.get("FadeIn", 0))),
                    "fadeOut": multiplier(int(function.attrib.get("FadeOut", 0))),
                    "duration": multiplier(int(function.attrib.get("Duration", 0))),
                }
            )
    return {
        "widget": widget.id,
        "caption": split_caption(widget.caption)[0],
        "key": widget.key,
        "timeMs": time_ms,
        "members": members,
    }
