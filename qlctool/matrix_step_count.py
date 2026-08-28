"""How many frames one pass of an RGB script takes, so a chaser can wait for it.

An RGBMatrix does not "play for a while": it walks a fixed number of frames and
starts again, and the number depends on the script *and on the grid*. Fill on an
eight-wide bar is eight frames; Waves on the same bar is twelve. A chaser that
holds such a matrix for less than that cuts the animation off wherever it had
got to - which on Fill means the bar lights half way, jumps to another colour,
and lights half way again, forever. The owner's words: "empezamos una animacion
pero nunca la terminamos".

The counts are QLC+'s own, read out of the `rgbMapStepCount` of each script in
`RGBScripts/` (QLC+ 5.2.2), for the script's default properties - which is how
the generator writes them for the four workhorse scripts below, since it sets
no properties on those. `matrix_algorithms.CURATED_MATRICES` sets properties
deliberately on the rest, so their counts assume *that* recipe, not the
script's shipped default - each branch says which. A script not listed here
falls back to the longest a sweep could sensibly take, so an unknown effect is
given too much time rather than too little.

Two scripts get a count QLC+ never claimed at all. plasma.js says outright
"This make no difference to the script" and returns 2 regardless of any
property - it is continuous Perlin noise with no loop point to count. noise.js
returns width * height, but its `rgbMap` redraws every pixel from
`Math.random()` every frame without ever looking at the `step` QLC+ passes it,
so that count is not a pass either, just a coincidence of grid size. Both get
an explicit fixed duration instead: a viewing window we chose, not a
measurement of anything the script does.
"""

PLAIN_STEPS = 1
# waves.js: taillength 50 %, direction Right, orientation Horizontal.
WAVES_TAIL = 0.5

# marquee.js: algo.marqueeCount, left at its own default of 3 in the curated
# recipe - rgbMapStepCount returns it verbatim.
MARQUEE_COUNT = 3
# gradient.js: rgbMapStepCount returns util.gradientData.length, which is
# (colours in the preset) * presetSize. The curated recipe fixes Rainbow (3
# stops) and presetSize 5: 3 * 5, not derived from the grid at all.
GRADIENT_RAINBOW_STEPS = 15
# Fixed duration policy (see module docstring): chosen viewing windows for the
# two scripts whose own declared count means nothing.
PLASMA_STEPS = 40
NOISE_STEPS = 20


def matrix_step_count(algorithm: str | None, width: int, height: int) -> int:
    """Frames in one full pass of this algorithm over a width x height grid."""
    if algorithm is None:
        return PLAIN_STEPS  # <Algorithm Type="Plain"/>: one static frame
    if algorithm == "Fill":
        return width  # fill.js, orientation Horizontal
    if algorithm in ("Even/Odd", "Alternate", "Random Column"):
        return 2  # evenodd.js and friends: one frame per half
    if algorithm == "Opposite":
        return width  # opposite.js, orientation Horizontal: two dots cross the row
    if algorithm in ("Fill From Center", "Stripes From Center"):
        return (width + 1) // 2  # *fromcenter.js, Horizontal: centre to both edges
    if algorithm == "Strobe":
        return 2  # strobe.js: the default frequency
    if algorithm == "Waves":
        return _waves(width)
    if algorithm == "One By One":
        return width * height  # onebyone.js visits every cell
    if algorithm == "Sine Wave":
        return width  # sinewave.js, curated recipe: orientation Horizontal
    if algorithm in ("Lines", "3D Starfield"):
        return 2  # lines.js / starfield.js: the script's own declared count
    if algorithm == "Marquee":
        return MARQUEE_COUNT
    if algorithm == "Plasma":
        return PLASMA_STEPS
    if algorithm == "Fill Unfill":
        return width * 2 - 1  # fillunfill.js, curated recipe: Horizontal
    if algorithm == "Noise":
        return NOISE_STEPS
    if algorithm == "Circular":
        return 100  # circular.js: fixed so every grid circles at the same speed
    if algorithm == "Gradient":
        return GRADIENT_RAINBOW_STEPS
    return max(width, height)


def _waves(span: int) -> int:
    """waves.js: the sweep plus its tail, one frame shorter on an odd span."""
    tail = max(1, round(span * WAVES_TAIL))
    return span + tail - (0 if span % 2 == 0 else 1)
