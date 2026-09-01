"""The rig-wide colour wheel: one colour everywhere, contrasts on purpose.

Three per-group Random wheels never land on the same colour, which is how the
heads ended up magenta while the PARs were green. These tests hold the two
things that fixes: a unison scene reaches every colour-capable fixture in the
patch - group or no group - and a contrast scene splits the movers from the
rest rather than splitting each group against itself.
"""

from pathlib import Path

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.unison_colors import CONTRAST_PAIRS, generate_unison_colors
from qlctool.library import FixtureLibrary
from qlctool.palette import PALETTE, PRIMARY_COLORS
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra.qxw"


def _functions(root):
    return {
        f.attrib["ID"]: f
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }


def _driven(function):
    return {int(v.attrib["ID"]) for v in findall_local(function, "FixtureVal")}


def test_a_unison_scene_lights_every_colour_fixture_in_the_patch(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()

    unison = generate_unison_colors(ws, library)

    out = tmp_path / "out.qxw"
    ws.save(out)
    functions = _functions(Workspace.load(out).root)
    assert len(unison.scene_ids) == len(PRIMARY_COLORS)

    # The lit fog machines count: their LED is a floor PAR on the wheel, only
    # their pump stays out of it.
    colored = {
        caps.fixture.fixture_id
        for caps in capabilities_of(ws.root, library)
        if not (caps.is_smoke and not caps.is_lit_smoke)
        and any(caps.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    }
    # The four beams have no RGB at all: their white is a wheel position.
    beams = {
        caps.fixture.fixture_id
        for caps in capabilities_of(ws.root, library)
        if caps.fixture.fixture_id not in colored
        and caps.wheel_for_role(roles.COLOR_MACRO) is not None
        and not caps.is_smoke
    }
    assert beams

    white = next(
        f for f in (functions[str(i)] for i in unison.scene_ids) if f.attrib["Name"] == "Rig Blanco"
    )
    # Including the two CLB2.4, which are in no fixture group and therefore in
    # no colour bank and no matrix: without this wheel AUTO leaves them dark.
    assert _driven(white) == colored | beams


def test_a_contrast_puts_the_movers_against_everything_else(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()

    unison = generate_unison_colors(ws, library)

    functions = _functions(ws.root)
    assert len(unison.contrast_ids) == len(CONTRAST_PAIRS)
    scene = next(
        f
        for f in (functions[str(i)] for i in unison.contrast_ids)
        if f.attrib["Name"] == "Cabezas Rojo / Resto Azul"
    )
    caps = {c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)}
    movers = {fid for fid, c in caps.items() if c.has_role(roles.PAN) and c.has_role(roles.TILT)}

    for value in findall_local(scene, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        pairs = [int(n) for n in (value.text or "").split(",")]
        by_offset = dict(zip(pairs[::2], pairs[1::2]))
        expected = PALETTE["Rojo"] if fixture_id in movers else PALETTE["Azul"]
        for role, level in zip((roles.RED, roles.GREEN, roles.BLUE), expected):
            for offset in caps[fixture_id].offsets_for_role(role):
                assert by_offset[offset] == level


def test_the_wheel_is_random_and_steps_every_scene(tmp_path):
    ws = Workspace.load(SHOW)

    unison = generate_unison_colors(ws, FixtureLibrary.load())

    wheel = _functions(ws.root)[str(unison.wheel_id)]
    assert wheel.attrib["Type"] == "Chaser"
    # Random: a fixed order reads as a loop when nobody is at the console.
    assert find_local(wheel, "RunOrder").text == "Random"
    assert len(findall_local(wheel, "Step")) == len(unison.scene_ids) + len(unison.contrast_ids)
