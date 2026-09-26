"""The universe whose input the pad's bindings arrive on."""

from lxml import etree

from .input_binding import midi_input_patch

# Where `pin_midi_input` seeds the pad's patch, and where `build_input_source`
# binds a widget by default.
DEFAULT_UNIVERSE = 0


def pad_input_universe(root: etree._Element) -> int:
    """The id of the universe carrying the show's MIDI input patch, or universe 0 without one.

    A show whose patch was lost still binds on universe 0, which is what
    `rule_pad_input` must see to say the surface is dead.
    """
    patch = midi_input_patch(root)
    universe = patch.getparent() if patch is not None else None
    if universe is None:
        return DEFAULT_UNIVERSE
    return int(universe.get("ID", str(DEFAULT_UNIVERSE)))
