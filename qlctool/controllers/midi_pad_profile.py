"""A MIDI pad the console can be bound to."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from lxml import etree

from ..argb import RGB


@dataclass(frozen=True)
class MidiPadProfile:
    """Its map (widget name -> input channel), its button colours, and how to patch its input."""

    name: str
    bindings: Mapping[str, int]
    colors: Mapping[str, RGB]
    pin_input: Callable[[etree._Element], None]
