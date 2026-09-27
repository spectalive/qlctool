"""A turned figure drawn at the size whose reach fits its window (2026-09-27).

Diamante, Hoja and Cascada Beams were drawn at the beam window's half-size
(W20 H13) and then turned, which reached past the window on tilt (en-sala DMX
re-audit). The fit is measured with `efx_extent`, so these are its answers.
"""

from qlctool.efx_extent import efx_extent
from qlctool.generate.fit_rotated_figure import fit_rotated_figure


def test_a_diamond_turned_90_swaps_its_axes():
    assert fit_rotated_figure("Diamond", 90, 20, 13) == (13, 20)


def test_a_leaf_turned_45_is_the_largest_that_fits():
    assert fit_rotated_figure("Leaf", 45, 20, 13) == (16, 18)


def test_a_circle_turned_45_is_the_circle_the_tighter_axis_allows():
    assert fit_rotated_figure("Circle", 45, 20, 13) == (13, 13)


def test_every_fit_stays_inside_and_one_count_more_does_not():
    for algorithm, rotation in (("Diamond", 90), ("Leaf", 45), ("Circle", 45)):
        width, height = fit_rotated_figure(algorithm, rotation, 20, 13)
        (pan_min, pan_max), (tilt_min, tilt_max) = efx_extent(algorithm, width, height, rotation)
        assert pan_min >= -20 - 1e-6 and pan_max <= 20 + 1e-6, algorithm
        assert tilt_min >= -13 - 1e-6 and tilt_max <= 13 + 1e-6, algorithm
        for grown in ((width + 1, height), (width, height + 1)):
            (_, pan_reach), (_, tilt_reach) = efx_extent(algorithm, *grown, rotation)
            assert pan_reach > 20 + 1e-6 or tilt_reach > 13 + 1e-6, (algorithm, grown)
