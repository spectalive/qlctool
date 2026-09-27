"""A figure's reach once QLC+ turns it (`rotateAndScale`, efx.cpp 306-327).

Added 2026-09-27, the night of the en-sala DMX re-audit: the Vibra beam
figures are Width 20 Height 13, and turned they reach further on tilt than
their Height - which is what put Diamante outside the audience window.
"""

import pytest

from qlctool.efx_extent import efx_extent


def test_a_diamond_turned_90_swaps_its_reach():
    (pan_min, pan_max), (tilt_min, tilt_max) = efx_extent("Diamond", 20, 13, 90)
    assert (pan_min, pan_max) == (pytest.approx(-13, abs=0.1), pytest.approx(13, abs=0.1))
    assert (tilt_min, tilt_max) == (pytest.approx(-20, abs=0.1), pytest.approx(20, abs=0.1))


def test_a_leaf_turned_45_reaches_past_its_height():
    (pan_min, pan_max), (tilt_min, tilt_max) = efx_extent("Leaf", 20, 13, 45)
    for value in (pan_max, tilt_max, -pan_min, -tilt_min):
        assert value == pytest.approx(14.7, abs=0.1)


def test_an_unturned_figure_reaches_its_half_size():
    for algorithm in ("Circle", "Eight", "Line", "Diamond", "Square", "Leaf", "Lissajous"):
        (pan_min, pan_max), (tilt_min, tilt_max) = efx_extent(algorithm, 20, 13, 0)
        assert (pan_min, pan_max) == (pytest.approx(-20), pytest.approx(20)), algorithm
        assert (tilt_min, tilt_max) == (pytest.approx(-13), pytest.approx(13)), algorithm
