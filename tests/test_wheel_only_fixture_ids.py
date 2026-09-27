"""Round G review, 2026-09-26: which fixtures take the talk white from a colour wheel.

`wheel_only_fixture_ids` had no test of its own: the talk light on a
wheel-only, gobo-less fixture was exercised only end to end by the sweep's
CLB2.4 two-channel case, and no shipped rig carries such a fixture.
"""

from pathlib import Path

import pytest
from single_shape_rig import build_single_shape_patch

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.capability import FixtureCapabilities
from qlctool.cli import main
from qlctool.color_wheel_match import color_wheel_pairs
from qlctool.fixture import PatchedFixture
from qlctool.generate.wheel_only_fixture_ids import wheel_only_fixture_ids
from qlctool.library import FixtureLibrary
from qlctool.names.default_names import default_names
from qlctool.workspace import Workspace
from qlctool.xmlutil import findall_local, iter_local

WHEEL_PARS = ("Stairville|CLB2.4 Compact LED PAR System|2 Channel|0|{address}|Bar {index}", 2, 2)


def _stand_in(fixture_id: int, *channel_roles: str, fixture_type: str = "Color Changer"):
    fixture = PatchedFixture(
        fixture_id=fixture_id,
        manufacturer="Stand-in",
        model=f"Model {fixture_id}",
        mode="Mode",
        universe=0,
        address=fixture_id * 8,
        channels=len(channel_roles),
        name=f"Fixture {fixture_id}",
    )
    return FixtureCapabilities(
        fixture=fixture,
        roles_by_offset=list(channel_roles),
        capabilities_by_offset=[() for _ in channel_roles],
        groups_by_offset=["Colour" for _ in channel_roles],
        fixture_type=fixture_type,
    )


def test_2026_09_27_only_a_wheel_with_no_rgb_no_gobo_and_no_smoke_qualifies():
    caps = [
        _stand_in(1, roles.COLOR_MACRO, roles.DIMMER),
        _stand_in(2, roles.COLOR_MACRO, roles.RED, roles.GREEN, roles.BLUE),
        _stand_in(3, roles.COLOR_MACRO, roles.GOBO, roles.DIMMER),
        _stand_in(4, roles.COLOR_MACRO, roles.SMOKE, fixture_type="Smoke"),
        _stand_in(5, roles.RED, roles.GREEN, roles.BLUE),
        _stand_in(6, roles.COLOR_MACRO),
    ]
    assert wheel_only_fixture_ids(caps) == [1, 6]


@pytest.fixture(scope="module")
def show(tmp_path_factory) -> Path:
    folder = tmp_path_factory.mktemp("wheel-pars")
    out = folder / "show.qxw"
    assert (
        main(["newshow", str(build_single_shape_patch(folder, *WHEEL_PARS)), "--out", str(out)])
        == 0
    )
    return out


def _scene_pairs(root, name: str) -> dict[int, set[tuple[int, int]]]:
    scene = next(
        f
        for f in iter_local(root, "Function")
        if f.get("Type") == "Scene" and f.get("Name") == name
    )
    pairs: dict[int, set[tuple[int, int]]] = {}
    for value in findall_local(scene, "FixtureVal"):
        numbers = [int(n) for n in (value.text or "").split(",") if n]
        pairs[int(value.get("ID"))] = set(zip(numbers[::2], numbers[1::2], strict=True))
    return pairs


def test_2026_09_27_the_talk_scene_lands_on_the_wheel_white(show):
    names = default_names()
    root = Workspace.load(show).root
    caps = capabilities_of(root, FixtureLibrary.load())
    ids = wheel_only_fixture_ids(caps)
    assert ids == [c.fixture.fixture_id for c in caps]
    written = _scene_pairs(root, names.display("talk_light_base"))
    for capability in caps:
        white = set(color_wheel_pairs(capability, "white", names))
        assert white and white <= written[capability.fixture.fixture_id]
