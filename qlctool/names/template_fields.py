"""The `{field}` names a catalogue value leaves to be filled, in order."""

from string import Formatter


def template_fields(text: str) -> tuple[str, ...]:
    """ "Golpe {colour}" -> ("colour",); a plain name -> ()."""
    return tuple(field for _, field, _, _ in Formatter().parse(text) if field is not None)
