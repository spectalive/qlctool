"""The input profile the repo ships is the map the show is bound to.

2026-08-29: the two had drifted. The profile still declared the pad's factory
notes 4-19 and a SHIFT bank at 52-67, while every binding in the workspaces was
on 36-51 - so QLC+'s input tab named the wrong control for all sixteen pads,
and the profile was quietly useless as documentation. Generating it removes the
chance of that; this file is what makes the shipped copy stay generated.
"""

from pathlib import Path

from lxml import etree

from qlctool.generate.input_profile import PROFILE_NAME, build_input_profile
from qlctool.generate.smc_pad_bindings import SMC_PAD_BINDINGS
from qlctool.generate.smc_pad_device import pad_channel
from qlctool.input_binding import INPUT_LINE_NAME, pin_midi_input
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, localname

REPO = Path(__file__).resolve().parents[3]
SHIPPED = REPO / "QLC+ InputProfiles" / "M-VAVE-SMC-PAD.qxi"


def _channels(profile: bytes) -> dict[int, str]:
    root = etree.fromstring(profile)
    return {
        int(channel.attrib["Number"]): find_local(channel, "Name").text
        for channel in root.iter()
        if localname(channel) == "Channel"
    }


def test_the_shipped_profile_is_the_generated_one():
    assert SHIPPED.read_bytes() == build_input_profile(), (
        "the shipped profile drifted from smc_pad_device - regenerate it with "
        "`qlctool input-profile 'QLC+ InputProfiles/M-VAVE-SMC-PAD.qxi'`"
    )


def test_every_binding_the_show_uses_is_a_control_the_profile_declares():
    """The drift that started this: a binding the profile could not name."""
    declared = _channels(build_input_profile())
    for name, channel in SMC_PAD_BINDINGS.items():
        assert channel in declared, f"{name} is bound to unnamed channel {channel}"


def test_the_pads_are_named_the_way_the_panel_is_printed():
    """PAD1 bottom-left, PAD13 top-left - measured 2026-08-29, notes 36/48."""
    declared = _channels(build_input_profile())
    assert declared[pad_channel(1)] == "Pad 1"
    assert declared[pad_channel(13)] == "Pad 13"
    assert declared[pad_channel(13, bank=2)] == "Banco 2 - Pad 13"


def test_the_workspaces_patch_the_pad_in_with_that_profile():
    """A binding is inert until a universe declares the input plugin."""
    for name in ("Vibra.qxw", "Vibra-beats.qxw", "Vibra-split.qxw"):
        root = Workspace.load(REPO / "QLC+ Setups" / name).root
        universe = find_local(
            find_local(find_local(root, "Engine"), "InputOutputMap"), "Universe"
        )
        patch = find_local(universe, "Input")
        assert patch is not None, f"{name} has no MIDI input patch"
        assert patch.attrib["Profile"] == PROFILE_NAME, name
        assert patch.attrib["Name"] == INPUT_LINE_NAME, name
        parameters = find_local(patch, "PluginParameters")
        # Omni, or QLC+ never ORs the MIDI channel into the channel number and
        # every pad binding in the file addresses the wrong control.
        assert parameters.attrib["midichannel"] == "16", name


def test_patching_twice_leaves_one_input():
    """Regenerating over a file QLC+ already patched must not stack patches."""
    workspace = Workspace.load(REPO / "QLC+ Setups" / "Vibra-split.qxw")
    pin_midi_input(workspace.root)
    pin_midi_input(workspace.root)
    universe = find_local(
        find_local(find_local(workspace.root, "Engine"), "InputOutputMap"), "Universe"
    )
    inputs = [child for child in universe if localname(child) == "Input"]
    assert len(inputs) == 1
