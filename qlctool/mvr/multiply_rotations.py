"""The product of two 3x3 matrices, `a` applied after `b`."""


def multiply_rotations(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
