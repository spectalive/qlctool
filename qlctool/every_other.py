"""Every other item of a sequence: the heads that run a figure backwards.

A movement EFX gives symmetry by reversing some of its fixtures
(`mirrored_ids`). Reversing one side of the truss makes the pairs open and
close together; reversing alternate heads makes each one oppose its neighbour,
which is the "cada cabeza para un lado" the owner asked for (2026-09-22). Both
are the same mechanism with a different set, so the set is what this names.
"""

from collections.abc import Sequence


def every_other(items: Sequence[int]) -> list[int]:
    """The items at odd positions, in order."""
    return list(items[1::2])
