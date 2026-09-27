"""Whether a shutter value is neither the fixture's open range nor its strobing one."""

from ..definition import Capability


def shutter_closed(value: int | None, opening: Capability, strobing: Capability | None) -> bool:
    if value is None:
        return False
    if opening.minimum <= value <= opening.maximum:
        return False
    return strobing is None or not (strobing.minimum <= value <= strobing.maximum)
