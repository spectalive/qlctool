"""Where a standing fixture's lens ends up pointing: its +Z after the turn."""

from pymvr import Matrix


def beam_direction(matrix: Matrix) -> tuple[float, float, float]:
    x, y, z = (round(v, 6) for v in matrix.matrix[2][:3])
    return (x, y, z)
