"""`count` positions evenly across `span`, centred, clear of both ends."""


def spread(count: int, span: float, margin: float) -> list[float]:
    if count <= 0:
        return []
    if count == 1:
        return [span / 2]
    usable = span - 2 * margin
    return [margin + usable * index / (count - 1) for index in range(count)]
