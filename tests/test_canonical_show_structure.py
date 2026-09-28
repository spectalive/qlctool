"""The canonical show's structure: the rig, the AUTO cycle and its colour wheel.

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
from qlctool.fog_offsets import fog_offsets
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.localname import localname
from qlctool.patch_conflicts import patch_conflicts
from qlctool.patched_fixtures import patched_fixtures
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


def test_the_rig_survives_and_the_old_content_does_not(built):
    show, out = built
    root = Workspace.load(out).root

    assert len(patched_fixtures(root)) == 27
    assert patch_conflicts(root) == []
    assert len(_functions(root)) == show.function_count
    assert [b.group_name for b in show.banks] == ["BarrasLed", "Cabezas", "PAR"]


def test_auto_is_a_colour_bed_a_haze_and_an_energy_cycle(built):
    """The colour and the haze run under everything; the level rides on top.

    Keeping the bed outside the cycle is what stops a level change from
    blacking the room out, and the effects that read as "peak" - fast movement,
    prism, the dimmer chase - are reachable only through the level that is one.
    The pixels' colour is part of the bed too: the wheel's own steps carry
    their matrices, so one clock owns the room's colour across a level change.
    """
    show, out = built
    functions = _functions(Workspace.load(out).root)

    auto = functions[str(show.master_ids["AUTO"])]
    assert auto.attrib["Type"] == "Collection"
    members = {step.text for step in findall_local(auto, "Step")}
    named = {str(show.master_ids[name]) for name in ("Rueda Colores", "Humo Auto", "Ciclo Energia")}
    assert named <= members
    # Plus what the pixel groups need beside the wheel, which carries their
    # colour inside its own steps: the scene holding their intensity open,
    # and the panels' phase cycle - their own programmes most of the night,
    # a stretch in manual listening to the wheel's RGB (2026-08-28).
    # And the family floors, started first, which a released pick falls back
    # on (ruling D8, 2026-09-27).
    assert {functions[m].attrib["Name"] for m in members - named} == {
        "Pixeles ON",
        "Ciclo Paneles Mixto",
        "Cabezas Suelo",
        "Gobo Suelo",
        "Prisma Suelo",
        "Paneles Suelo",
    }

    cycle = functions[str(show.master_ids["Ciclo Energia"])]
    assert cycle.attrib["Type"] == "Chaser"
    # A wave, not a ramp: the way down from the peak is the dynamic level,
    # party pace with the dimmers taking turns (2026-08-28).
    assert [functions[s.text].attrib["Name"] for s in findall_local(cycle, "Step")] == [
        "Nivel Ambiente",
        "Nivel Fiesta",
        "Nivel Peak",
        "Nivel Fiesta Dinamico",
    ]

    def _names(level):
        collection = functions[str(show.master_ids[level])]
        return {functions[step.text].attrib["Name"] for step in findall_local(collection, "Step")}

    # 2026-08-27, the owner on pressing AUTO and watching parked heads: "el
    # auto es eso, como el modo auto de las cabezas en si". Every level moves
    # from the first second - the quiet one slowly, each family on its own slow
    # envelope - and every level owns its intensity, low or full. The beams
    # held the static fan through this level until 2026-08-29, when the owner
    # watched AUTO and reported them not moving: the hold is four minutes.
    ambient = _names("Nivel Ambiente")
    assert "Movimientos Suaves" in ambient
    assert "Suaves Washes" not in ambient
    assert "Suaves Beams" not in ambient
    assert "Beams Abanico" not in ambient
    assert "Intensidad Ambiente" in ambient

    party = _names("Nivel Fiesta")
    assert {
        "Movimientos Cabezas",
        "Gobo Animacion",
        "Intensidad Total",
    } <= party

    # 2026-08-27: Peak is the one level `Dimmer Chase` actually owns. Before
    # this, `Intensidad Total` ran beside it here too and held every dimmer at
    # 255 - HTP means the chase's dips could never win, so it was cosmetic
    # (TODO.md). `Intensidad Peak` is its replacement: a static owner only for
    # the fixtures the chase cannot reach at all (no dimmer role).
    peak = _names("Nivel Peak")
    assert {"Movimientos Rapidos", "Dimmer Chase", "Intensidad Peak"} <= peak
    assert "Intensidad Total" not in peak
    # Held back for the peak, not running all night.
    assert "Dimmer Chase" not in party
    # And the colour wheel is one wheel over the whole rig, not one per group:
    # three Random wheels never agree, and the heads and the PARs have to.
    wheel = functions[str(show.master_ids["Rueda Colores"])]
    assert wheel.attrib["Type"] == "Chaser"
    assert wheel.attrib["Name"] == "Rueda Colores"


def test_dimmer_chase_owns_peak_and_nothing_is_left_dark(built):
    """2026-08-27: `Dimmer Chase` in Peak was cosmetically dead.

    `intensidad tapada` cannot see this shape at all: it only counts Scene and
    Sequence writes (`rule_shadowed_intensity._dimmer_writes`), on purpose - an
    EFX's actual output is not one knowable value, so the rule treats it as "we
    don't know" rather than risk a false alarm. Sharpening it to count a
    Dimmer-mode EFX as a writer would also light up `Momento Locura`, which
    pairs the very same chase with `Intensidad Total` on purpose and stays that
    way (out of scope here) - a real false positive on a shipped workspace, not
    a missed catch. So the proof lives here instead, at the generator level:
    reproduce the old shape and show analytically that a static 255 - the DMX
    ceiling - shadows every channel the chase could ever write to, then confirm
    the generated Peak no longer pairs them, and that the fixtures the chase
    cannot dim (the MiN Wash - no dimmer role, its light lives behind a shutter
    range) still have an owner so they are not left dark. The full check gate
    over the real shipped shows is `test_check.py`'s.
    """
    from qlctool.checks.driven_channels import driven_channels

    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)
    library = FixtureLibrary.load()
    caps = {c.fixture.fixture_id: c for c in capabilities_of(root, library)}

    # 2026-08-28: the chase went back to the hand-built shape - a Collection
    # of per-family Serial Line cascades - so its writes are the union of its
    # members' (driven_channels returns {} for the Collection itself).
    chase = functions[str(show.master_ids["Dimmer Chase"])]
    chase_writes: dict[int, dict[int, int | None]] = {}
    chase_parts = (
        [functions[step.text] for step in findall_local(chase, "Step")]
        if chase.attrib["Type"] == "Collection"
        else [chase]
    )
    for part in chase_parts:
        for fixture_id, pairs in driven_channels(part, caps, {}).items():
            chase_writes.setdefault(fixture_id, {}).update(pairs)
    assert chase_writes, "the chase should drive at least one fixture's dimmer"

    total = functions[str(show.master_ids["Intensidad Total"])]
    total_writes = driven_channels(total, caps, {})
    # RED, reproduced: for every fixture `Intensidad Total` actually reaches
    # (it deliberately skips the pixel groups and the panels - a separate
    # owner each, unrelated to this bug), the channel the chase drives was
    # also a 255 there - HTP can never show anything but that ceiling.
    shadowed = 0
    for fixture_id, offsets in chase_writes.items():
        if fixture_id not in total_writes:
            continue
        for offset in offsets:
            assert total_writes[fixture_id].get(offset) == 255, (
                "the old bug should still shadow every channel the chase owns"
            )
            shadowed += 1
    assert shadowed, "the chase and `Intensidad Total` should overlap somewhere"

    # GREEN: Peak itself does not carry `Intensidad Total` any more, and
    # nothing else in Peak contests the chase's own channels.
    peak = functions[str(show.master_ids["Nivel Peak"])]
    peak_members = {step.text for step in findall_local(peak, "Step")}
    assert str(show.master_ids["Intensidad Total"]) not in peak_members

    chase_step_id = str(show.master_ids["Dimmer Chase"])
    other_writes: dict[int, dict[int, int | None]] = {}
    for member_id in peak_members - {chase_step_id}:
        for fixture_id, pairs in driven_channels(functions[member_id], caps, {}).items():
            other_writes.setdefault(fixture_id, {}).update(pairs)
    for fixture_id, offsets in chase_writes.items():
        contested = set(offsets) & set(other_writes.get(fixture_id, {}))
        assert not contested, "something besides the chase owns its dimmers"

    # Nothing goes dark: the fixture the chase cannot dim at all (no dimmer
    # role - found by capability, not by name) still has an owner in Peak.
    static_id = show.master_ids.get("Intensidad Peak")
    assert static_id is not None, "Peak needs an owner for fixtures the chase skips"
    static_writes = driven_channels(functions[str(static_id)], caps, {})
    assert static_writes, "the static owner should light at least one fixture"
    # The static owner never bids on a dimmer the chase owns - HTP, the chase's
    # dips could never win. What it does write on the dimmered fixtures is
    # their strobe-off (2026-08-28): a flash released during a chase level
    # used to latch the strobe until the next level's intensity base cleared
    # it, because nothing in the level wrote the channel back.
    # A smoke machine is not in the chase at all, and on a plain fog machine
    # the pump *is* typed as the dimmer - what this level writes there is the
    # pump held shut, which is the point (2026-08-29, `fog_off_pairs`).
    for fixture_id, written in static_writes.items():
        if caps[fixture_id].is_smoke:
            assert set(written) <= set(fog_offsets(caps[fixture_id])), (
                "the static owner touches a smoke machine beyond its pump"
            )
            assert not any(written.values()), "the static owner fires a pump"
            continue
        dimmers = set(caps[fixture_id].offsets_for_role(roles.DIMMER))
        assert not (dimmers & set(written)), "the static owner must not contest the chase's dimmers"
    min_wash_ids = {c.fixture.fixture_id for c in caps.values() if c.fixture.model == "MiN Wash"}
    assert min_wash_ids and min_wash_ids <= static_writes.keys()


def test_only_a_pixel_group_gets_matrices_inside_the_wheel(built):
    """Two chasers that each rotate colour never agree, so there is one clock.

    The bars' colour rides inside the rig-wide wheel: each of its steps starts
    a matrix of the step's own colour over the group that has pixels to draw
    on, and nothing else in AUTO rotates colour - the standalone matrix cycle
    stays on the console for a person, and out of the room states.
    """
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    auto = functions[str(show.master_ids["AUTO"])]
    names = {functions[m.text].attrib["Name"] for m in findall_local(auto, "Step")}
    assert not any(n.startswith("Ciclo Matrices") for n in names)

    wheel = functions[str(show.master_ids["Rueda Colores"])]
    steps = [functions[s.text] for s in findall_local(wheel, "Step")]
    assert steps and all(s.attrib["Type"] == "Collection" for s in steps)
    matrices = [
        functions[member.text]
        for step in steps
        for member in findall_local(step, "Step")
        if functions[member.text].attrib["Type"] == "RGBMatrix"
    ]
    assert len(matrices) == len(steps), "every wheel step colours the pixels"
    pixel_group = next(str(g.group_id) for g in fixture_groups(root) if g.name == "BarrasLed")
    assert {find_local(m, "FixtureGroup").text for m in matrices} == {pixel_group}
    # The step's scene and its matrix state the same colour, by name: the
    # solid steps their own, a contrast step the colour of the "resto". The
    # multicolour steps left this wheel on 2026-09-22 ("los colores siguen
    # siendo una feria", owner) for `Rueda Multicolor`, so every step here
    # has one colour for its matrix to agree on.
    for step, matrix in zip(steps, matrices, strict=True):
        assert not step.attrib["Name"].startswith(("Rig Multicolor", "Rig 4 Colores"))
        colour = step.attrib["Name"].split(" + ")[0].split()[-1]
        assert f" {colour} (Rueda)" in matrix.attrib["Name"], step.attrib["Name"]
    # White is nobody's step: "luz blanca solo para blanco total" (owner,
    # 2026-09-22). The wheels the states run, the simple and the pastel modes.
    for wheel_name in ("Rueda Colores", "Rueda Simples", "Rueda Pastel"):
        wheel = functions[str(show.master_ids[wheel_name])]
        names = [functions[s.text].attrib["Name"] for s in findall_local(wheel, "Step")]
        assert not any("Blanco" in n for n in names), (wheel_name, names)


def test_the_multicolour_looks_rotate_on_a_wheel_no_state_starts(built):
    """2026-09-22: "un modo multicolor solo por si acaso (casi nunca se va a
    usar) y los otros modos con colores sutiles, como mucho 2 mezclas".

    The wild steps - every fixture its own colour, the four-colour deals -
    are a Random wheel of their own, on a button, reachable from neither
    AUTO nor any moment.
    """
    show, out = built
    root = Workspace.load(out).root
    functions = _functions(root)

    wheel = functions[str(show.master_ids["Rueda Multicolor"])]
    assert wheel.attrib["Type"] == "Chaser"
    assert find_local(wheel, "RunOrder").text == "Random"
    names = [functions[s.text].attrib["Name"] for s in findall_local(wheel, "Step")]
    assert len([n for n in names if n.startswith("Rig Multicolor")]) == 2
    assert len([n for n in names if n.startswith("Rig 4 Colores")]) == 4
    assert len(names) == 6

    members = {}
    for function in functions.values():
        if function.attrib["Type"] in ("Collection", "Chaser"):
            members[function.attrib["ID"]] = {s.text for s in findall_local(function, "Step")}

    def reachable(function_id):
        seen, stack = set(), [str(function_id)]
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            stack.extend(members.get(current, ()))
        return seen

    wheel_id = str(show.master_ids["Rueda Multicolor"])
    for state in ("AUTO", "Momento Tranquilo", "Momento Fiesta", "Momento Locura"):
        assert wheel_id not in reachable(show.master_ids[state]), state

    for level in ("Nivel Ambiente", "Nivel Fiesta", "Nivel Peak"):
        collection = functions[str(show.master_ids[level])]
        names = {functions[step.text].attrib["Name"] for step in findall_local(collection, "Step")}
        assert not any(n.startswith("Ciclo Matrices") for n in names), level
