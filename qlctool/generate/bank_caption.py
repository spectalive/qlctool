"""The caption a colour bank button wears: the colour's short form.

Moved verbatim out of `live_console` (2026-09-27 split).
"""

from collections.abc import Mapping


def bank_caption(name: str, short_colour: Mapping[str, str]) -> str:
    """ "Rojo BarrasLed" is a red button in the bars' bank: it says "Rojo"."""
    first = name.split(" ", maxsplit=1)[0] if name else ""
    return short_colour.get(first, first)
