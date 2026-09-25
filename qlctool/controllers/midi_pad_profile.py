"""A MIDI pad the console can be bound to."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from lxml import etree

from ..argb import RGB


@dataclass(frozen=True)
class MidiPadProfile:
    """Its map (identifier -> input channel), its button colours, how to patch its input."""

    name: str
    bindings: Mapping[str, int]
    colors: Mapping[str, RGB]
    pin_input: Callable[[etree._Element], None]
