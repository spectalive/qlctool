"""The RGB script algorithms this show actually uses.

QLC+ resolves an `<Algorithm Type="Script">` by name against the RGB scripts
installed with the application, so these strings must match QLC+ exactly. This
list is every script name found in the production DeluxeEventos workspaces, so
each one is known to load on the show Mac.
"""

from .curated_script import CuratedScript

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


# Read against `~/p/qlcplus/resources/rgbscripts/*.js` (QLC+ 5.2.2 line), one
# script per file, `algo.name` for the exact `<Algorithm>` text and
# `algo.acceptColors` for how many colours it actually reads. Grid shapes are
# `BarrasLed` 8x2, `PAR` 15x1 (`fixture_group.py`).
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
    # is a required build_rgbmatrix argument the script never reads - and not
    # white, because the checker reads the file, not the script, and a white
    # matrix on a rotation is what `rule_wheel_white` exists to catch.
    CuratedScript("BarrasLed", "Plasma", {"presetIndex": "Rainbow"}, ("Cyan",)),
    # `Cabezas` carried six scripts here until ruling D6 (2026-09-26): its
    # rigged cells are 7R beams on a colour wheel and every red-green-blue
    # cell is a spare in a flight case, so nobody saw any of them
    # (`rule_invisible_matrix`).
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
    # instead of two. No property here changes that. Cool stars, not white
    # ones: the cycle rotates by itself and white is `Blanco Total`'s alone
    # (owner, 2026-09-22; `rule_wheel_white`).
    CuratedScript("PAR", "3D Starfield", {}, ("Celeste",)),
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
    # fillunfill.js: Vertical would read `height`, so on a one-row sweep it is
    # a one-frame flash; Horizontal is the sweep. onebyone.js declares no
    # acceptColors - QLC+ defaults it to 2 (rgbscript.cpp) - and only reads
    # rgb[0]. Both in colours the bars' base set lacks.
    CuratedScript(
        "BarrasLed",
        "Fill Unfill",
        {"orientation": "Horizontal"},
        ("Rosa",),
    ),
    CuratedScript("BarrasLed", "One By One", {}, ("Cyan",)),
    # The PARs carry the rest of the missing palette.
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
