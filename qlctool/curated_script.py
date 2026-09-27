"""One hand-tuned RGB script recipe for one fixture group's own grid."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CuratedScript:
    """One hand-tuned RGB script recipe for one fixture group's own grid.

    Fill/Even-Odd/Waves/Strobe are generic - the same four names cross every
    group and every colour. These are the opposite: each is a specific script
    property values had to be chosen for by hand, verified against the script's
    own `.js` in `~/p/qlcplus/resources/rgbscripts/` so a chosen property name
    matches what the script declares and a chosen colour count matches what it
    actually reads (`acceptColors`). `properties` values are written into
    `<Property Value="...">` verbatim, so they use the script's own vocabulary
    (e.g. "Horizontal", not a translation of it). `colors` names 1 or 2 entries
    from `palette.PALETTE`; a second name is only ever given to a script that
    reads a second colour - see the per-entry comments below.
    """

    group_name: str
    algorithm: str
    properties: dict[str, str]
    colors: tuple[str, ...]
