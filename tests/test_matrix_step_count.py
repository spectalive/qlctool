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


def test_sine_wave_sweeps_the_curated_horizontal_orientation():
    """sinewave.js, orientation Horizontal: the sweep is as wide as the grid."""
    assert matrix_step_count("Sine Wave", 8, 2) == 8


def test_fill_unfill_doubles_the_curated_horizontal_span_minus_one():
    """fillunfill.js, orientation Horizontal: (width * 2) - 1."""
    assert matrix_step_count("Fill Unfill", 12, 1) == 23


def test_marquee_is_its_own_default_marquee_count():
    """marquee.js: rgbMapStepCount returns algo.marqueeCount verbatim."""
    assert matrix_step_count("Marquee", 8, 2) == 3


def test_circular_is_fixed_at_one_hundred_on_every_grid():
    """circular.js: fixed so every grid circles at the same speed."""
    assert matrix_step_count("Circular", 15, 1) == 100
    assert matrix_step_count("Circular", 8, 2) == 100


def test_gradient_is_the_curated_rainbow_preset_length():
    """gradient.js: gradientData.length for Rainbow (3 stops) x presetSize 5."""
    assert matrix_step_count("Gradient", 15, 1) == 15


def test_lines_and_starfield_declare_two_regardless_of_grid():
    for algorithm in ("Lines", "3D Starfield"):
        assert matrix_step_count(algorithm, 8, 2) == 2, algorithm


def test_plasma_and_noise_use_a_fixed_duration_policy_not_the_grid():
    """Neither script's own declared count means anything (see docstring)."""
    assert matrix_step_count("Plasma", 8, 2) == 40
    assert matrix_step_count("Plasma", 15, 1) == 40
    assert matrix_step_count("Noise", 12, 1) == 20
    assert matrix_step_count("Noise", 15, 1) == 20
