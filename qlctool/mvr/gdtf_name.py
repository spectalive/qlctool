"""A name the GDTF schema accepts.

Every `Name` in a GDTF file - a channel set, a wheel slot, a function - is
held to one character class: letters, digits, space and a short list of
punctuation. QLC+ definitions are written for people and say things like
`Strobe (slow → fast)`; the arrow is what fails the whole file. Anything
outside the class becomes a space, and runs of spaces collapse, so the label
still reads.
"""

import re

_DISALLOWED = re.compile(r"""[^a-zA-Z0-9#%()*+,\-./:;<=>@_` "']+""")


def gdtf_name(text: str) -> str:
    return re.sub(r" {2,}", " ", _DISALLOWED.sub(" ", text)).strip() or "Unnamed"
