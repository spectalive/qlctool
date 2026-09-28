"""Put the pre-2026-09-02 STROBO back: a white/black chaser on a Toggle."""

from functions_by_name_of_workspace import functions_by_name_of_workspace as _functions
from strip_strobe_writes_from_black_twin import (
    strip_strobe_writes_from_black_twin as _strip_strobe_writes_from_black_twin,
)
from twin_scene import twin_scene as _twin_scene

from qlctool.capabilities_of import capabilities_of
from qlctool.localname import localname


def burst_chaser(workspace, library, hold=125):
    """Put the pre-2026-09-02 STROBO back: a white/black chaser on a Toggle.

    `Strobo Rapido` was a SingleShot chaser alternating a white scene and a
    black one, on a Toggle button on the show page. It is a held shutter scene
    now, so the tests that need a strobe-shaped chaser build the old one here:
    twins of `Golpe Graves` (white, shutters open) and `Todo Negro`.
    """

    from qlctool.functions.build_chaser import build_chaser
    from qlctool.next_function_id import next_function_id
    from qlctool.vc.build_button import build_button
    from qlctool.vc.next_widget_id import next_widget_id

    functions = _functions(workspace)
    capabilities = {
        capability.fixture.fixture_id: capability
        for capability in capabilities_of(workspace.root, library)
    }
    white = _twin_scene(workspace, functions, "Golpe Graves", "Rafaga Blanco")
    black = _twin_scene(workspace, functions, "Todo Negro", "Rafaga Negro")
    _strip_strobe_writes_from_black_twin(black, capabilities)
    chaser_id = next_function_id(workspace.root)
    chaser = build_chaser(
        chaser_id,
        "Rafaga",
        [int(white.attrib["ID"]), int(black.attrib["ID"])] * 4,
        hold=hold,
        run_order="SingleShot",
        path="Strobos",
    )
    workspace.add_function(chaser)
    hits = next(
        f
        for f in workspace.root.iter()
        if localname(f) == "Frame" and f.attrib.get("Caption", "").startswith("GOLPES")
    )
    button = build_button(
        hits, next_widget_id(workspace.root), "RAFAGA", chaser_id, x=8, y=30, width=60, height=40
    )
    return chaser, button
