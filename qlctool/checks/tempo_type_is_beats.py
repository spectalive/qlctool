"""Whether a function's Tempo Type attribute names the Beats build."""

from lxml import etree

from ..xmlutil import find_local

BEATS = "Beats"  # Function::TempoType


def tempo_type_is_beats(function: etree._Element) -> bool:
    """Whether this function already counts in beats of the show's own BPM."""
    tempo = find_local(function, "Tempo")
    return tempo is not None and tempo.attrib.get("Type") == BEATS
