"""The MVR export: the rig as BlenderDMX will draw it (2026-09-23).

The show's 3D view was QLC+'s own until the owner called it unusable - no smoke
plume, gobos as flat textures, a four-head bar drawn as one light - and chose
BlenderDMX. That visualiser reads GDTF and MVR, so the toolkit writes them:
one GDTF per definition, one MVR with every placed fixture. What these tests
hold to is what the picture depends on: every GDTF is one the schema accepts
and pygdtf reads back; a channel's attribute is the one BlenderDMX renders; a
fixture faces the way the QLC+ plot says it does; the package names every
GDTF it references and every address the patch has.

`tests/gdtf.xsd` is the GDTF 1.2 schema as shipped in python-gdtf's tests.
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

import pygdtf
import pymvr
import pytest
from rig_root import RIG_ROOT

from qlctool import roles
from qlctool.definition import Channel, Dimensions, FixtureDefinition
from qlctool.fixture import patched_fixtures
from qlctool.library import FixtureLibrary
from qlctool.monitor_node import MonitorItem
from qlctool.mvr.beam_direction import beam_direction
from qlctool.mvr.build_fixture_type import build_fixture_type
from qlctool.mvr.cie_from_hex import cie_from_hex
from qlctool.mvr.gdtf_attribute import gdtf_attribute
from qlctool.mvr.gdtf_file_name import gdtf_file_name
from qlctool.mvr.gdtf_name import gdtf_name
from qlctool.mvr.monitor_items import monitor_items
from qlctool.mvr.mvr_matrix import mvr_matrix
from qlctool.mvr.write_gdtf import write_gdtf
from qlctool.mvr.write_mvr import write_mvr
from qlctool.workspace import Workspace

REPO = RIG_ROOT
SHOW = REPO / "QLC+ Setups" / "Vibra-split.qxw"
GOBOS = REPO / "QLC+ Setups" / "Gobos"
SCHEMA = Path(__file__).resolve().parent / "gdtf.xsd"
STAGE = (12000.0, 6000.0, 8000.0)


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


@pytest.fixture(scope="module")
def parsed(tmp_path_factory, library):
    """A definition's GDTF as pygdtf reads it back from the written archive."""
    folder = tmp_path_factory.mktemp("gdtf")

    def load(manufacturer, model):
        return pygdtf.FixtureType(str(write_gdtf(library.get(manufacturer, model), folder, GOBOS)))

    return load


@pytest.fixture(scope="module")
def package(tmp_path_factory, library):
    out = tmp_path_factory.mktemp("mvr") / "vibra.mvr"
    return write_mvr(Workspace.load(SHOW), library, out, GOBOS)


def _definition(
    fixture_type="Color Changer", channels=(), heads=(), size=(300, 200, 100), optics=None
):
    names = [c.name for c in channels]
    return FixtureDefinition(
        manufacturer="Test",
        model="Unit",
        fixture_type=fixture_type,
        channels={c.name: c for c in channels},
        modes={"Mode": names},
        heads={"Mode": heads},
        dimensions=Dimensions(*size),
        optics=optics,
    )


def _channel(name, preset=None, group="", caps=()):
    return Channel(
        name=name, role=roles.role_of(preset, group, name), capabilities=tuple(caps), group=group
    )


# --- every definition in the library becomes a GDTF the schema accepts -------


@pytest.mark.parametrize("key", list(FixtureLibrary.load()._by_key), ids=lambda k: f"{k[0]} {k[1]}")
def test_every_definition_writes_a_valid_gdtf(key, library, tmp_path):
    definition = library.get(*key)
    path = write_gdtf(definition, tmp_path, GOBOS)

    with pygdtf.FixtureType(str(path)) as parsed:
        assert [m.name for m in parsed.dmx_modes] == [gdtf_name(m) for m in definition.modes]
        # A primitive has no mesh file, and "None" is not the same as none.
        assert all(model.file_attr == "" for model in parsed.models)
        for mode in parsed.dmx_modes:
            # Every DMX offset of the QLC+ mode is covered exactly once.
            offsets = sorted(o for ch in mode.dmx_channels for o in ch.offset)
            assert offsets == list(range(1, len(definition.modes[mode.name]) + 1))

    if shutil.which("xmllint") is None:
        pytest.skip("xmllint not available to validate against the schema")
    with zipfile.ZipFile(path) as archive:
        description = tmp_path / f"{path.stem}.xml"
        description.write_bytes(archive.read("description.xml"))
    subprocess.run(
        ["xmllint", "--noout", "--schema", str(SCHEMA), str(description)],
        check=True,
        capture_output=True,
    )


# --- attributes: what BlenderDMX renders ------------------------------------


def test_channels_map_to_the_attributes_a_visualiser_renders():
    assert gdtf_attribute(_channel("Red", "IntensityRed")) == "ColorAdd_R"
    assert gdtf_attribute(_channel("Dimmer", "IntensityMasterDimmer")) == "Dimmer"
    assert gdtf_attribute(_channel("Pan", "PositionPan")) == "Pan"
    assert gdtf_attribute(_channel("Strobe", "ShutterStrobeSlowFast")) == "Shutter1"
    assert gdtf_attribute(_channel("Gobo Wheel", group="Gobo")) == "Gobo1"
    assert gdtf_attribute(_channel("Color Wheel", group="Colour")) == "Color1"
    assert gdtf_attribute(_channel("Zoom", "BeamZoomSmallBig")) == "Zoom"
    # The pump of a fog machine is not a light, and GDTF has no name for it.
    assert gdtf_attribute(_channel("Fog", group="Effect")) == "NoFeature"


def test_the_7r_gobo_wheel_carries_its_eighteen_images(library):
    built = build_fixture_type(library.get("Generic", "BEAM 230W 7R"), GOBOS)
    wheels = {w.name: w for w in built.fixture_type.wheels}
    gobos = next(w for name, w in wheels.items() if name.startswith("Gobo"))
    assert len(gobos.wheel_slots) == 18
    assert all(slot.media_file_name is not None for slot in gobos.wheel_slots)
    assert len(built.media) == 18
    colours = next(w for name, w in wheels.items() if name.startswith("Color"))
    assert colours.wheel_slots[1].name == "Red"
    red = colours.wheel_slots[1].color
    assert red.x > 0.6 and red.y > 0.3


def test_a_shutter_channel_becomes_closed_open_and_strobe_functions(parsed):
    mode = parsed("Generic", "BEAM 230W 7R").dmx_modes[0]
    strobe = next(ch for ch in mode.dmx_channels if ch.offset == [6])
    functions = [
        (f.attribute.str_link, f.dmx_from.value)
        for f in strobe.logical_channels[0].channel_functions
    ]
    assert functions == [("Shutter1", 0), ("Shutter1Strobe", 51), ("Shutter1", 241)]
    closed = strobe.logical_channels[0].channel_functions[0].channel_sets[0]
    assert closed.name == "Closed" and closed.physical_from.value == 0.0


def test_pan_and_fine_pan_fold_into_one_sixteen_bit_channel(parsed):
    mode = parsed("Generic", "BEAM 230W 7R").dmx_modes[0]
    pan = next(ch for ch in mode.dmx_channels if ch.geometry == "Yoke")
    assert pan.offset == [1, 3]
    function = pan.logical_channels[0].channel_functions[0]
    assert (function.physical_from.value, function.physical_to.value) == (-270.0, 270.0)
    assert function.default.value == 128


def test_each_head_of_a_pixel_bar_drives_its_own_beam(parsed):
    fixture = parsed("Stairville", "LED Bar 240/8 RGB")
    mode = next(m for m in fixture.dmx_modes if m.name == "24-channel")
    assert [ch.geometry for ch in mode.dmx_channels] == [
        f"Beam{i}" for i in range(1, 9) for _ in range(3)
    ]
    beams = list(fixture.geometries[0].geometries)
    assert len(beams) == 8
    xs = [g.position.matrix[0][3] for g in beams]
    assert xs == sorted(xs) and xs[0] < 0 < xs[-1]


def test_names_are_held_to_the_schema_character_class():
    assert gdtf_name("Strobe (slow → fast)") == "Strobe (slow fast)"
    assert gdtf_name("Gobo 1 + prism, 50%") == "Gobo 1 + prism, 50%"
    assert gdtf_name("→") == "Unnamed"


def test_hex_colours_land_on_cie_chromaticity():
    white = cie_from_hex("#ffffff")
    assert (round(white.x, 3), round(white.y, 3), round(white.Y)) == (0.313, 0.329, 100)
    assert cie_from_hex("#000000").Y == 0.0
    assert cie_from_hex("garbage").Y == 100.0


# --- placement: which way each fixture faces --------------------------------


def _mesh():
    return _definition("Color Changer", [_channel("Red", "IntensityRed")])


def test_a_hanging_par_at_zero_points_at_the_floor():
    direction = beam_direction(mvr_matrix(MonitorItem(1, 0, 4000, 0), _mesh(), STAGE))
    assert direction == (0.0, 0.0, -1.0)


def test_a_truss_par_at_fifty_leans_out_over_the_audience():
    # The rule beam_landing derives from QLC+'s renderer: positive x_rot on a
    # meshed fixture points it downstage. Audience is -y in MVR.
    x, y, z = beam_direction(mvr_matrix(MonitorItem(1, 0, 4000, 0, x_rot=50), _mesh(), STAGE))
    assert y < 0 and z < 0 and x == 0.0


def test_a_pixel_bar_at_minus_ninety_faces_the_room():
    bar = _definition("LED Bar (Pixels)", [_channel("Red", "IntensityRed")])
    assert beam_direction(mvr_matrix(MonitorItem(1, 0, 3000, 0, x_rot=-90), bar, STAGE)) == (
        0.0,
        -1.0,
        0.0,
    )


def test_a_mover_standing_on_the_floor_points_up():
    mover = _definition(
        "Moving Head", [_channel("Pan", "PositionPan"), _channel("Tilt", "PositionTilt")]
    )
    assert beam_direction(mvr_matrix(MonitorItem(1, 0, 0, 0, x_rot=180), mover, STAGE)) == (
        0.0,
        0.0,
        1.0,
    )


def test_a_smoke_machine_is_a_box_on_the_floor():
    smoke = _definition("Smoke", [_channel("Fog", group="Effect")])
    assert beam_direction(mvr_matrix(MonitorItem(1, 0, 0, 0), smoke, STAGE)) == (0.0, 0.0, 1.0)


def test_positions_are_centred_on_the_stage_in_millimetres():
    # Near corner (0,0,0) of a 300 x 200 x 100 box on a 12 x 6 x 8 m stage.
    matrix = mvr_matrix(MonitorItem(1, 0, 0, 0, x_rot=180), _mesh(), STAGE)
    x, y, z, _ = matrix.matrix[3]
    assert (x, y, z) == (-6000 + 150, 4000 - 50, 0.0)


# --- the package ------------------------------------------------------------


def test_the_package_places_every_rigged_fixture_with_its_address(package, library):
    root = Workspace.load(SHOW).root
    placed = monitor_items(root)
    rigged = {i.fixture_id for i in placed.items if not i.hidden}
    patched = {f.fixture_id: f for f in patched_fixtures(root)}
    assert len(package.fixtures) == len(rigged)

    with zipfile.ZipFile(package.path) as archive:
        names = set(archive.namelist())
    scene = pymvr.GeneralSceneDescription(str(package.path))
    fixtures = scene.scene.layers[0].child_list.fixtures
    assert len(fixtures) == len(rigged)
    for fixture in fixtures:
        assert fixture.gdtf_spec in names
        original = patched[int(fixture.fixture_id)]
        address = fixture.addresses.addresses[0]
        assert (address.universe, address.address) == (original.universe + 1, original.address + 1)
        assert fixture.gdtf_mode == gdtf_name(original.mode)
        assert fixture.gdtf_spec == gdtf_file_name(
            library.get(original.manufacturer, original.model)
        )


def test_spares_stay_out_and_are_reported(package):
    assert all("hidden spare" in why for why in package.skipped.values())
    assert any(name.startswith("CromoWash100") for name in package.skipped)
