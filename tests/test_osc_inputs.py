"""The console bound to an OSC surface, opt-in (2026-10-28).

dmxdesk's OSC adapter drove the test QLC+ on :9997 by address, and the console
had to be bound by hand in QLC+'s input tab first: nothing in a generated show
listened. `[controllers] osc` now gives the show an OSC universe and binds
every button, slider and speed dial to `<prefix>/<id>` - the addresses the desk
sends - while a show that does not ask stays exactly as it was. The vectors
are the ones dmxdesk's converter was checked against.
"""

import copy
from dataclasses import replace
from types import SimpleNamespace

import pytest
from lxml import etree
from rig_root import RIG_ROOT

from qlctool.checks.check_workspace import check_workspace
from qlctool.checks.osc_bindings import osc_bindings
from qlctool.checks.pad_bindings import pad_bindings
from qlctool.checks.rule_osc_input import check_osc_input
from qlctool.checks.rule_providers import rule_providers
from qlctool.constants import QLC_NS
from qlctool.controllers.bind_osc_inputs import bind_osc_inputs
from qlctool.controllers.osc_channel import osc_channel
from qlctool.controllers.osc_dial_factor_inputs import OSC_DIAL_FACTOR_INPUTS
from qlctool.controllers.pin_osc_input import pin_osc_input
from qlctool.description.controller_settings import ControllerSettings
from qlctool.description.reading.read_controllers import read_controllers
from qlctool.find_local import find_local
from qlctool.findall_local import findall_local
from qlctool.fixture_library import FixtureLibrary
from qlctool.generate.add_osc_inputs import add_osc_inputs
from qlctool.generate.build_canonical_show import build_canonical_show
from qlctool.localname import localname
from qlctool.midi_input_patch import midi_input_patch
from qlctool.osc_input_universe import osc_input_universe
from qlctool.qlcplus_binary import qlcplus_binary
from qlctool.validate_workspace import validate_workspace
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace

SHOW = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
PREFIX = "/desk"


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


def _built(library, controllers):
    workspace = Workspace.load(SHOW)
    description = replace(vibra_description(), controllers=controllers)
    build_canonical_show(workspace, library, description=description)
    return workspace


@pytest.fixture(scope="module")
def plain(library):
    return _built(library, vibra_description().controllers)


@pytest.fixture(scope="module")
def bound(library):
    return _built(library, replace(vibra_description().controllers, osc=PREFIX))


def _controls(root):
    console = find_local(root, "VirtualConsole")
    return [w for w in console.iter() if localname(w) in ("Button", "Slider", "SpeedDial")]


def _osc_sources(widget, universe):
    return {
        int(s.get("ID")): int(s.get("Channel"))
        for s in findall_local(widget, "Input")
        if s.get("Universe") == str(universe) and "Channel" in s.attrib
    }


def test_the_channel_is_qlcplus_hash_of_the_address():
    assert osc_channel("/vibra/33") == 32623
    assert osc_channel("/vibra/33/x2") == 40739
    assert osc_channel("/vibra/33/x6") == 55559
    assert osc_channel("/vibra/33/x10") == 63637


def test_the_prefix_is_read_and_checked():
    assert read_controllers({"osc": "/desk"}, "show.toml").osc == "/desk"
    assert read_controllers({}, "show.toml").osc is None
    for wrong in ("desk", "/desk/", "/", "/a b", "/a#b", "//desk", 3):
        with pytest.raises(ValueError, match="osc"):
            read_controllers({"osc": wrong}, "show.toml")


def test_vibra_does_not_ask_for_osc(plain):
    assert vibra_description().controllers.osc is None
    assert osc_input_universe(plain.root) is None


def test_the_osc_universe_comes_after_the_pads(bound):
    universe = osc_input_universe(bound.root)
    assert universe == 1
    patch = midi_input_patch(bound.root)
    assert patch is not None and patch.get("Plugin") == "MIDI"
    assert patch.getparent().get("ID") == "0"
    io_map = find_local(find_local(bound.root, "Engine"), "InputOutputMap")
    osc = [u for u in findall_local(io_map, "Universe") if u.get("ID") == "1"]
    assert len(osc) == 1
    inputs = findall_local(osc[0], "Input")
    assert [(i.get("Plugin"), i.get("Name"), i.get("Line")) for i in inputs] == [
        ("OSC", "127.0.0.1", "0")
    ]
    assert pin_osc_input(bound.root) == 1


def test_every_control_has_its_address(bound):
    controls = _controls(bound.root)
    assert len(controls) > 100
    for widget in controls:
        address = f"{PREFIX}/{widget.get('ID')}"
        expected = {0: osc_channel(address)}
        if localname(widget) == "SpeedDial":
            for factor, source in OSC_DIAL_FACTOR_INPUTS.items():
                expected[source] = osc_channel(f"{address}/x{factor}")
        assert _osc_sources(widget, 1) == expected, widget.get("Caption")


def test_the_pad_keeps_every_binding(plain, bound):
    assert pad_bindings(bound.root) == pad_bindings(plain.root)


def test_the_bound_show_passes_every_check(bound, library):
    osc = [p for p in rule_providers() if p.name == "osc"]
    assert osc and osc[0].applies(bound.root)
    assert check_workspace(bound, library) == []


def test_an_osc_only_show_wakes_no_pad_rule(library):
    workspace = _built(library, ControllerSettings(osc=PREFIX))
    pad = next(p for p in rule_providers() if p.name == "smc-pad")
    # The source file's own MIDI patch survives the strip; nothing is bound to it.
    assert osc_input_universe(workspace.root) == 1
    assert not pad_bindings(workspace.root)
    assert not pad.applies(workspace.root)
    assert check_workspace(workspace, library) == []


def test_two_controls_on_one_channel_are_caught(bound, library):
    """The regression: two addresses hashing to one channel press two controls."""
    workspace = copy.deepcopy(bound)
    first, second = _controls(workspace.root)[:2]
    taken = _osc_sources(first, 1)[0]
    for source in findall_local(second, "Input"):
        if source.get("Universe") == "1" and source.get("ID") == "0":
            source.set("Channel", str(taken))
    assert taken in osc_bindings(workspace.root, 1)
    findings = check_workspace(workspace, library)
    assert [(f.rule_id, f.fields["channel"]) for f in findings] == [
        ("osc_control_bound_twice", taken)
    ]


@pytest.mark.skipif(qlcplus_binary() is None, reason="QLC+ is not installed on this machine")
def test_qlcplus_loads_the_bound_show(bound, tmp_path):
    out = tmp_path / "osc.qxw"
    bound.save(out)
    assert validate_workspace(out).ok


def test_a_workspace_with_nowhere_to_listen_gets_nothing():
    """No `<InputOutputMap>`, no console: nothing to patch, bind or check."""
    bare = etree.fromstring(f'<Workspace xmlns="{QLC_NS}"><Engine/></Workspace>')
    assert pin_osc_input(bare) is None
    assert bind_osc_inputs(bare, PREFIX, 1) == 0
    assert check_osc_input(bare) == []
    build = SimpleNamespace(
        described=SimpleNamespace(controllers=ControllerSettings(osc=PREFIX)),
        workspace=SimpleNamespace(root=bare),
    )
    assert add_osc_inputs(build) == 0


def test_an_empty_map_gets_universe_zero():
    root = etree.fromstring(
        f'<Workspace xmlns="{QLC_NS}"><Engine><InputOutputMap/></Engine></Workspace>'
    )
    assert pin_osc_input(root) == 0
    assert osc_input_universe(root) == 0
