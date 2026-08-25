"""Symmetry: one side of the rig runs the path backwards.

With every head going the same way round, a circle sweeps the whole room in
parallel. Reversing the fixtures past the centre line is what makes the pairs
open and close together, and it is the reason the plot's positions are read back
out of the workspace rather than only written into it.
"""

from pathlib import Path

from qlctool.generate.home_position import MID, generate_home_position
from qlctool.generate.movement_efx import generate_movement_efx, moving_head_ids
from qlctool.library import FixtureLibrary
from qlctool.monitor_positions import house_right_fixture_ids
from qlctool.skeleton import strip_to_skeleton
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


def test_the_plot_says_which_fixtures_are_house_right():
    root = Workspace.load(SHOW).root

    right = house_right_fixture_ids(root)

    assert right, "the rig is placed, so it has two sides"
    # Both sides are populated - a rule that put everything on one side would
    # pass every other check here and mirror nothing.
    monitor = find_local(find_local(root, "Engine"), "Monitor")
    visible = [
        item for item in monitor
        if localname(item) == "FxItem" and item.get("Hidden") is None
    ]
    assert 0 < len(right) < len(visible)


def test_the_far_side_of_the_rig_runs_the_efx_backwards():
    ws = strip_to_skeleton(Workspace.load(SHOW))
    library = FixtureLibrary.load()
    mirrored = house_right_fixture_ids(ws.root)
    movers = set(moving_head_ids(ws, library))
    assert movers & mirrored

    generate_movement_efx(ws, library, mirrored_ids=mirrored)

    checked = 0
    for function in ws.engine:
        if function.attrib.get("Type") != "EFX":
            continue
        for fixture in findall_local(function, "Fixture"):
            fixture_id = int(find_local(fixture, "ID").text)
            direction = find_local(fixture, "Direction").text
            expected = "Backward" if fixture_id in mirrored else "Forward"
            assert direction == expected, f"fixture {fixture_id}"
            checked += 1
    assert checked


def test_the_heads_have_somewhere_to_be_when_nothing_moves_them():
    """Stillness is a look, so it needs a scene - a head nothing drives sits
    wherever the last effect abandoned it, often pointing at the ceiling."""
    ws = strip_to_skeleton(Workspace.load(SHOW))
    library = FixtureLibrary.load()

    function_id = generate_home_position(ws, library)

    scene = next(
        f for f in ws.engine
        if localname(f) == "Function" and f.attrib.get("ID") == str(function_id)
    )
    driven = {int(v.attrib["ID"]) for v in findall_local(scene, "FixtureVal")}
    assert driven == set(moving_head_ids(ws, library))
    values = [int(n) for n in (findall_local(scene, "FixtureVal")[0].text).split(",")]
    assert MID in values[1::2]
