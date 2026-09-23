"""A 3x3 matrix applied to a vector."""


def apply_rotation(
    m: list[list[float]], v: tuple[float, float, float]
) -> tuple[float, float, float]:
    x, y, z = (sum(m[i][k] * v[k] for k in range(3)) for i in range(3))
    return (x, y, z)
