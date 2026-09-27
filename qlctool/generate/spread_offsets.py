"""Phase offsets spreading `count` fixtures evenly around the path."""


def spread_offsets(count: int) -> list[int]:
    if count <= 0:
        return []
    return [round(360 * index / count) % 360 for index in range(count)]
