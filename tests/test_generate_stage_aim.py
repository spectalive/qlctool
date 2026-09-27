"""The measured stage look survives generation - `Escenario`, 2026-08-27.

The hand-built show had one button aiming the heads at the stage, tuned by eye
on the real rig. Those numbers are data, not something a generator can derive,
so the test pins them: the scene must land each measured pan/tilt on the
fixture patched at that DMX address, on its PAN/TILT channels, fine at zero.
"""

from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.generate_stage_aim import MEASURED_AIMS, generate_stage_aim
from qlctool.generate.movement_aim import WASH_PAN_AIM, WASH_TILT_AIM
from qlctool.workspace import Workspace
from qlctool.xmlutil import localname

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "Vibra-split.qxw"


def test_the_measured_aims_land_on_the_patched_fixtures():
    workspace = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    function_id = generate_stage_aim(workspace, library)
    assert function_id is not None

    by_id = {c.fixture.fixture_id: c for c in capabilities_of(workspace.root, library)}
    scene = next(
        f
        for f in find_local(workspace.root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID") == str(function_id)
    )
    assert scene.attrib["Name"] == "Escenario"

    # Ruling D7 (2026-09-26): a rigged head with no measured aim - the MAC
    # WASH - holds its window's centre until somebody measures it on site.
    seen = set()
    for value in findall_local(scene, "FixtureVal"):
        capability = by_id[int(value.attrib["ID"])]
        address = capability.fixture.address
        pan, tilt = MEASURED_AIMS.get(address, (WASH_PAN_AIM, WASH_TILT_AIM))
        seen.add(capability.fixture.name)
        numbers = [int(n) for n in value.text.split(",")]
        written = dict(zip(numbers[0::2], numbers[1::2], strict=True))
        for role, expected in (
            (roles.PAN, pan),
            (roles.TILT, tilt),
            (roles.PAN_FINE, 0),
            (roles.TILT_FINE, 0),
        ):
            for offset in capability.offsets_for_role(role):
                assert written[offset] == expected, (address, role)

    # The four beams at their measured aims and the two MACs at the window
    # centre; the two downstage CromoWash the hand-built scene aimed are
    # spares in a flight case on this rig now, and are left out.
    assert seen == {
        "BEAM 230W 7R #1",
        "BEAM 230W 7R #2",
        "BEAM 230W 7R #3",
        "BEAM 230W 7R #4",
        "MAC WASH 1915Z #1",
        "MAC WASH 1915Z #2",
    }
