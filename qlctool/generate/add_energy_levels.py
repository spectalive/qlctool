"""The four energy levels, their cycle and AUTO, the one thing to press.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .energy_levels import EnergyLevel, generate_energy_levels
from .show_build import ShowBuild
from .show_collection import show_collection


def add_energy_levels(build: ShowBuild) -> None:
    """The energy levels and AUTO."""
    workspace = build.workspace
    vocabulary = build.vocabulary
    described = build.described
    master = build.master
    pixel_layer = build.pixel_layer
    movement = build.movement
    gobo_open_id = build.gobo_open_id
    prism_off_id = build.prism_off_id
    intensity = build.intensity
    peak_static = build.peak_static
    dimmer_programs_id = build.dimmer_programs_id
    energy = generate_energy_levels(
        workspace,
        levels=[
            EnergyLevel(
                vocabulary.display("level_ambient"),
                # Alive from the first second - "el auto es eso, como el modo
                # auto de las cabezas en si" (owner, 2026-08-27). Both families
                # breathe, each through its own slow envelope, and the room
                # sits at the low intensity base. The beams held the static fan
                # here until 2026-08-29, when the owner watched AUTO and
                # reported them not moving: four minutes of a needle nailed to
                # one spot is the level's whole hold. The gobo wheel is parked
                # open: the quiet level is where the pattern comes *out*, and a
                # wheel nothing drives keeps what it was left on.
                [
                    fid
                    for fid in (
                        movement.slow_id,
                        gobo_open_id,
                        prism_off_id,
                        intensity.ambient_id,
                    )
                    if fid is not None
                ],
                described.timing.ambient_ms,
            ),
            EnergyLevel(
                vocabulary.display("level_party"),
                # The prism runs here too since 2026-08-30. It used to be
                # held back for the 40-second peak, which meant the room saw
                # it for forty seconds out of every twenty-four minutes:
                # "le faltaba usar mas los gobos los prismas etc" (owner).
                # The dance takes it in and out on its own, so a level that
                # runs it is not a level stuck inside a kaleidoscope.
                [
                    fid
                    for fid in (
                        movement.cabezas_id,
                        master.get(vocabulary.display("gobo_animation")),
                        master.get(vocabulary.display("prism_animation"), prism_off_id),
                        intensity.full_id,
                    )
                    if fid is not None
                ],
                described.timing.party_ms,
            ),
            EnergyLevel(
                vocabulary.display("level_peak"),
                [
                    fid
                    for fid in (
                        movement.rapidos_id,
                        master.get(vocabulary.display("gobo_animation")),
                        master.get(vocabulary.display("prism_animation")),
                        master.get(vocabulary.display("dimmer_chase")),
                        peak_static,
                    )
                    if fid is not None
                ],
                described.timing.peak_ms,
            ),
            # The way down from the peak: party movement, but the dimmers
            # belong to the serialized programmes - lights taking turns
            # instead of a flat wall.
            EnergyLevel(
                vocabulary.display("level_dynamic"),
                [
                    fid
                    for fid in (
                        movement.cabezas_id,
                        master.get(vocabulary.display("gobo_animation")),
                        master.get(vocabulary.display("prism_animation"), prism_off_id),
                        dimmer_programs_id,
                        peak_static,
                    )
                    if fid is not None
                ],
                described.timing.dynamic_ms,
            ),
        ],
        order=tuple(
            vocabulary.display(identifier)
            for identifier in ("level_ambient", "level_party", "level_peak", "level_dynamic")
        ),
        names=vocabulary,
    )
    master.update(energy.level_ids)
    if energy.cycle_id is not None:
        master[vocabulary.display("energy_cycle")] = energy.cycle_id

    # The one thing to press: the colour bed, the pixels, the haze and the
    # energy cycle. Not the beams' colour wheel: it started after the colour
    # wheel and so won the beams' one colour channel, which is what kept them
    # off whatever the rest of the rig was doing. The rig-wide scenes set that
    # wheel themselves now, and the beams' own wheel walk is gone with its
    # button (2026-09-22).
    auto_members = [
        f
        for f in (
            master.get(vocabulary.display("colour_wheel")),
            master.get(vocabulary.display("smoke_auto")),
        )
        if f is not None
    ] + [*pixel_layer]
    if vocabulary.display("energy_cycle") in master:
        auto_members.append(master[vocabulary.display("energy_cycle")])
    else:
        auto_members += [
            f
            for f in (
                master.get(vocabulary.display("head_movements")),
                master.get(vocabulary.display("gobo_animation")),
            )
            if f is not None
        ]
    master[vocabulary.display("auto")] = show_collection(
        workspace, vocabulary.display("auto"), auto_members
    )
