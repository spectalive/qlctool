"""Keep the show's MIDI input patch: name the profile, force omni, touch nothing else.

`Vibra-split.qxw` shipped with no input patch at all, so QLC+ opened it with
nothing listening and every `<Input>` binding in the file was inert until
somebody built the patch by hand in the Inputs/Outputs tab. The other two shows
did carry one - the owner's, `Name="ble device"`, the pad over Bluetooth - and
the first version of this module **overwrote it** with a port name invented
from CoreMIDI's display name. That broke the surface completely (2026-08-29):
QLC+ names a MIDI port by its `kMIDIPropertyModel`, falling back to the display
name (`plugins/midi/src/macx/coremidienumerator.cpp`), so "SINCO
SMC-PAD-Master" matched nothing, the match fell through to the saved line
number, and the universe listened to the wrong port.

The lesson is in the shape of this file now: **which port the pad is on is not
the show's business.** It changes with the night - USB is three ports, Bluetooth
is a fourth called "ble device" - and the workspace is where QLC+ remembers the
one that worked. So an existing patch is left exactly as it is. What this does
set is the two things that *are* the show's business and that a person cannot
be expected to re-pick every time:

- the input profile's name, so QLC+'s tab names the controls; and
- `midichannel="16"`, omni. The pad speaks on MIDI channel 10 for the pads and
  1 for the knobs, so a patch pinned to either channel hears half the surface -
  and QLC+ only ORs the MIDI channel into the input channel number in omni
  mode, which is what makes every number in `smc_pad_device` correct.

A workspace with no patch at all is seeded with the pad's Bluetooth port, which
is how the owner runs it. That is a starting point, not a claim: QLC+ matches
it by name, and re-picking the port in the tab is a normal thing to do.
"""

from lxml import etree

from .constants import QLC_NS
from .generate.input_profile import PROFILE_NAME
from .xmlutil import find_local, iter_local

INPUT_PLUGIN = "MIDI"
# What QLC+ calls the pad's Bluetooth port - its CoreMIDI `Model` property, not
# the display name macOS shows ("SMC-PAD Bluetooth"). Read off the running
# machine 2026-08-29 with the enumerator's own property order.
DEFAULT_LINE_NAME = "ble device"
FALLBACK_LINE = "0"
OMNI_MIDI_CHANNEL = "16"


def pin_midi_input(root: etree._Element) -> None:
    """Give universe 0 a MIDI input patch on the pad's profile, in place.

    An existing patch keeps its plugin, port name, UID and line: only the
    profile and the MIDI channel are ours to state.
    """
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return
    universe = find_local(io_map, "Universe")
    if universe is None:
        return

    patch = find_local(universe, "Input")
    if patch is None:
        patch = etree.Element(
            f"{{{QLC_NS}}}Input",
            Plugin=INPUT_PLUGIN,
            Name=DEFAULT_LINE_NAME,
            UID="",
            Line=FALLBACK_LINE,
        )
        # QLC+ writes the input patch first inside <Universe>, ahead of <Output>.
        universe.insert(0, patch)

    patch.set("Profile", PROFILE_NAME)
    parameters = find_local(patch, "PluginParameters")
    if parameters is None:
        parameters = etree.SubElement(patch, f"{{{QLC_NS}}}PluginParameters")
    parameters.set("midichannel", OMNI_MIDI_CHANNEL)


def midi_input_patch(root: etree._Element) -> etree._Element | None:
    """The universe-0 MIDI input patch, or None if the show has no listener."""
    engine = find_local(root, "Engine")
    io_map = find_local(engine, "InputOutputMap") if engine is not None else None
    if io_map is None:
        return None
    for universe in iter_local(io_map, "Universe"):
        patch = find_local(universe, "Input")
        if patch is not None:
            return patch
    return None
