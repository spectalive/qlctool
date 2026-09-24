"""The Vibra night's clock: how long each level holds, and the beats its chases count."""

from ..description.show_timing import ShowTiming
from ..generate.beat_tempo import BeatTiming

VIBRA_TIMING = ShowTiming(
    # Where the internal clock starts. 120 is the middle of the room this show
    # plays, and the beat the tap dial's multipliers are figured against.
    bpm=120,
    # How long the night spends at each level, in milliseconds. A wave rather
    # than a ramp: the cycle comes down through the middle level instead of
    # jumping from peak to quiet. Peak is a burst, not a block - two
    # continuous minutes of fast movement and prism stopped reading as a peak
    # at all (Codex review, 2026-08-27: 20-45 s); the wave passes through it
    # twice per cycle anyway.
    ambient_ms=4 * 60 * 1000,
    party_ms=8 * 60 * 1000,
    peak_ms=40 * 1000,
    # The descent from the peak: party pace, but the intensity moves - the
    # running chase, then the odd/even ping-pong - so the room reads "some on,
    # some off" instead of a flat wall of light ("a veces se apagan unos y se
    # encienden otros", owner, 2026-08-28).
    dynamic_ms=4 * 60 * 1000,
    # Inside that level the two dimmer programmes take turns - serialized in
    # one chaser, because two of them at once are not an ownership handover:
    # intensity mixes HTP and the ping-pong's 255 half simply masks the chase.
    dynamic_chase_ms=30 * 1000,
    dynamic_pingpong_ms=8 * 1000,
    # The panels' night, in phases: their own forty-one programmes most of the
    # time, then a stretch in manual listening to the rig wheel's RGB -
    # "estaría bien usar rgb para que vaya con el resto de vez en cuando"
    # (owner, 2026-08-28). The wheel writes their colour on every step all
    # night; this cycle only decides whether they are listening.
    panel_effects_ms=8 * 60 * 1000,
    panel_manual_ms=4 * 60 * 1000,
    prism_step_ms=8000,
    # Beat-locked timings, in beats, for every generated show. Two bars of
    # colour, one bar of matrix, eight bars of one movement shape: the counts
    # a chase is actually written in. On the clock these ratios were fixed
    # milliseconds and the only way to re-time them live was a dial writing
    # raw durations - which is how tapping a 500 ms beat put every wheel on
    # 500 ms flat ("se vuelven todos los programas locos", owner,
    # 2026-08-29). In Beats each layer keeps its own count and one global BPM
    # moves them all together.
    beat_timings={
        "Rueda Colores": BeatTiming(hold=8, fade=1),
        "Movimientos Suaves": BeatTiming(hold=64, fade=10),
        # The 5 s crossfade between movement blocks (old Chaser 23, restored
        # 2026-08-28) is 10 beats at the default 120 BPM.
        "Movimientos Washes": BeatTiming(hold=32, fade=10),
        "Movimientos Beams": BeatTiming(hold=32, fade=10),
        "Rapidos Washes": BeatTiming(hold=16),
        "Rapidos Beams": BeatTiming(hold=16),
        "Gobo Animacion": BeatTiming(hold=16),
        "Prisma Animacion": BeatTiming(hold=32),
        "Dimmer Chase": BeatTiming(hold=4),
        "Dimmer PingPong": BeatTiming(hold=2),
    },
    matrix_beats=BeatTiming(hold=4),
)
