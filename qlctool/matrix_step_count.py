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
the generator writes them, since it sets no properties. A script not listed here
falls back to the longest a sweep could sensibly take, so an unknown effect is
given too much time rather than too little.
"""

PLAIN_STEPS = 1
# waves.js: taillength 50 %, direction Right, orientation Horizontal.
WAVES_TAIL = 0.5


def matrix_step_count(algorithm: str | None, width: int, height: int) -> int:
    """Frames in one full pass of this algorithm over a width x height grid."""
    if algorithm is None:
        return PLAIN_STEPS  # <Algorithm Type="Plain"/>: one static frame
    if algorithm == "Fill":
        return width  # fill.js, orientation Horizontal
    if algorithm in ("Even/Odd", "Alternate", "Opposite"):
        return 2  # evenodd.js and friends: one frame per half
    if algorithm == "Strobe":
        return 2  # strobe.js: the default frequency
    if algorithm == "Waves":
        return _waves(width)
    if algorithm == "One By One":
        return width * height  # onebyone.js visits every cell
    return max(width, height)


def _waves(span: int) -> int:
    """waves.js: the sweep plus its tail, one frame shorter on an odd span."""
    tail = max(1, round(span * WAVES_TAIL))
    return span + tail - (0 if span % 2 == 0 else 1)
