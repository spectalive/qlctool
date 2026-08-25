"""EFX builder and the movement generator, against the real show.

Same two guarantees as the RGBMatrix suite: the builder reproduces all 30 EFX
functions in the production workspace node for node, and the generator injects
new movement without disturbing what is there.
"""

from pathlib import Path

import pytest

from qlctool.efx_algorithms import EFX_ALGORITHMS
from qlctool.functions.efx import EFXAxis, EFXFixture, build_efx
from qlctool.generate.movement_efx import (
    generate_movement_efx,
    moving_head_ids,
    spread_offsets,
)
from qlctool.ids import existing_function_ids
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace
from qlctool.xmlsemantics import first_difference
from qlctool.xmlutil import find_local, findall_local, iter_local

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"
# The same show as saved by three QLC+ versions: 4.13.1 (SHOW), 4.14.3 and
# 5.2.2. Each writes the schema slightly differently, and the builders must
# reproduce all of them.
ALL_FORMATS = [
    SHOW,
    REPO / "QLC+ Setups" / "DeluxeEventos2_qlc4143.qxw",
    REPO / "QLC+ Setups" / "DeluxeEventos2_qlcv5.qxw",
]


def _efx(root):
    return [
        f for f in iter_local(root, "Function") if f.attrib.get("Type") == "EFX"
    ]


def _text_of(parent, name):
    element = find_local(parent, name)
    return None if element is None else (element.text or "").strip()


def _axis(function, name):
    for element in findall_local(function, "Axis"):
        if element.attrib.get("Name") == name:
            return EFXAxis(
                offset=int(_text_of(element, "Offset")),
                frequency=int(_text_of(element, "Frequency")),
                phase=int(_text_of(element, "Phase")),
            )
    raise AssertionError(f"no {name} axis")


@pytest.mark.parametrize("show", ALL_FORMATS, ids=lambda p: p.stem)
def test_builder_reproduces_every_real_efx(show):
    root = Workspace.load(show).root
    originals = _efx(root)
    assert len(originals) == 30

    for original in originals:
        members = [
            EFXFixture(
                fixture_id=int(_text_of(element, "ID")),
                head=int(_text_of(element, "Head")),
                mode=int(_text_of(element, "Mode")),
                direction=_text_of(element, "Direction"),
                start_offset=int(_text_of(element, "StartOffset")),
            )
            for element in findall_local(original, "Fixture")
        ]
        speed = find_local(original, "Speed")
        # <Direction>/<StartOffset> also appear inside <Fixture>; the EFX-level
        # ones are the direct children, which find_local returns first only
        # because the Fixture blocks are nested - read them explicitly.
        top = [c for c in original]
        efx_direction = next(
            c for c in top if c.tag.endswith("}Direction")
        ).text.strip()
        efx_start_offset = [
            c for c in top if c.tag.endswith("}StartOffset")
        ][0].text.strip()

        rebuilt = build_efx(
            int(original.attrib["ID"]),
            original.attrib["Name"],
            members,
            algorithm=_text_of(original, "Algorithm"),
            x_axis=_axis(original, "X"),
            y_axis=_axis(original, "Y"),
            width=int(_text_of(original, "Width")),
            height=int(_text_of(original, "Height")),
            rotation=int(_text_of(original, "Rotation")),
            start_offset=int(efx_start_offset),
            is_relative=int(_text_of(original, "IsRelative")),
            propagation_mode=_text_of(original, "PropagationMode"),
            direction=efx_direction,
            run_order=_text_of(original, "RunOrder"),
            fade_in=int(speed.attrib["FadeIn"]),
            fade_out=int(speed.attrib["FadeOut"]),
            duration=int(speed.attrib["Duration"]),
            path=original.attrib.get("Path"),
        )
        diff = first_difference(original, rebuilt)
        assert diff is None, f"{original.attrib['Name']}: {diff}"


def test_spread_offsets_is_even_and_wrapped():
    assert spread_offsets(0) == []
    assert spread_offsets(1) == [0]
    assert spread_offsets(2) == [0, 180]
    assert spread_offsets(4) == [0, 90, 180, 270]
    assert all(0 <= o < 360 for o in spread_offsets(7))


def test_moving_heads_found_in_real_show():
    ws = Workspace.load(SHOW)
    ids = moving_head_ids(ws, FixtureLibrary.load())
    # 4 BEAM 230W 7R + 2 LED Beam Mini + 4 CromoWash100 + 2 Chauvet MiN Wash:
    # every one is a moving head. Cross-check against the fixtures the show's
    # own hand-built EFX drives - capability selection must find the same set.
    assert len(ids) == 12
    assert len(set(ids)) == len(ids)

    hand_built = next(
        f for f in _efx(ws.root) if f.attrib["Name"] == "Movimiento Circulo"
    )
    assert set(ids) == {
        int(_text_of(m, "ID")) for m in findall_local(hand_built, "Fixture")
    }


def test_generate_movement_into_real_show(tmp_path):
    ws = Workspace.load(SHOW)
    library = FixtureLibrary.load()
    before_ids = existing_function_ids(ws.root)
    before_count = len(_efx(ws.root))

    result = generate_movement_efx(ws, library)

    assert len(result.efx_ids) == len(EFX_ALGORITHMS)
    new_ids = set(result.efx_ids) | {result.chaser_id}
    assert new_ids.isdisjoint(before_ids)

    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    # This rig holds both kinds of mover, so each shape is a Collection over two
    # EFX - see test_pan_tilt_pairing for why they cannot share one.
    functions = _efx(reloaded)
    assert len(functions) == before_count + len(result.part_ids)

    by_name = {
        f.attrib["Name"]: f
        for f in functions
        if int(f.attrib["ID"]) in set(result.part_ids)
    }
    assert "Movimiento Circulo (16 bit)" in by_name
    assert "Movimiento Circulo (8 bit)" in by_name

    paired = by_name["Movimiento Circulo (16 bit)"]
    unpaired = by_name["Movimiento Circulo (8 bit)"]
    members = findall_local(paired, "Fixture")
    assert len(members) == 8
    assert len(findall_local(unpaired, "Fixture")) == 4
    offsets = [int(_text_of(m, "StartOffset")) for m in members]
    assert offsets == [45 * step for step in range(8)]
    assert _text_of(paired, "PropagationMode") == "Parallel"
    assert paired.attrib["Path"] == "Movimiento (generado)/Partes"

    # What the console and the chaser see is still one function per shape.
    collection = next(
        f for f in iter_local(reloaded, "Function")
        if f.attrib.get("Name") == "Movimiento Circulo"
        and f.attrib.get("Type") == "Collection"
    )
    assert int(collection.attrib["ID"]) in set(result.efx_ids)

    chaser = next(
        f for f in iter_local(reloaded, "Function")
        if f.attrib.get("ID") == str(result.chaser_id)
    )
    assert [s.text for s in findall_local(chaser, "Step")] == [
        str(i) for i in result.efx_ids
    ]


def test_generate_rejects_workspace_without_movers():
    ws = Workspace.load(SHOW)
    with pytest.raises(ValueError, match="pan and tilt"):
        generate_movement_efx(ws, FixtureLibrary.load(), fixture_ids=[])
