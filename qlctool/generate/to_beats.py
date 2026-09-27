"""Switch one function to Beats tempo, writing its step timing in beats."""

from lxml import etree

from ..constants import QLC_NS
from ..xmlutil import find_local, findall_local
from .beat_timing import BeatTiming
from .beat_units import beat_units

TEMPO_BEATS = "Beats"


def to_beats(function: etree._Element, timing: BeatTiming) -> None:
    hold, fade = beat_units(timing.hold), beat_units(timing.fade)

    if find_local(function, "Tempo") is None:
        # First child, where Function::saveXML writes it: after the attributes
        # saveXMLCommon carries and before <Speed>.
        tempo = etree.Element(f"{{{QLC_NS}}}Tempo")
        tempo.text = TEMPO_BEATS
        function.insert(0, tempo)

    speed = find_local(function, "Speed")
    if speed is not None:
        speed.set("FadeIn", str(fade))
        speed.set("FadeOut", str(fade))
        speed.set("Duration", str(fade + hold))

    for step in findall_local(function, "Step"):
        step.set("FadeIn", str(fade))
        step.set("Hold", str(hold))
        step.set("FadeOut", str(fade))
