"""2026-09-25, review of `rotulo que promete lo que no hay`: page 3 promised haze
on a rig with panels and no smoke machine.

The generator titled page 3 `page_control` ("... intensidad y humo") whenever
the panels' vertical-smoke light was built, and that light needs only the
panels. Vibra with its smoke machines taken out (fixtures 17 and 29-32, the
reviewer's reproduction) built with that title and `check` rejected it. A
hazer, by type or by a pump channel named "haze", is a smoke machine too.
"""

from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.checks.run import check_workspace
from qlctool.cli import main
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
SMOKE_MACHINES = ("17", "29", "30", "31", "32")


def test_2026_09_25_panels_without_a_smoke_machine_promise_no_haze(tmp_path):
    removals = [arg for fixture in SMOKE_MACHINES for arg in ("--remove", fixture)]
    patch = tmp_path / "nosmoke-patch.qxw"
    assert main(["patch", str(VIBRA), *removals, "--out", str(patch)]) == 0
    out = tmp_path / "nosmoke.qxw"
    assert main(["newshow", str(patch), "--out", str(out)]) == 0
    findings = check_workspace(Workspace.load(out), FixtureLibrary.load())
    assert [str(f) for f in findings] == []


def test_2026_09_25_a_pump_named_haze_is_a_smoke_channel():
    assert roles.role_of(None, "Effect", "Haze") == roles.SMOKE
    assert roles.role_of(None, "Intensity", "Hazer output") == roles.SMOKE


def test_2026_09_25_a_hazer_typed_fixture_is_a_smoke_machine():
    import dataclasses

    from qlctool.capabilities_of import capabilities_of
    from qlctool.is_smoke_machine import is_smoke_machine

    caps = capabilities_of(Workspace.load(VIBRA).root, FixtureLibrary.load())
    par = next(c for c in caps if c.has_role(roles.RED) and not c.is_smoke)
    assert not is_smoke_machine(par)
    hazer = dataclasses.replace(par, fixture_type="Hazer")
    assert is_smoke_machine(hazer)
    # 2026-09-25, re-review: the smoke property every generator and rule
    # reads (pump parked, no dimmer, no light) sees the hazer too.
    assert hazer.is_smoke
