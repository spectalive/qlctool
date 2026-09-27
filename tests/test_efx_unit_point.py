"""QLC+'s unit shapes, ported from `EFX::calculatePoint` (efx.cpp 378-490).

Added 2026-09-27 with the rotated-figure fix of `movement_window`: the reach of
a turned figure is read off these points, so they have to be QLC+'s.
"""

import math

import pytest

from qlctool.efx_unit_point import efx_unit_point


def test_a_diamond_starts_at_its_top():
    x, y = efx_unit_point("Diamond", 0.0)
    assert x == pytest.approx(0.0, abs=1e-12)
    assert y == pytest.approx(1.0)


def test_a_leaf_a_quarter_turn_in_is_at_its_left_tip():
    # cos(pi/2 + pi/2) ** 5 = cos(pi) ** 5 = -1
    x, y = efx_unit_point("Leaf", math.pi / 2)
    assert x == pytest.approx(-1.0)
    assert y == pytest.approx(0.0, abs=1e-12)


def test_a_lissajous_with_zero_phase_is_its_two_cosines():
    for step in range(16):
        iterator = math.pi * 2 * step / 16
        x, y = efx_unit_point("Lissajous", iterator, 2, 3, 0.0, 0.0)
        assert x == pytest.approx(math.cos(2 * iterator))
        assert y == pytest.approx(math.cos(3 * iterator))


def test_an_unknown_algorithm_draws_a_circle_like_qlcplus():
    for step in range(8):
        iterator = math.pi * 2 * step / 8
        assert efx_unit_point("Spiral", iterator) == efx_unit_point("Circle", iterator)
