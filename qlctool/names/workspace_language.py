"""Which shipped language a saved workspace was generated in (ruling B12).

The room-states frame is on every generated console, and its title differs in
every catalogue, so it identifies the language without reading any function
name. A workspace without it (a hand-built one) is read as Spanish, the
language every such workspace in this repository was built in.
"""

from lxml import etree

from ..desk_widgets import FRAME_TAGS, desk_widgets
from .load_catalogue import load_catalogue
from .shipped_languages import shipped_languages


def workspace_language(root: etree._Element) -> str:
    """The first shipped language whose room-states title is a frame caption here."""
    # The desk reads frames and solo frames alike; the room states are a solo frame.
    captions = {widget.caption for widget in desk_widgets(root) if widget.kind in FRAME_TAGS}
    for language in shipped_languages():
        if load_catalogue(language)["frames"]["room_states"] in captions:
            return language
    return "es"
