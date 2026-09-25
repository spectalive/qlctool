"""A show that renames a colour still reaches the wheel-only fixtures (2026-09-25).

Plan B ruling P11: the wheel match looked colour names up in the shipped
catalogues only, so a description saying `red = "Rojo Vivo"` painted its PARs
red and left the BEAM 230W 7R on whatever it had - no RGB, and a colour name
the matcher had never heard of. The show's own vocabulary is what spells it.
"""

from pathlib import Path

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.color_wheel_match import color_wheel_pairs
from qlctool.description.reading.read_names import read_names
from qlctool.generate.color_flashes import generate_color_flashes
from qlctool.library import FixtureLibrary
from qlctool.names.shipped_names import shipped_names
from qlctool.palette import PALETTE
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
RENAMED = "Rojo Vivo"


def _wheel_only(caps):
    return [
        c
        for c in caps
        if c.has_role(roles.COLOR_MACRO)
        and not any(c.has_role(role) for role in (roles.RED, roles.GREEN, roles.BLUE))
    ]


def _values(function):
    values: dict[int, dict[int, int]] = {}
    for fixture in findall_local(function, "FixtureVal"):
        numbers = [int(n) for n in (fixture.text or "").split(",") if n]
        values[int(fixture.attrib["ID"])] = dict(zip(numbers[::2], numbers[1::2]))
    return values


def test_a_renamed_colour_still_gets_its_wheel_colour():
    workspace = Workspace.load(SHOW)
    caps = capabilities_of(workspace.root, FixtureLibrary.load())
    beams = _wheel_only(caps)
    assert beams, "the show needs a wheel-only fixture for this test to mean anything"
    names = shipped_names("es", read_names({"es": {"red": RENAMED}}, "show.toml"))

    flashes = generate_color_flashes(workspace, caps, {RENAMED: PALETTE["Rojo"]}, 0.9, names=names)

    functions = {
        f.attrib["ID"]: f for f in findall_local(find_local(workspace.root, "Engine"), "Function")
    }
    hit = functions[str(flashes.ids[RENAMED])]
    assert hit.attrib["Name"] == names.render("colour_hit", colour=RENAMED)
    values = _values(hit)
    for beam in beams:
        expected = color_wheel_pairs(beam, "red")
        assert expected, f"{beam.fixture.fixture_id} has no red on its wheel"
        for offset, value in expected:
            assert values.get(beam.fixture.fixture_id, {}).get(offset) == value


def test_without_the_show_vocabulary_the_renamed_colour_is_unknown():
    """The regression the vocabulary fixes: the catalogues alone do not know it."""
    caps = capabilities_of(Workspace.load(SHOW).root, FixtureLibrary.load())
    names = shipped_names("es", read_names({"es": {"red": RENAMED}}, "show.toml"))
    for beam in _wheel_only(caps):
        assert color_wheel_pairs(beam, RENAMED) == []
        assert color_wheel_pairs(beam, RENAMED, names) == color_wheel_pairs(beam, "red")
