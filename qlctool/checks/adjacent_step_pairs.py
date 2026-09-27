"""The (lit, dark) step index pairs that can be adjacent in time."""


def adjacent_step_pairs(count: int, run_order: str) -> list[tuple[int, int]]:
    if run_order == "Random":
        # Any step can follow any other.
        return [(a, b) for a in range(count) for b in range(count) if a != b]
    last = count if run_order == "Loop" else count - 1
    pairs = []
    for index in range(last):
        follower = (index + 1) % count
        pairs.append((index, follower))
        pairs.append((follower, index))
    return pairs
