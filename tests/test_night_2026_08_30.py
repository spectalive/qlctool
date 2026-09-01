"""The night of 2026-08-29, reported the morning after - pinned.

Four things the owner watched, in his words:

- "las nuevas cabezas wash se quedaban mirando para abajo y hacian cosas raras
  como una especie de cambios de colores muy rapidos" - the two MAC WASH
  1915Z running their own programme while the show sent them a measured aim
  and a slow colour wheel.
- "los beam quedaron bien posicionados pero le faltaba usar mas los gobos los
  prismas etc ... se echaba en falta mas variedad" - seventeen gobos thrown
  out of focus, four heads always on the same one, and a prism that only
  existed for forty seconds out of every twenty-four minutes.
- "salia humo bien pero la luz solo salia la blanca, no hacia las transiciones
  de colores" - the held column repainting itself white over the room's
  colour, at flash priority.
- "el humo vertical nunca debe dispararse solo, el otro humo (ambiente)
  debemos tener ... un timer y que se dispare cada x tiempo (estaria bien
  poder tocar eso desde la consola en el show)".

Each test puts the shipped generator through its paces on the real patch and
fails if that night can happen again.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capabilities_of import capabilities_of
from qlctool.generate.canonical_show import BEAM_FOCUS, build_canonical_show
from qlctool.generate.smoke_auto import SMOKE_INTERVALS_MIN
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local, localname

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "Vibra-split.qxw"


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


@pytest.fixture(scope="module")
def built(library):
    workspace = Workspace.load(SHOW)
    build_canonical_show(workspace, library)
    return workspace


def _functions(root):
    return {
        function.attrib.get("Name"): function
        for function in find_local(root, "Engine")
        if localname(function) == "Function"
    }


def _values(function, fixture_id: int) -> dict[int, int]:
    for element in findall_local(function, "FixtureVal"):
        if element.attrib.get("ID") != str(fixture_id):
            continue
        numbers = [int(n) for n in (element.text or "").split(",") if n != ""]
        return dict(zip(numbers[::2], numbers[1::2], strict=True))
    return {}


def _fixtures_with(workspace, library, role):
    return [
        capability
        for capability in capabilities_of(workspace.root, library)
        if capability.has_role(role)
    ]


def test_every_colour_look_takes_the_washes_off_their_own_programme(built, library):
    """2026-08-30: the two new washes ignored the show all night.

    Their `Function Mode` channel - one blanket 000-255 range, no names for
    `internal_program` to match on - was written by nothing, so it carried
    whatever the last controller left there while the show sent position,
    colour and dimmer into a fixture that was not listening. Every look that
    states a colour parks it now.
    """
    functions = _functions(built.root)
    movers = [
        capability
        for capability in capabilities_of(built.root, library)
        if capability.has_role(roles.EFFECT)
        and capability.has_role(roles.PAN)
        and capability.has_role(roles.RED)
    ]
    assert movers, "no RGB moving head in this patch carries a mode channel"
    for capability in movers:
        offsets = capability.offsets_for_role(roles.EFFECT)
        fixture_id = capability.fixture.fixture_id
        # 2026-08-31: a mover can now live in a fixture group of its own, and a
        # rig-wide look deliberately skips a group that has its own colour bank
        # - two colour clocks on one fixture is its own bug. So a look that does
        # not reach this fixture is not a look that abandoned it; what matters
        # is that everything which *lights* it owns the mode channel.
        reaching = [
            name
            for name in ("Blanco Total", "Rig Rojo", "Luz Charla")
            if _values(functions[name], fixture_id)
        ]
        assert reaching, f"no room look reaches {capability.fixture.name} at all"
        for name in reaching:
            written = _values(functions[name], fixture_id)
            assert all(written.get(offset) == 0 for offset in offsets), (
                f"{name} leaves {capability.fixture.name} on its own programme"
            )

        # And the scene that owns a matrix-lit fixture, which is the only thing
        # holding it open under AUTO once it is in a group of its own. Missing
        # this is what let the two MAC WASH run their own programme under a
        # matrix that thought it was painting them.
        base = functions.get("Pixeles ON")
        if base is not None and _values(base, fixture_id):
            written = _values(base, fixture_id)
            assert all(written.get(offset) == 0 for offset in offsets), (
                f"Pixeles ON lights {capability.fixture.name} and leaves it on its own programme"
            )

    # The beams have no RGB, so the colour generator never reaches them: their
    # own effect channel is parked by the wheel-colour looks or by nothing.
    for capability in _fixtures_with(built, library, roles.GOBO):
        offsets = capability.offsets_for_role(roles.EFFECT)
        for name in ("Blanco Total", "Rig Rojo"):
            written = _values(functions[name], capability.fixture.fixture_id)
            assert all(written.get(offset) == 0 for offset in offsets), (
                f"{name} leaves {capability.fixture.name} on its own programme"
            )


def test_the_gobos_are_focused_and_the_four_beams_differ(built, library):
    """2026-08-30: "le faltaba usar mas los gobos".

    Two causes, both in the file. Nothing had ever written the focus channel,
    so seventeen patterns were projected at one end of its travel; and every
    gobo scene put the same pattern on all four heads, which is one shape
    repeated rather than a rig.
    """
    functions = _functions(built.root)
    beams = _fixtures_with(built, library, roles.GOBO)
    assert len(beams) >= 4, "this patch lost its beams"

    plain = functions["Gobo - Gobo 3"]
    for capability in beams:
        focus = capability.offsets_for_role(roles.FOCUS)
        written = _values(plain, capability.fixture.fixture_id)
        assert focus, f"{capability.fixture.name} has no focus channel"
        assert all(written.get(offset) == BEAM_FOCUS for offset in focus), (
            "a gobo scene that states no focus is a gobo out of focus"
        )

    dealt = functions["Gobo Repartido 1"]
    positions = set()
    for capability in beams:
        offset, _ = capability.wheel_for_role(roles.GOBO)
        positions.add(_values(dealt, capability.fixture.fixture_id)[offset])
    assert len(positions) == len(beams), "the dealt gobo puts the same pattern on every head"


def test_the_prism_turns_more_than_one_way_and_runs_in_the_party(built, library):
    """2026-08-30: the prism existed for 40 s out of every 24 minutes, always
    inserted, always turning forward at 25 of its 0-127 run.

    It rides the party level and the party moment now, and its dance ends on
    the two spins the rotation channel could always do.
    """
    functions = _functions(built.root)
    animation = functions["Prisma Animacion"]
    steps = [int(step.text) for step in findall_local(animation, "Step")]
    ids = {
        int(function.attrib["ID"]): name
        for name, function in functions.items()
        if function.attrib.get("ID")
    }
    danced = {ids.get(step) for step in steps}
    assert {"Prisma Giro Rapido", "Prisma Giro Inverso"} <= danced

    spins = set()
    for name in ("Prisma - Insert Prism", "Prisma Giro Rapido", "Prisma Giro Inverso"):
        for capability in _fixtures_with(built, library, roles.PRISM_ROTATION):
            written = _values(functions[name], capability.fixture.fixture_id)
            spins.update(
                written[offset]
                for offset in capability.offsets_for_role(roles.PRISM_ROTATION)
                if offset in written
            )
    assert len(spins) >= 3, "the prism still has one speed and one direction"

    for level in ("Nivel Fiesta", "Nivel Fiesta Dinamico", "Momento Fiesta"):
        members = {ids.get(int(step.text)) for step in findall_local(functions[level], "Step")}
        assert "Prisma Animacion" in members, f"{level} carries no prism"


def test_the_held_column_leaves_the_colour_to_the_room(built, library):
    """2026-08-30: "salia humo bien pero la luz solo salia la blanca".

    The column scene is flashed with Override - the top fader priority in
    QLC+ - so the white it used to write beat the colour wheel every time the
    button went down. Pump and LED master only: the room owns the colour.
    """
    burst = _functions(built.root)["Humo Vertical YA"]
    columns = [
        capability
        for capability in capabilities_of(built.root, library)
        if capability.is_smoke and capability.has_role(roles.RED)
    ]
    assert columns, "this patch lost its lit fog machines"
    for capability in columns:
        written = _values(burst, capability.fixture.fixture_id)
        colours = [
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE)
            for offset in capability.offsets_for_role(role)
        ]
        assert not any(offset in written for offset in colours), (
            "the held column paints over the colour the room is running"
        )
        assert all(
            written.get(offset) == 255 for offset in capability.offsets_for_role(roles.DIMMER)
        ), "the column fires with its own LED down"


def test_the_ambient_haze_offers_its_rhythm_on_the_console(built):
    """2026-08-30: "estaria bien poder tocar eso desde la consola en el show".

    A speed dial cannot do it - the timer is a two-step chaser in PerStep
    duration mode - so the rhythms are functions, one per interval, and the
    console puts them in a solo frame.
    """
    functions = _functions(built.root)
    names = ["Humo Auto"] + [f"Humo Auto {minutes} min" for minutes in SMOKE_INTERVALS_MIN[1:]]
    for name in names:
        assert name in functions, f"the console has no {name} to press"
    waits = []
    for name in names:
        steps = findall_local(functions[name], "Step")
        waits.append(int(steps[-1].attrib["Hold"]))
    assert waits == sorted(waits) and len(set(waits)) == len(waits), (
        "the haze rhythms are not four different intervals"
    )
