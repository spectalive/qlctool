"""The haze timer, the vertical smoke burst, the dimmer chases and the strobes.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .dimmer_chases import generate_dimmer_chases
from .haze_machines import haze_machines
from .show_build import ShowBuild
from .smoke_auto import generate_smoke_auto
from .strobe_effects import generate_strobe_effects
from .vertical_smoke_burst import generate_vertical_smoke_burst


def add_haze_dimmers_strobes(build: ShowBuild) -> None:
    """Haze, the vertical smoke burst, the dimmer chases and the console strobes."""
    workspace = build.workspace
    library = build.library
    caps = build.caps
    vocabulary = build.vocabulary
    master = build.master
    builtins = build.builtins
    matrix_lit_ids = build.matrix_lit_ids
    smoke = (
        generate_smoke_auto(workspace, library, names=vocabulary) if haze_machines(caps) else None
    )
    if smoke is not None:
        # The haze timer, one function per rhythm. AUTO starts the default and
        # the console puts all four in a solo frame, so the operator can change
        # how often the room hazes without leaving the show page.
        master.update(smoke.interval_ids)
        # The burst on its own, for the console: a held button, never a
        # latched one.
        master[vocabulary.display("smoke_on")] = smoke.on_id
    # The vertical machines' column, fog and its own LED in one held scene -
    # with DMX plugged in their internal light program is dead, so if this
    # scene does not light them, nothing does (`rule_smoke_light`).
    burst_id = generate_vertical_smoke_burst(workspace, library, names=vocabulary)
    if burst_id is not None:
        master[vocabulary.display("vertical_smoke_now")] = burst_id

    # The panels and the matrix-lit groups keep their own intensity owners
    # (`Ciclo Paneles Mixto`, `Pixeles ON`), and those hold 255: a chase under
    # a steady 255 can dip nothing - HTP - so they leave the chase entirely.
    dimmers = generate_dimmer_chases(
        workspace,
        library,
        exclude_fixture_ids=sorted(matrix_lit_ids | set(builtins.fixture_ids)),
        names=vocabulary,
    )
    if dimmers is not None:
        master[vocabulary.display("dimmer_chase")] = dimmers.chase_id
        master[vocabulary.display("dimmer_chase_2")] = dimmers.chase2_id
        master[vocabulary.display("dimmer_pingpong")] = dimmers.pingpong_id

    # The console strobes are held scenes on the shutters, not chasers: a
    # chaser's black step is all Intensity channels, and Intensity is HTP, so
    # under any lit state the zeros lost and the "strobe" was white over the
    # room's colour with never a black between (cross-audit, 2026-09-02). The
    # chaser twins of `Blanco Total`/`Todo Negro` that used to be here also
    # pressed the state buttons by proxy (2026-08-29) before they got twins.
    strobes = generate_strobe_effects(workspace, library, names=vocabulary)
    master[vocabulary.display("strobe_fast")] = strobes.fast_id
    master[vocabulary.display("strobe_medium")] = strobes.medium_id
    if strobes.on_id is not None and strobes.off_id is not None:
        master[vocabulary.display("strobe_on")] = strobes.on_id
        master[vocabulary.display("strobe_off")] = strobes.off_id
    build.dimmers = dimmers
