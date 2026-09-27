"""Whether another state can leave this channel at a value that is not 0."""

from .driven_channels import Driven


def left_showing(reaches: dict[int, Driven], state_id: int, fixture_id: int, offset: int) -> bool:
    for other_id, other in reaches.items():
        if other_id == state_id:
            continue
        value = other.get(fixture_id, {}).get(offset)
        if value is None and offset in other.get(fixture_id, {}):
            return True
        if value:
            return True
    return False
