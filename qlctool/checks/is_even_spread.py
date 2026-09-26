"""Whether a set of values is a fan: three or more, evenly spaced.

A generated fan spreads its heads over a span in equal steps, rounded to whole
DMX counts, so two neighbouring gaps may differ by one. A hand-aimed look -
`Escenario`, measured on site with two heads on the same pan - is not a fan,
and its order across the stage is somebody's decision.
"""

from collections.abc import Sequence
from itertools import pairwise


def is_even_spread(values: Sequence[int]) -> bool:
    """True when `values` are three or more distinct numbers in equal steps, give or take one."""
    ordered = sorted(values)
    if len(set(ordered)) != len(ordered) or len(ordered) < 3:
        return False
    gaps = [high - low for low, high in pairwise(ordered)]
    return max(gaps) - min(gaps) <= 1
