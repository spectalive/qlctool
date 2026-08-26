"""One pass of an RGB script, in frames - QLC+'s own numbers, not a guess.

A chaser can only wait for an animation if it knows how long the animation is,
and that is a property of the script *and* the grid. These are read out of
`rgbMapStepCount` in QLC+ 5.2.2's own RGBScripts, for the default properties
the generator writes.
"""

from qlctool.matrix_step_count import matrix_step_count


def test_fill_is_one_frame_per_column():
    """fill.js, orientation Horizontal: the sweep is as wide as the grid."""
    assert matrix_step_count("Fill", 8, 3) == 8
    assert matrix_step_count("Fill", 7, 3) == 7


def test_waves_carries_a_tail_past_the_end_of_the_grid():
    """waves.js: span + tail, one frame shorter on an odd span."""
    assert matrix_step_count("Waves", 8, 3) == 12
    assert matrix_step_count("Waves", 7, 3) == 10


def test_the_two_frame_scripts():
    for algorithm in ("Even/Odd", "Alternate", "Opposite", "Strobe"):
        assert matrix_step_count(algorithm, 8, 3) == 2, algorithm


def test_a_solid_matrix_is_one_frame():
    """<Algorithm Type="Plain"/> does not animate at all."""
    assert matrix_step_count(None, 8, 3) == 1


def test_an_unknown_script_is_given_too_much_time_rather_than_too_little():
    """A sweep nobody has measured still has to be allowed to finish."""
    assert matrix_step_count("Fireworks", 8, 3) == 8
    assert matrix_step_count("Fireworks", 3, 9) == 9
