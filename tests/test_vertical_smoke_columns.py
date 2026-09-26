"""2026-09-25, the owner's delegated decision: no vertical-smoke light where there is no column.

Vibra with its smoke machines taken out (fixtures 17 and 29-32, the
reproduction of `tests/test_haze_promise.py`) still built the panels'
`Humo Vertical` chaser, a function nothing could start: page 3 builds its
button only where a smoke machine is patched. The light is now built only
where a vertical column is - a smoke machine with a red channel, the same
answer the burst gives (`vertical_smoke_columns`).
"""

import pytest
from rig_root import RIG_ROOT

from qlctool.capabilities_of import capabilities_of
from qlctool.cli import main
from qlctool.generate import vertical_smoke_light
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.generate.builtin_effects import generate_builtin_effects
from qlctool.library import FixtureLibrary
from qlctool.vibra.keys import KEYS
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, iter_local

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
SMOKE_MACHINES = ("17", "29", "30", "31", "32")
# The column light's own holds: Effect 1 for a minute, Effect 3 for ten.
HOLDS = [vertical_smoke_light.FIRST_HOLD_MS, vertical_smoke_light.SECOND_HOLD_MS]


@pytest.fixture(scope="module")
def no_smoke_patch(tmp_path_factory):
    folder = tmp_path_factory.mktemp("nosmoke")
    removals = [arg for fixture in SMOKE_MACHINES for arg in ("--remove", fixture)]
    patch = folder / "nosmoke-patch.qxw"
    assert main(["patch", str(VIBRA), *removals, "--out", str(patch)]) == 0
    return patch


def _column_light_chasers(workspace: Workspace) -> list[str]:
    """The chasers stepping through two holds of one and ten minutes, by id."""
    return [
        f.get("ID", "")
        for f in iter_local(workspace.root, "Function")
        if f.get("Type") == "Chaser"
        and [int(s.get("Hold", "0")) for s in findall_local(f, "Step")] == HOLDS
    ]


def test_2026_09_25_no_column_no_column_light(no_smoke_patch):
    library = FixtureLibrary.load()
    workspace = Workspace.load(no_smoke_patch)
    caps = capabilities_of(workspace.root, library)
    builtins = generate_builtin_effects(workspace, caps, label="Panels")
    assert builtins.scene_ids, "the panels are still patched"
    assert (
        vertical_smoke_light.generate_vertical_smoke_light(workspace, builtins.scene_ids, caps)
        is None
    )


def test_2026_09_25_the_show_without_columns_builds_one_function_fewer(no_smoke_patch, monkeypatch):
    library = FixtureLibrary.load()
    without = Workspace.load(no_smoke_patch)
    built = build_canonical_show(without, library)
    assert _column_light_chasers(without) == []
    # The same build with the column check forced open: exactly the one chaser more.
    monkeypatch.setattr(vertical_smoke_light, "vertical_smoke_columns", list)
    allowed = Workspace.load(no_smoke_patch)
    forced = build_canonical_show(allowed, library)
    assert len(_column_light_chasers(allowed)) == 1
    assert forced.function_count == built.function_count + 1


def test_2026_09_25_vibra_keeps_its_column_light():
    """And its button: a toggle on its own key (the contract `test_live_console` held on
    DeluxeEventos2 until that rig, which has no column, stopped building it)."""
    workspace = Workspace.load(VIBRA)
    build_canonical_show(workspace, FixtureLibrary.load())
    [chaser] = _column_light_chasers(workspace)
    buttons = [
        b
        for b in iter_local(workspace.root, "Button")
        if find_local(b, "Function") is not None and find_local(b, "Function").get("ID") == chaser
    ]
    assert len(buttons) == 1
    assert find_local(buttons[0], "Action").text == "Toggle"
    assert find_local(buttons[0], "Key").text == KEYS["Humo Vertical"]
