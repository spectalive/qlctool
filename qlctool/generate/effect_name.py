"""The name a built-in panel effect is shown under."""

import re

from ..names.names import Names

# A definition that only numbers its effects ("Effect 7") says nothing a
# translation would lose, so the show's own word for it is used instead.
_NUMBERED = re.compile(r"effect\s*(\d+)", re.IGNORECASE)


def effect_name(raw: str, number: int, vocabulary: Names) -> str:
    """The definition's effect name, or the show's "Effect {number}" when it has none of its own."""
    name = raw.strip()
    numbered = _NUMBERED.fullmatch(name)
    if numbered:
        return vocabulary.render("panel_effect", number=int(numbered.group(1)))
    return name or vocabulary.render("panel_effect", number=number)
