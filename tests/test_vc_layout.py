"""Virtual Console layout: buttons for generated functions, grouped and placed.

Checks the two things that make a layout usable rather than merely valid - every
function gets exactly one button, and the new frames land below whatever the
console already holds - and then has QLC+ itself load the result.
"""

from pathlib import Path

import pytest

from qlctool.argb import argb_from_rgb
from qlctool.generate.color_palette import generate_color_palette
from qlctool.generate.movement_efx import generate_movement_efx
from qlctool.generate.vc_layout import generate_vc_layout
from qlctool.library import FixtureLibrary
from qlctool.validate import qlcplus_binary, validate_workspace
from qlctool.vc.widget_ids import existing_widget_ids
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _console_frame(root):
    return find_local(find_local(root, "VirtualConsole"), "Frame")


def _generated_frames(root, frame_ids):
    wanted = {str(i) for i in frame_ids}
    return [
        child for child in _console_frame(root)
        if localname(child) == "SoloFrame" and child.attrib.get("ID") in wanted
    ]


def test_layout_gives_every_function_one_button(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    before_widgets = existing_widget_ids(ws.root)

    palette = generate_color_palette(ws, library)
    movement = generate_movement_efx(ws, library)
    exposed = palette.scene_ids + [palette.chaser_id] + movement.efx_ids
    layout = generate_vc_layout(ws, function_ids=exposed)

    # One frame per UI folder the functions were filed under.
    assert len(layout.frame_ids) == 2
    assert len(layout.button_ids) == len(exposed)
    assert set(layout.button_ids).isdisjoint(before_widgets)
    assert len(set(layout.button_ids) | set(layout.frame_ids)) == len(exposed) + 2

    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    frames = _generated_frames(reloaded, layout.frame_ids)
    assert sorted(f.attrib["Caption"] for f in frames) == [
        "Colores (generado)", "Movimiento (generado)"
    ]
    wired = [
        int(find_local(button, "Function").attrib["ID"])
        for frame in frames
        for button in findall_local(frame, "Button")
    ]
    assert sorted(wired) == sorted(exposed)


def test_colour_buttons_carry_their_colour(tmp_path):
    ws = Workspace.load(SHOW)
    palette = generate_color_palette(ws, FixtureLibrary.load(), make_chaser=False)
    layout = generate_vc_layout(ws, function_ids=palette.scene_ids)

    frame = _generated_frames(ws.root, layout.frame_ids)[0]
    buttons = {b.attrib["Caption"]: b for b in findall_local(frame, "Button")}
    background = find_local(
        find_local(buttons["Color Rojo"], "Appearance"), "BackgroundColor"
    )
    assert background.text == str(argb_from_rgb((255, 0, 0)))


def test_layout_lands_below_the_existing_console(tmp_path):
    ws = Workspace.load(SHOW)
    frame = _console_frame(ws.root)
    bottom = max(
        int(state.attrib["Y"]) + int(state.attrib["Height"])
        for child in frame
        if (state := find_local(child, "WindowState")) is not None
    )

    palette = generate_color_palette(ws, FixtureLibrary.load())
    layout = generate_vc_layout(ws, function_ids=palette.scene_ids)

    new_frame = _generated_frames(ws.root, layout.frame_ids)[0]
    assert int(find_local(new_frame, "WindowState").attrib["Y"]) >= bottom

    # The console canvas grew to fit what we added.
    properties = find_local(find_local(ws.root, "VirtualConsole"), "Properties")
    size = find_local(properties, "Size")
    assert int(size.attrib["Height"]) >= int(
        find_local(new_frame, "WindowState").attrib["Y"]
    )


def test_layout_refuses_an_empty_selection():
    ws = Workspace.load(SHOW)
    with pytest.raises(ValueError, match="no functions"):
        generate_vc_layout(ws, function_ids=[])


@pytest.mark.skipif(
    qlcplus_binary() is None, reason="QLC+ is not installed on this machine"
)
def test_qlcplus_loads_a_generated_layout(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    palette = generate_color_palette(ws, library)
    generate_vc_layout(ws, function_ids=palette.scene_ids + [palette.chaser_id])
    out = tmp_path / "out.qxw"
    ws.save(out)

    result = validate_workspace(out)

    assert result.ok, result.describe()
