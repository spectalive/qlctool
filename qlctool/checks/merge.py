"""Two functions running at once, mixed the way the room mixes them."""

from .driven_channels import Driven
from .higher import higher


def merge(first: Driven, second: Driven) -> Driven:
    merged: Driven = {fixture: dict(pairs) for fixture, pairs in first.items()}
    for fixture_id, pairs in second.items():
        target = merged.setdefault(fixture_id, {})
        for offset, value in pairs.items():
            target[offset] = higher(target.get(offset, 0), value)
    return merged
