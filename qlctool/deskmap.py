"""The tablet desk's map, assembled from the saved workspace.

The desk validates this map against the console the master actually serves
before it enables a single control, so the map has to name what the console
will show: widget ids, function ids, action types, the solo frame each
button sits in. The rest - pages, captions, swatches, roles - is what the
desk draws, decided here beside the generator rather than by hand in the
desk's own repository, where it would drift from the show.
"""

import hashlib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from lxml import etree

from .capabilities_of import capabilities_of
from .checks.rule_desk_bursts import check_desk_bursts
from .checks.show_graph import build_show_graph, group_fixtures
from .desk_burst_buttons import desk_burst_buttons
from .desk_burst_identifier import desk_burst_identifier
from .desk_burst_note import desk_burst_note
from .desk_policy import (
    BURST_MS,
    PAGES,
    SAFETY_CAPTION_BY_FUNCTION,
    SAFETY_DETAIL_BY_FUNCTION,
    SAFETY_DETAIL_BY_ROLE,
    SECTION_ORDER,
    SECTION_TITLES,
    place,
    split_caption,
)
from .desk_swatch import swatches
from .desk_widgets import DeskWidget, desk_widgets
from .leading_glyph import leading_glyph
from .library import FixtureLibrary
from .names.names import Names
from .names.shipped_names import shipped_names
from .names.workspace_language import workspace_language
from .slug import slugify
from .speed_multiplier import multiplier
from .workspace import Workspace
from .xmlutil import find_local, findall_local

SCHEMA = 2
GENERATOR = "qlctool deskmap"
TARGET_QLC = "5.2.2"


def build_deskmap(
    workspace: Workspace, library: FixtureLibrary, path: str | Path, names: Names | None = None
) -> dict[str, Any]:
    """The desk's map; with no `names`, in the language the workspace was generated in."""
    root = workspace.root
    vocabulary = shipped_names(workspace_language(root)) if names is None else names
    capabilities = capabilities_of(root, library)
    graph = build_show_graph(root, capabilities)
    groups = group_fixtures(root)
    widgets = desk_widgets(root)
    frames = {w.id: w for w in widgets if w.kind in ("Frame", "SoloFrame")}
    burst_findings = check_desk_bursts(graph, root, vocabulary)
    if burst_findings:
        raise ValueError("invalid desk bursts: " + "; ".join(f.message for f in burst_findings))
    bursts = desk_burst_buttons(root, vocabulary)

    controls: dict[str, dict[str, Any]] = {}
    sections: dict[tuple[str, str], list[str]] = {}
    section_solo: dict[tuple[str, str], int | None] = {}
    for widget in widgets:
        function_name = graph.name(widget.function) if widget.function is not None else None
        function_kind = graph.kind(widget.function) if widget.function is not None else ""
        placement = place(widget, frames, function_name, function_kind, names=vocabulary)
        if placement is None:
            continue
        caption, detail = split_caption(widget.caption)
        # The console keeps the glyph in the caption; the desk gets it as a
        # field of its own, to draw at tile size (2026-09-22).
        icon, caption = leading_glyph(caption)
        if placement.role == "haze":
            # The section heading says HUMO; the tile says only the rhythm.
            for word in vocabulary.spellings("haze_word"):
                caption = caption.removeprefix(word + " ")
        key = _unique_key(controls, caption, widget.id)
        function = next(iter(vocabulary.lookup(function_name or "", ("functions",))), None)
        if function in SAFETY_DETAIL_BY_FUNCTION:
            # An empty detail is written as "", never null (ruling P8).
            words = SAFETY_DETAIL_BY_FUNCTION[function]
            detail = vocabulary.display(words) if words is not None else ""
        elif placement.role in SAFETY_DETAIL_BY_ROLE:
            detail = vocabulary.display(SAFETY_DETAIL_BY_ROLE[placement.role])
        if function in SAFETY_CAPTION_BY_FUNCTION:
            caption = vocabulary.display(SAFETY_CAPTION_BY_FUNCTION[function])
        controls[key] = {
            "widget": widget.id,
            "function": widget.function,
            "functionType": function_kind,
            "action": "toggle" if widget.action == "Toggle" else "flash",
            "caption": caption,
            "icon": icon,
            "detail": detail,
            "role": placement.role,
            "solo": widget.solo,
            "key": widget.key,
            "swatches": (
                swatches(graph, groups, widget.function) if widget.function is not None else []
            ),
            "enabled": placement.enabled,
            "reason": placement.reason,
        }
        if placement.role == "accent":
            burst = bursts[key][0]
            identifier = desk_burst_identifier(widget.caption, vocabulary)
            if identifier is None:
                # check_desk_bursts above already refused an accent it cannot name.
                raise ValueError(f"invalid desk bursts: {key} names no single accent")
            controls[key].update(
                {
                    "widget": burst.id,
                    "function": burst.function,
                    "functionType": "Chaser",
                    "action": "toggle",
                    "role": "burst",
                    "burstMs": BURST_MS[identifier],
                    "source": key,
                    "solo": burst.solo,
                    "key": burst.key,
                    "enabled": True,
                    "reason": "",
                }
            )
            note = desk_burst_note(identifier, vocabulary)
            if note is not None:
                controls[key]["burstNote"] = note
        where = (placement.page, placement.section)
        sections.setdefault(where, []).append(key)
        section_solo.setdefault(where, widget.solo)

    pages = []
    for page_key, title in PAGES:
        page_sections = sorted(
            (
                {
                    "key": section,
                    "title": vocabulary.display(SECTION_TITLES[section]),
                    "solo": section_solo[(page_key, section)],
                    "controls": keys,
                }
                for (page, section), keys in sections.items()
                if page == page_key
            ),
            key=lambda s: SECTION_ORDER.index(s["key"]),
        )
        if page_sections:
            pages.append(
                {"key": page_key, "title": vocabulary.display(title), "sections": page_sections}
            )

    stop_all = next((w for w in widgets if w.kind == "Button" and w.action == "StopAll"), None)
    grand_master = next(
        (w for w in widgets if w.kind == "Slider" and w.slider_mode == "GrandMaster"), None
    )
    dials: dict[str, dict[str, Any]] = {}
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


def _unique_key(existing: Mapping[str, object], caption: str, widget_id: int) -> str:
    key = slugify(caption)
    if key in existing:
        key = f"{key}-{widget_id}"
    return key


def _dial(root: etree._Element, widget: DeskWidget) -> dict[str, Any]:
    element = next(
        (
            e
            for e in root.iter()
            if e.attrib.get("ID") == str(widget.id) and e.tag.endswith("SpeedDial")
        ),
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
