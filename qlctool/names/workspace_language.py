"""Which shipped language a saved workspace was generated in (ruling B12).

The room-states frame is on every generated console, and its title differs in
every catalogue, so it identifies the language without reading any function
name. A workspace without it (a hand-built one) is read as Spanish, the
language every such workspace in this repository was built in.
"""

from lxml import etree

from ..desk_widgets import FRAME_TAGS, desk_widgets
from .frame_caption_head import frame_caption_head
from .load_catalogue import load_catalogue
from .shipped_languages import shipped_languages


def workspace_language(root: etree._Element) -> str:
    """The first shipped language whose room-states title heads a frame caption here.

    Only the head before " — " is compared, ignoring case, as the desk does
    (`desk_frame_identifier`): a reworded explanation keeps the language.
    """
    # The desk reads frames and solo frames alike; the room states are a solo frame.
    heads = {
        frame_caption_head(widget.caption)
        for widget in desk_widgets(root)
        if widget.kind in FRAME_TAGS
    }
    for language in shipped_languages():
        title = load_catalogue(language)["frames"]["room_states"]
        if frame_caption_head(title) in heads:
            return language
    return "es"
