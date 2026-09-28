"""The canonical show's colour: one source per fixture, and nothing left dark.

Split by topic out of the original `test_canonical_show.py` (over the
codeality test-file line cap).
"""

import pytest
from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_groups import fixture_groups
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.localname import localname
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _functions(root):
    return {
        f.attrib["ID"]: f
        for f in find_local(root, "Engine")
        if localname(f) == "Function" and f.attrib.get("ID")
    }


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    ws = Workspace.load(SHOW)
    show = build_canonical_show(ws, FixtureLibrary.load())
    out = tmp_path_factory.mktemp("show") / "Vibra.qxw"
    ws.save(out)
    return show, out


def test_one_fixture_never_has_two_colour_sources_under_auto(built):
    """RGB mixes HTP, so two sources on one fixture add up instead of choosing.

    A bar told red by the rig-wide wheel and blue by its own matrix came out
    magenta, and anything on top of that came out white. The pixel groups
    belong to their matrix; the wheel lights everything else.
    """
    _, out = built
    root = Workspace.load(out).root
    caps = {c.fixture.fixture_id: c for c in capabilities_of(root, FixtureLibrary.load())}
    painted = {
        fixture_id
        for group in fixture_groups(root)
        if group.name == "BarrasLed"
        for fixture_id in group.fixture_ids
    }
    assert painted, "no pixel group in this patch"

    for function in _functions(root).values():
        name = function.attrib.get("Name", "")
        if not name.startswith(("Rig ", "Cabezas ")):
            continue
        for value in findall_local(function, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            if fixture_id not in painted or not value.text:
                continue
            numbers = [int(n) for n in value.text.split(",")]
            written = set(numbers[0::2])
            rgb = {
                offset
                for role in (roles.RED, roles.GREEN, roles.BLUE)
                for offset in caps[fixture_id].offsets_for_role(role)
            }
            assert not (written & rgb), (name, fixture_id)


def test_a_moment_brings_its_own_colour_bed(built):
    """A moment replaces AUTO, so whatever AUTO was providing has to come with
    it - otherwise pressing CHARLA leaves the room dark."""
    show, out = built
    functions = _functions(Workspace.load(out).root)

    for moment in (
        "Momento Charla",
        "Momento Tranquilo",
        "Momento Fiesta",
        "Momento Locura",
    ):
        collection = functions[str(show.master_ids[moment])]
        assert collection.attrib["Type"] == "Collection"
        members = {
            functions[step.text].attrib["Name"] for step in findall_local(collection, "Step")
        }
        lights_something = members & {
            "Rueda Colores",
            "Luz Charla",
            "Ciclo Matrices BarrasLed",
        }
        assert lights_something, (moment, members)

    # The speech look is the one with nothing moving in it.
    charla = functions[str(show.master_ids["Momento Charla"])]
    moving = {functions[step.text].attrib["Name"] for step in findall_local(charla, "Step")} & {
        "Rueda Colores",
        "Movimientos Cabezas",
        "Gobo Animacion",
        "Ciclo Matrices BarrasLed",
        "Dimmer Chase",
    }
    assert not moving, moving


def test_there_is_one_white_and_it_is_not_called_luces_on(built):
    """Three buttons drove full white on the same fixtures and no name said
    which was which."""
    show, _ = built
    assert "Blanco Total" in show.master_ids
    assert "Luces ON" not in show.master_ids
    assert "Todo Blanco" not in show.master_ids


def _pairs(function, fixture_id):
    """The (offset, value) a Scene writes to one fixture."""
    for value in findall_local(function, "FixtureVal"):
        if int(value.attrib["ID"]) != fixture_id or not value.text:
            continue
        numbers = [int(n) for n in value.text.split(",")]
        return dict(zip(numbers[0::2], numbers[1::2], strict=True))
    return {}


def test_everything_white_reaches_the_beams(built):
    """A beam has no RGB, so a colour scene skipped it and left it dark.

    Not dimmed and not the wrong colour: never written to. "Blanco Total" is
    the button somebody presses to see the room, and four 7R staying black is
    the most visible way for it to be wrong.
    """
    show, out = built
    root = Workspace.load(out).root
    caps = capabilities_of(root, FixtureLibrary.load())
    functions = _functions(root)

    wheel_only = [
        c
        for c in caps
        if c.has_role(roles.COLOR_MACRO)
        and not any(c.has_role(r) for r in (roles.RED, roles.GREEN, roles.BLUE))
    ]
    assert wheel_only, "no wheel-coloured fixture in this patch"

    # Both flashes at full: "50%" is half the strobe *speed*, not half the
    # brightness - what it meant on the hand-built console (2026-08-27).
    for look, level in (("Blanco Total", 255), ("Flash 100%", 255), ("Flash 50%", 255)):
        scene = functions[str(show.master_ids[look])]
        for capability in wheel_only:
            written = _pairs(scene, capability.fixture.fixture_id)
            assert written, (look, capability.fixture.name)
            for offset in capability.offsets_for_role(roles.DIMMER):
                assert written.get(offset) == level, (look, capability.fixture.name)
            wheel = capability.wheel_for_role(roles.COLOR_MACRO)
            assert wheel is not None and wheel[0] in written, look


def test_a_matrix_lit_fixture_has_its_intensity_opened(built):
    """A matrix writes RGB and nothing else.

    The panels keep a master dimmer on channel 1 and a shutter on channel 5,
    and no matrix touches either. The rig-wide wheel used to open them by
    accident; taking these fixtures off the wheel took that away too, and they
    went dark everywhere except under a flat scene like Flash 100%.
    """
    show, out = built
    root = Workspace.load(out).root
    caps = {c.fixture.fixture_id: c for c in capabilities_of(root, FixtureLibrary.load())}
    functions = _functions(root)

    base = functions[str(show.master_ids["Pixeles ON"])]
    assert base.attrib["Type"] == "Scene"

    painted = {
        fixture_id
        for group in fixture_groups(root)
        if group.name == "BarrasLed"
        for fixture_id in group.fixture_ids
    }
    needs_opening = [
        capability
        for fixture_id in painted
        if (capability := caps[fixture_id])
        and any(capability.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
        and capability.offsets_for_role(roles.DIMMER)
    ]
    assert needs_opening, "no matrix-lit fixture has a dimmer to open"
    for capability in needs_opening:
        written = _pairs(base, capability.fixture.fixture_id)
        for offset in capability.offsets_for_role(roles.DIMMER):
            assert written.get(offset) == 255, capability.fixture.name

    # It carries no colour: that is the matrix's, and two sources make white.
    for capability in needs_opening:
        written = _pairs(base, capability.fixture.fixture_id)
        for role in (roles.RED, roles.GREEN, roles.BLUE):
            for offset in capability.offsets_for_role(role):
                assert offset not in written, capability.fixture.name


def test_the_pixel_intensity_runs_wherever_the_wheel_does(built):
    """Colour without intensity is a fixture that is off. They travel together.

    The wheel's steps paint the pixel groups through their matrices, and a
    matrix writes RGB and nothing else - so every state that starts the wheel
    starts the scene holding their dimmers and shutters open beside it.
    """
    show, out = built
    functions = _functions(Workspace.load(out).root)
    base = str(show.master_ids["Pixeles ON"])
    wheel = str(show.master_ids["Rueda Colores"])

    for name in ("AUTO", "Momento Tranquilo", "Momento Fiesta", "Momento Locura"):
        collection = functions[str(show.master_ids[name])]
        members = {step.text for step in findall_local(collection, "Step")}
        assert wheel in members, name
        assert base in members, name
