"""Whether a function's own Tempo element text names the Beats build."""

from lxml import etree

from ..find_local import find_local

BEATS = "Beats"


def tempo_element_is_beats(function: etree._Element) -> bool:
    tempo = find_local(function, "Tempo")
    return tempo is not None and (tempo.text or "").strip() == BEATS
