"""The work light, the blackout, the flashes and the hits: the lowest function ids.

Moved verbatim out of `build_canonical_show` (2026-09-26, round G); the
functions are created in the order they always were.
"""

from .blackout_scene import blackout_scene
from .color_flashes import generate_color_flashes
from .flash_color import generate_flash_color
from .flat_scene import flat_scene
from .show_build import ShowBuild


def add_base_looks(build: ShowBuild) -> None:
    """Base looks first, so they are the lowest function IDs and read first."""
    workspace = build.workspace
    caps = build.caps
    vocabulary = build.vocabulary
    described = build.described
    master = build.master
    colours = build.described.colours
    # Base looks first, so they are the lowest function IDs and read first.
    # One white, not three. "Luces ON", "Todo Blanco" and "Flash 100%" were all
    # full white on the same fixtures, which is why nobody could say what the
    # difference was: there was none. What is left is a latched work light and a
    # held hit, and the names say which is which.
    # `wheel_color` is what lights the beams: they have no RGB, so a colour
    # scene alone skipped them entirely and "everything white" left the four
    # 7R dark - not dimmed, never written to.
    master[vocabulary.display("full_white")] = flat_scene(
        workspace,
        caps,
        vocabulary.display("full_white"),
        (255, 255, 255),
        names=vocabulary,
        wheel_color=vocabulary.display("white"),
    )
    master[vocabulary.display("all_black")] = blackout_scene(
        workspace, caps, vocabulary.display("all_black")
    )
    # The flashes are the work light *strobing*: full white plus every shutter
    # driven, fast on Space and at half speed on `-` - which is what "50%"
    # meant on the hand-built console, not half the brightness.
    master[vocabulary.display("flash_full")] = flat_scene(
        workspace,
        caps,
        vocabulary.display("flash_full"),
        (255, 255, 255),
        names=vocabulary,
        wheel_color=vocabulary.display("white"),
        strobe=described.tuning.strobe_fast,
    )
    master[vocabulary.display("flash_half")] = flat_scene(
        workspace,
        caps,
        vocabulary.display("flash_half"),
        (255, 255, 255),
        names=vocabulary,
        wheel_color=vocabulary.display("white"),
        strobe=described.tuning.strobe_slow,
    )
    # And the third flash the old console had on `.`: the strobe over whatever
    # colour is already running - dimmer and shutter only, RGB untouched.
    master[vocabulary.display("flash_colour")] = generate_flash_color(
        workspace, caps, fraction=described.tuning.strobe_fast, names=vocabulary
    )
    color_flashes = generate_color_flashes(
        workspace,
        caps,
        {name: colours.palette[name] for name in colours.primary},
        described.tuning.strobe_fast,
        names=vocabulary,
    )
    master.update(
        {
            vocabulary.render("colour_hit", colour=name): function_id
            for name, function_id in color_flashes.ids.items()
        }
    )
    # The bass bar's hit. It was `Flash 100%` - but that scene now strobes,
    # and a strobe fired by whatever the PA does is a strobe nobody chose. So
    # the bass keeps its own plain white: same look, shutters open, no strobe.
    master[vocabulary.display("bass_hit")] = flat_scene(
        workspace,
        caps,
        vocabulary.display("bass_hit"),
        (255, 255, 255),
        names=vocabulary,
        wheel_color=vocabulary.display("white"),
    )
    build.colour_flash_ids = color_flashes.ids
