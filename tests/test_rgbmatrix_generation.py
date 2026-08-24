"""RGBMatrix builder and the algorithm x colour generator, against the real show.

Two guarantees here. First, the builder can reproduce every one of the 122
RGBMatrix functions in the production workspace node for node - so its element
order, attributes and colour encoding are what QLC+ actually wrote. Second, the
generator injects the cross-product without touching anything that was there.
"""

from pathlib import Path

import pytest

from qlctool.argb import argb_from_rgb, rgb_from_argb
from qlctool.color_format import INDEXED, LEGACY, color_format_of
from qlctool.constants import ALL_FIXTURES_GROUP
from qlctool.fixture_group import fixture_groups
from qlctool.functions.rgbmatrix import build_rgbmatrix
from qlctool.generate.matrix_effects import generate_matrix_effects
from qlctool.ids import existing_function_ids
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


def _matrices(root):
    return [
        f for f in iter_local(root, "Function")
        if f.attrib.get("Type") == "RGBMatrix"
    ]


def _text_of(parent, name):
    element = find_local(parent, name)
    return None if element is None else (element.text or "").strip()


def test_argb_round_trip():
    # The two colours the show writes most often, from real MonoColor values.
    assert argb_from_rgb((255, 0, 0)) == 4294901760
    assert argb_from_rgb((0, 0, 255)) == 4278190335
    assert rgb_from_argb(4294901760) == (255, 0, 0)
    assert rgb_from_argb(4278190335) == (0, 0, 255)


@pytest.mark.parametrize("show", ALL_FORMATS, ids=lambda p: p.stem)
def test_builder_reproduces_every_real_matrix(show):
    root = Workspace.load(show).root
    originals = _matrices(root)
    assert len(originals) == 122

    for original in originals:
        speed = find_local(original, "Speed")
        algorithm_element = find_local(original, "Algorithm")
        algorithm = (
            None if algorithm_element.attrib["Type"] == "Plain"
            else (algorithm_element.text or "").strip()
        )
        indexed = [c for c in original if c.tag.endswith("}Color")]
        if indexed:
            mono_text = (indexed[0].text or "").strip()
            end_color = (
                (indexed[1].text or "").strip() if len(indexed) > 1 else None
            )
        else:
            mono_text = _text_of(original, "MonoColor")
            end_color = _text_of(original, "EndColor")
        rebuilt = build_rgbmatrix(
            int(original.attrib["ID"]),
            original.attrib["Name"],
            algorithm=algorithm,
            mono_color=rgb_from_argb(int(mono_text)),
            group_id=int(_text_of(original, "FixtureGroup")),
            end_color=None if end_color is None else rgb_from_argb(int(end_color)),
            control_mode=_text_of(original, "ControlMode"),
            direction=_text_of(original, "Direction"),
            run_order=_text_of(original, "RunOrder"),
            fade_in=int(speed.attrib["FadeIn"]),
            fade_out=int(speed.attrib["FadeOut"]),
            duration=int(speed.attrib["Duration"]),
            properties={
                p.attrib["Name"]: p.attrib["Value"]
                for p in findall_local(original, "Property")
            },
            color_format=INDEXED if indexed else LEGACY,
            path=original.attrib.get("Path"),
        )
        diff = first_difference(original, rebuilt)
        assert diff is None, f"{original.attrib['Name']}: {diff}"


def test_plain_algorithm_has_no_text():
    matrix = build_rgbmatrix(9000, "Solid", algorithm=None, mono_color=(1, 2, 3))
    algorithm = find_local(matrix, "Algorithm")
    assert algorithm.attrib["Type"] == "Plain"
    assert (algorithm.text or "") == ""
    assert find_local(matrix, "EndColor") is None
    assert _text_of(matrix, "FixtureGroup") == str(ALL_FIXTURES_GROUP)


def test_fixture_groups_read_only_definitions():
    root = Workspace.load(SHOW).root
    groups = fixture_groups(root)
    # The show defines three groups; the other 122 <FixtureGroup> nodes are
    # plain ID references inside RGBMatrix functions.
    assert [(g.group_id, g.name) for g in groups] == [
        (0, "BarrasLed"), (1, "Cabezas"), (2, "PAR")
    ]
    bars = groups[0]
    assert (bars.width, bars.height) == (8, 2)
    assert bars.head_count > 0


def test_generate_matrix_effects_into_real_show(tmp_path):
    ws = Workspace.load(SHOW)
    before_ids = existing_function_ids(ws.root)
    before_count = len(_matrices(ws.root))

    algorithms = ["Strobe", "Waves", None]
    palette = {"Rojo": (255, 0, 0), "Azul": (0, 0, 255)}
    result = generate_matrix_effects(
        ws, group_id=0, algorithms=algorithms, palette=palette
    )

    assert len(result.matrix_ids) == len(algorithms) * len(palette)
    new_ids = set(result.matrix_ids) | {result.chaser_id}
    assert len(new_ids) == len(result.matrix_ids) + 1
    assert new_ids.isdisjoint(before_ids)

    out = tmp_path / "out.qxw"
    ws.save(out)
    reloaded = Workspace.load(out).root

    matrices = _matrices(reloaded)
    assert len(matrices) == before_count + len(result.matrix_ids)

    generated = {
        m.attrib["Name"]: m
        for m in matrices
        if int(m.attrib["ID"]) in set(result.matrix_ids)
    }
    assert "BarrasLed - Strobe Rojo" in generated
    assert "BarrasLed - Solid Azul" in generated

    strobe = generated["BarrasLed - Strobe Rojo"]
    assert _text_of(strobe, "MonoColor") == str(argb_from_rgb((255, 0, 0)))
    assert _text_of(strobe, "FixtureGroup") == "0"
    assert _text_of(strobe, "ControlMode") == "RGB"
    assert strobe.attrib["Path"] == "Matrices (generado)"

    chaser = next(
        f for f in iter_local(reloaded, "Function")
        if f.attrib.get("ID") == str(result.chaser_id)
    )
    steps = findall_local(chaser, "Step")
    assert [s.text for s in steps] == [str(i) for i in result.matrix_ids]


def test_generate_rejects_unknown_group():
    ws = Workspace.load(SHOW)
    with pytest.raises(ValueError, match="no fixture group 99"):
        generate_matrix_effects(ws, group_id=99, algorithms=["Fill"])


@pytest.mark.parametrize(
    "show,expected",
    [(ALL_FORMATS[0], LEGACY), (ALL_FORMATS[1], INDEXED), (ALL_FORMATS[2], INDEXED)],
    ids=lambda value: getattr(value, "stem", value),
)
def test_colour_format_is_detected_per_show(show, expected):
    assert color_format_of(Workspace.load(show).root) == expected


def test_generation_matches_the_target_show_colour_shape(tmp_path):
    """A matrix generated into a 4.14+ show must use <Color Index>, not
    <MonoColor> - QLC+ still reads the old shape, but a file that mixes both is
    a trap for the next reader."""
    ws = Workspace.load(ALL_FORMATS[2])  # saved by QLC+ 5.2.2
    result = generate_matrix_effects(
        ws, group_id=0, algorithms=["Strobe"], palette={"Rojo": (255, 0, 0)}
    )
    out = tmp_path / "out.qxw"
    ws.save(out)

    generated = next(
        f for f in _matrices(Workspace.load(out).root)
        if int(f.attrib["ID"]) == result.matrix_ids[0]
    )
    colors = [c for c in generated if c.tag.endswith("}Color")]
    assert [c.attrib["Index"] for c in colors] == ["0"]
    assert colors[0].text == str(argb_from_rgb((255, 0, 0)))
    assert find_local(generated, "MonoColor") is None
