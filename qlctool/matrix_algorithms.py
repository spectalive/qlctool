"""The RGB script algorithms this show actually uses.

QLC+ resolves an `<Algorithm Type="Script">` by name against the RGB scripts
installed with the application, so these strings must match QLC+ exactly. This
list is every script name found in the production DeluxeEventos workspaces, so
each one is known to load on the show Mac.
"""

from dataclasses import dataclass

SCRIPT_ALGORITHMS: tuple[str, ...] = (
    "Alternate",
    "Even/Odd",
    "Fill",
    "Fill From Center",
    "Fill Unfill",
    "Gradient",
    "One By One",
    "Opposite",
    "Random Column",
    "Stripes From Center",
    "Strobe",
    "Waves",
)


@dataclass(frozen=True)
class CuratedScript:
    """One hand-tuned RGB script recipe for one fixture group's own grid.

    Fill/Even-Odd/Waves/Strobe are generic - the same four names cross every
    group and every colour. These are the opposite: each is a specific script
    property values had to be chosen for by hand, verified against the script's
    own `.js` in `~/p/qlcplus/resources/rgbscripts/` so a chosen property name
    matches what the script declares and a chosen colour count matches what it
    actually reads (`acceptColors`). `properties` values are written into
    `<Property Value="...">` verbatim, so they use the script's own vocabulary
    (e.g. "Horizontal", not a translation of it). `colors` names 1 or 2 entries
    from `palette.PALETTE`; a second name is only ever given to a script that
    reads a second colour - see the per-entry comments below.
    """

    group_name: str
    algorithm: str
    properties: dict[str, str]
    colors: tuple[str, ...]


# Read against `~/p/qlcplus/resources/rgbscripts/*.js` (QLC+ 5.2.2 line), one
# script per file, `algo.name` for the exact `<Algorithm>` text and
# `algo.acceptColors` for how many colours it actually reads. Grid shapes are
# `BarrasLed` 8x2, `Cabezas` 12x1, `PAR` 15x1 (`fixture_group.py`).
CURATED_MATRICES: tuple[CuratedScript, ...] = (
    # sinewave.js: apiVersion 2, acceptColors 2 - one colour fades into the
    # other across the sweep. Orientation is load-bearing for the step count
    # (matrix_step_count.py assumes Horizontal), not just a look.
    CuratedScript(
        "BarrasLed",
        "Sine Wave",
        {"orientation": "Horizontal"},
        ("Rojo", "Azul"),
    ),
    # lines.js: apiVersion 2. rgbMapStepCount always returns 2 regardless of
    # any property - its own animation runs off internal state the QLC+ "step"
    # argument never reaches, so the count is a formality, not a measurement.
    # acceptColors 2, but the two colours only ever blend across that
    # meaningless 2-frame pass, so one colour is what actually reads.
    CuratedScript("BarrasLed", "Lines", {"linesType": "Horizontal"}, ("Verde",)),
    # marquee.js: apiVersion 3, acceptColors 2, both colours live at once -
    # colorArray[0] is the fixed edge glow, [1] is the crawling dot - unlike
    # the apiVersion-2 scripts above. "marquee" defaults to None (static); set
    # to Forward so the dot actually moves. marqueeCount (default 3, left as
    # is) is what rgbMapStepCount returns - written explicitly since the step
    # count table depends on it.
    CuratedScript(
        "BarrasLed",
        "Marquee",
        {"marquee": "Forward", "marqueeCount": "3"},
        ("Amarillo", "Azul"),
    ),
    # plasma.js: apiVersion 3. Its own setPreset("Rainbow") sets
    # acceptColors to 0 - the preset supplies its own spectrum and a chosen
    # colour would be silently ignored, which is exactly why "Rainbow" is the
    # preset picked here (brief: "plasma (Rainbow preset)"). The colour below
    # is a required build_rgbmatrix argument the script never reads.
    CuratedScript("BarrasLed", "Plasma", {"presetIndex": "Rainbow"}, ("Blanco",)),
    # onebyone.js: declares no properties and no acceptColors at all - QLC+
    # defaults an undeclared acceptColors to 2 (rgbscript.cpp), but the script
    # only ever reads rgb[0], so one colour is what the light shows.
    CuratedScript("Cabezas", "One By One", {}, ("Cyan",)),
    # fillunfill.js: Vertical would read `height`, and Cabezas is 12x1 - a
    # vertical fill on a one-row grid is a one-frame flash, not a sweep.
    # Horizontal is not a preference here, it is the only orientation this
    # grid can show at all.
    CuratedScript("Cabezas", "Fill Unfill", {"orientation": "Horizontal"}, ("Naranja",)),
    # noise.js: acceptColors 1, explicit - the script clamps random noise to
    # one chosen colour's own channels. "High" (its default) redraws every
    # pixel every frame; "Medium" backs that off so twelve moving heads read
    # as a flicker, not a strobe.
    CuratedScript("Cabezas", "Noise", {"noisePercentage": "Medium"}, ("Rosa",)),
    # circular.js: acceptColors 1. Radar is both the brief's pick and the
    # script's own default (circularMode 0). Traced against the algorithm
    # (util.blindoutRadius = min(width, height) / 2 = 0.5 on a 15x1 row): the
    # centre pixel blanks out, but every other pixel's blindout factor
    # saturates past 1 and stops mattering - the endfade/sidefade sweep still
    # plays across the full 15-wide row. It does not collapse to a dot.
    CuratedScript("PAR", "Circular", {"circularMode": "Radar"}, ("Rojo",)),
    # starfield.js: acceptColors 1. On a 15x1 row halfHeight rounds to 0, so a
    # star only draws when its projected y lands on that single row - the
    # simulation is still real, it just reads as stars in one dimension
    # instead of two. No property here changes that.
    CuratedScript("PAR", "3D Starfield", {}, ("Blanco",)),
    # gradient.js: acceptColors 0 - it paints from its own preset palette and
    # never reads a chosen colour at all (unlike the brief's example, which
    # named gradient among the two-colour scripts; verifying the script says
    # otherwise). presetIndex and presetSize are both load-bearing for the
    # step count (rgbMapStepCount returns gradientData.length = colours in the
    # preset times presetSize - Rainbow has 3 stops, so 3 x 5 = 15), which is
    # why both are written even though 5 is already the script's default.
    CuratedScript(
        "PAR",
        "Gradient",
        {"presetIndex": "Rainbow", "presetSize": "5", "orientation": "Horizontal"},
        ("Ambar",),
    ),
    # --- Recovered from the hand-built show (old-vs-new audit, 2026-08-28).
    # DeluxeEventos2's bar cycle ran Alternate, Opposite, Fill From Center,
    # Fill Unfill, One By One, Random Column and Stripes From Center, plus
    # two-colour looks - all of which the generated show had dropped. The old
    # matrices' own MonoColors were sloppy (several "Rosa"/"Cyan" ones were
    # literally blue), so the vocabulary comes back with palette colours, and
    # the seven palette colours nothing generated was emitting ride in here.
    #
    # alternate.js: acceptColors 2, both colours drawn at once (even pixels /
    # odd pixels), step count 2 - the honest script for the old "X / Y" bar
    # duals. orientation is explicit because the step-count table assumes it.
    CuratedScript(
        "BarrasLed",
        "Alternate",
        {"orientation": "Horizontal"},
        ("Azul", "Rojo"),
    ),
    CuratedScript(
        "BarrasLed",
        "Alternate",
        {"orientation": "Horizontal"},
        ("Cyan", "Rosa"),
    ),
    CuratedScript(
        "BarrasLed",
        "Alternate",
        {"orientation": "Horizontal"},
        ("Verde", "Amarillo"),
    ),
    # opposite.js: two dots crossing the row, step count = width (Horizontal).
    CuratedScript("BarrasLed", "Opposite", {"orientation": "Horizontal"}, ("Verde",)),
    # fillfromcenter.js / stripesfromcenter.js: centre outwards, (width+1)/2
    # steps on Horizontal - Vertical on an 8x2 bar is a two-frame blink.
    CuratedScript(
        "BarrasLed",
        "Fill From Center",
        {"orientation": "Horizontal"},
        ("Naranja",),
    ),
    CuratedScript(
        "BarrasLed",
        "Stripes From Center",
        {"orientation": "Horizontal"},
        ("Morado",),
    ),
    # randomcolumn.js: declares nothing, step count 2, reads rgb[0] only.
    CuratedScript("BarrasLed", "Random Column", {}, ("Amarillo",)),
    # fillunfill.js and onebyone.js: same recipes the Cabezas entries above
    # use, on the bars' own grid, in colours the bars' base set lacks.
    CuratedScript(
        "BarrasLed",
        "Fill Unfill",
        {"orientation": "Horizontal"},
        ("Rosa",),
    ),
    CuratedScript("BarrasLed", "One By One", {}, ("Cyan",)),
    # The heads and the PARs carry the rest of the missing palette.
    CuratedScript(
        "Cabezas",
        "Alternate",
        {"orientation": "Horizontal"},
        ("Verde Menta", "Azul Profundo"),
    ),
    CuratedScript("Cabezas", "Opposite", {"orientation": "Horizontal"}, ("Celeste",)),
    CuratedScript("Cabezas", "Random Column", {}, ("Fucsia",)),
    CuratedScript(
        "PAR",
        "Fill From Center",
        {"orientation": "Horizontal"},
        ("Rojo Fuego",),
    ),
    CuratedScript(
        "PAR",
        "Stripes From Center",
        {"orientation": "Horizontal"},
        ("Azul Cielo",),
    ),
    CuratedScript(
        "PAR",
        "Alternate",
        {"orientation": "Horizontal"},
        ("Rosa", "Cyan"),
    ),
)
