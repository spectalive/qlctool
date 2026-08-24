"""Lay out Virtual Console buttons for a set of functions, grouped and ordered.

Clicking two hundred buttons into place is the other half of the manual work.
This takes the functions a generator just created, groups them by the UI folder
they were filed under, and builds one solo frame per group with the buttons in a
tidy grid - below whatever the console already holds, so an existing layout is
never disturbed.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from lxml import etree

from ..argb import argb_from_rgb
from ..palette import PALETTE
from ..vc.appearance import DEFAULT
from ..vc.button import build_button
from ..vc.solo_frame import build_solo_frame
from ..vc.widget_ids import next_widget_id
from ..workspace import Workspace
from ..xmlutil import find_local, localname

BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
PADDING = 6
HEADER = 26


@dataclass(frozen=True)
class GeneratedLayout:
    frame_ids: list[int]
    button_ids: list[int]


def generate_vc_layout(
    workspace: Workspace,
    function_ids: Sequence[int] | None = None,
    columns: int = 6,
    color_by_name: bool = True,
    action: str = "Toggle",
    keys: dict[int, str] | None = None,
    actions: dict[int, str] | None = None,
) -> GeneratedLayout:
    """Add one solo frame per function group, with a button per function.

    function_ids selects what to expose; by default every function that has a
    Path (the UI folder QLC+ shows), which is exactly what the generators tag.
    Functions are grouped by that Path and ordered by name inside each group.
    keys and actions override the keyboard shortcut and the Toggle/Flash mode
    per function - the show's flash buttons live on Space and ".".
    """
    engine = workspace.engine
    functions = [f for f in engine if localname(f) == "Function"]
    if function_ids is not None:
        wanted = {str(i) for i in function_ids}
        functions = [f for f in functions if f.attrib.get("ID") in wanted]
    else:
        functions = [f for f in functions if f.attrib.get("Path")]
    if not functions:
        raise ValueError("no functions to lay out")

    groups: dict[str, list[etree._Element]] = {}
    for function in functions:
        key = function.attrib.get("Path") or function.attrib.get("Type", "Otros")
        groups.setdefault(key, []).append(function)

    console_frame = _console_frame(workspace.root)
    y = _first_free_y(console_frame) + PADDING

    frame_ids: list[int] = []
    button_ids: list[int] = []
    for caption in sorted(groups):
        members = sorted(groups[caption], key=lambda f: f.attrib.get("Name", ""))
        rows = (len(members) + columns - 1) // columns
        width = PADDING + columns * (BUTTON_WIDTH + PADDING)
        height = HEADER + PADDING + rows * (BUTTON_HEIGHT + PADDING)

        frame_id = next_widget_id(workspace.root)
        frame = build_solo_frame(
            console_frame, frame_id, caption, PADDING, y, width, height
        )
        frame_ids.append(frame_id)

        for index, function in enumerate(members):
            column, row = index % columns, index // columns
            button_id = next_widget_id(workspace.root)
            build_button(
                frame,
                button_id,
                function.attrib.get("Name", ""),
                int(function.attrib["ID"]),
                x=PADDING + column * (BUTTON_WIDTH + PADDING),
                y=HEADER + row * (BUTTON_HEIGHT + PADDING),
                width=BUTTON_WIDTH,
                height=BUTTON_HEIGHT,
                action=(actions or {}).get(int(function.attrib["ID"]), action),
                key=(keys or {}).get(int(function.attrib["ID"])),
                background=_background_for(function, color_by_name),
            )
            button_ids.append(button_id)

        y += height + PADDING

    _grow_console(workspace.root, y)
    return GeneratedLayout(frame_ids=frame_ids, button_ids=button_ids)


def _console_frame(root: etree._Element) -> etree._Element:
    console = find_local(root, "VirtualConsole")
    if console is None:
        raise ValueError("workspace has no <VirtualConsole>")
    frame = find_local(console, "Frame")
    if frame is None:
        raise ValueError("Virtual Console has no root <Frame>")
    return frame


def _first_free_y(frame: etree._Element) -> int:
    """The Y below every widget already placed in the console's root frame."""
    bottom = 0
    for child in frame:
        state = find_local(child, "WindowState")
        if state is None:
            continue
        bottom = max(
            bottom,
            int(state.attrib.get("Y", "0")) + int(state.attrib.get("Height", "0")),
        )
    return bottom


def _background_for(function: etree._Element, color_by_name: bool) -> str:
    """Colour a button by the palette colour its function is named after."""
    if not color_by_name:
        return DEFAULT
    name = function.attrib.get("Name", "")
    for color_name, rgb in PALETTE.items():
        if name.endswith(color_name):
            return str(argb_from_rgb(rgb))
    return DEFAULT


def _grow_console(root: etree._Element, needed_height: int) -> None:
    """Keep the console canvas at least as tall as what we just laid out."""
    console = find_local(root, "VirtualConsole")
    properties = find_local(console, "Properties")
    if properties is None:
        return
    size = find_local(properties, "Size")
    if size is None:
        return
    if int(size.attrib.get("Height", "0")) < needed_height:
        size.set("Height", str(needed_height))
