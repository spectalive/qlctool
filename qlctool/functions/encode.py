"""Encode a Scene's (offset, value) pairs as QLC+'s flat comma-separated text."""


def encode(pairs: list[tuple[int, int]]) -> str:
    ordered = sorted(pairs, key=lambda pair: pair[0])
    return ",".join(f"{offset},{value}" for offset, value in ordered)
