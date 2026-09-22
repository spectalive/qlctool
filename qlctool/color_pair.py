"""Two palette colours that go together, and which of them leads.

`lead` is the colour that should read first - on the moving heads in a
contrast, on the odd fixtures in a split - and `bed` the one under it. The
order is not cosmetic: warm dominates cool and paler dominates more saturated
(HARMAN's colour theory for concert lighting, in
`brain/topics/stage-lighting-design`), so a pair is written the way the eye
will rank it and the generators keep that order.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ColorPair:
    lead: str
    bed: str
