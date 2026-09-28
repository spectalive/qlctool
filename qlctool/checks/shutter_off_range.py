"""Whether the shutter is somewhere other than its open or strobing range."""

from ..capability import Capability


def shutter_off_range(value: int | None, opening: Capability, strobing: Capability | None) -> bool:
    """Whether the shutter is somewhere other than its open or strobing range.

    An untouched DMX channel is 0, which on one fixture is "no strobe, open"
    and on the next is "closed". A value nobody can predict - an effect driving
    the shutter - is not reported: strobing is what that fixture was asked to
    do. A value inside the *labelled strobing range* is not shut either: a
    strobing shutter emits light, which is the whole reason `Flash 100%`
    drives it there.
    """
    if value is None:
        return False
    if opening.minimum <= value <= opening.maximum:
        return False
    return strobing is None or not (strobing.minimum <= value <= strobing.maximum)
