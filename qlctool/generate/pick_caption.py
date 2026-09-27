"""The pick's function name without the markers its family's template adds (B8)."""

from ..names.names import Names
from ..names.template_affixes import template_affixes
from .source_name import source_name


def pick_caption(name: str, vocabulary: Names) -> str:
    caption = source_name(name, vocabulary)
    prefixes = (
        template_affixes(vocabulary, "movement_shape")[0],
        vocabulary.display("panels_label") + " - ",
        "Gobo - ",
        vocabulary.display("prism_label") + " - ",
    )
    for prefix in prefixes:
        caption = caption.removeprefix(prefix)
    return caption.removesuffix(template_affixes(vocabulary, "with_pixels")[1])
