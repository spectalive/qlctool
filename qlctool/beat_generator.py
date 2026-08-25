"""Tell the workspace where its beat comes from.

QLC+ can run a function's speed in beats instead of milliseconds, and the beat
itself has four possible sources - `InputOutputMap::BeatGeneratorType`:
`Disabled`, `Internal` (the MasterTimer's own metronome at a fixed BPM),
`Plugin` (MIDI beat clock) and `Audio`, which derives it from an audio input
device by wiring `AudioCapture::beatDetected` into the beat clock.

`Audio` is the one that matters to a laptop left alone in a venue: the room's
own music becomes the clock, with no operator and no MIDI cable. It needs an
audio input picked in QLC+'s configuration, which lives in the application's
settings and not in the workspace - so a file asking for Audio on a machine with
no input selected has a beat source that never ticks, and anything set to Beats
tempo waits forever. That is the whole risk of this switch, and why the show is
generated in real time by default.

The node is `<BeatGenerator BeatType="..." BPM="n"/>`, the first child of
`<InputOutputMap>`. BPM is what the generator last measured; zero is the right
value to store for a detected source, which fills it in as soon as it hears
something.
"""

from lxml import etree

from .constants import QLC_NS
from .xmlutil import find_local

BEAT_TYPES = ("Disabled", "Internal", "Plugin", "Audio")


def set_beat_generator(
    root: etree._Element, beat_type: str = "Audio", bpm: int = 0
) -> None:
    """Set the workspace's beat source in place. Raises on an unknown type."""
    if beat_type not in BEAT_TYPES:
        raise ValueError(
            f"unknown beat generator {beat_type!r} "
            f"(known: {', '.join(BEAT_TYPES)})"
        )

    io_map = find_local(find_local(root, "Engine"), "InputOutputMap")
    if io_map is None:
        raise ValueError("workspace has no <InputOutputMap>")

    generator = find_local(io_map, "BeatGenerator")
    if generator is None:
        generator = etree.Element(f"{{{QLC_NS}}}BeatGenerator")
        io_map.insert(0, generator)
    generator.set("BeatType", beat_type)
    generator.set("BPM", str(bpm))
