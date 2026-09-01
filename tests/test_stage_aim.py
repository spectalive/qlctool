"""The measured stage look survives generation - `Escenario`, 2026-08-27.

The hand-built show had one button aiming the heads at the stage, tuned by eye
on the real rig. Those numbers are data, not something a generator can derive,
so the test pins them: the scene must land each measured pan/tilt on the
fixture patched at that DMX address, on its PAN/TILT channels, fine at zero.
"""

from pathlib import Path

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.stage_aim import MEASURED_AIMS, generate_stage_aim
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
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

    seen_addresses = set()
    for value in findall_local(scene, "FixtureVal"):
        capability = by_id[int(value.attrib["ID"])]
        address = capability.fixture.address
        pan, tilt = MEASURED_AIMS[address]
        seen_addresses.add(address)
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

    # Every measured address that is patched got aimed - the four beams and
    # the two downstage CromoWash, on this rig.
    patched = {c.fixture.address for c in by_id.values()}
    assert seen_addresses == set(MEASURED_AIMS) & patched
    assert len(seen_addresses) == 6
