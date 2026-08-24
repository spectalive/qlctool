"""Generate a full colour palette + cycle chaser into the real show.

Proves the headline generator: 12 colour scenes and a chaser that steps through
them, all with unique IDs, injected without disturbing existing functions.
"""

from pathlib import Path

from qlctool.generate.color_palette import generate_color_palette
from qlctool.ids import existing_function_ids
from qlctool.library import FixtureLibrary
from qlctool.palette import PALETTE
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def test_generate_palette_and_chaser(tmp_path):
    library = FixtureLibrary.load()
    ws = Workspace.load(SHOW)
    before_ids = existing_function_ids(ws.root)

    result = generate_color_palette(ws, library)

    assert len(result.scene_ids) == len(PALETTE)
    assert result.chaser_id is not None
    # Every new ID is unique and none collides with a pre-existing function.
    new_ids = set(result.scene_ids) | {result.chaser_id}
    assert len(new_ids) == len(PALETTE) + 1
    assert new_ids.isdisjoint(before_ids)

    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    # Scenes present and named.
    names = {
        f.attrib.get("Name")
        for f in iter_local(reloaded, "Function")
        if f.attrib.get("Type") == "Scene"
    }
    for color in PALETTE:
        assert f"Color {color}" in names

    # Chaser has one step per generated scene, in order.
    chaser = next(
        f for f in iter_local(reloaded, "Function")
        if f.attrib.get("ID") == str(result.chaser_id)
    )
    assert chaser.attrib["Type"] == "Chaser"
    steps = findall_local(chaser, "Step")
    assert [s.text for s in steps] == [str(i) for i in result.scene_ids]
    assert find_local(chaser, "RunOrder").text == "Loop"
