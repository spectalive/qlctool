"""The pieces of Spanish catalogue values a generator must not spell itself.

A literal is flagged when, stripped of spaces and joining punctuation, it
equals a piece of a Spanish catalogue value whose English value differs: that
piece would stay Spanish in an English show. Words both languages share
("AUTO", "Dimmer Chase") are not flagged - they are the same either way.
"""

import re
from string import Formatter

from literal_strip import LITERAL_STRIP

from qlctool.names.load_catalogue import load_catalogue


def catalogue_chunks() -> frozenset[str]:
    """Every word-bearing piece of every Spanish value that English spells differently."""
    spanish, english = load_catalogue("es"), load_catalogue("en")
    chunks: set[str] = set()
    for section, entries in spanish.items():
        for identifier, text in entries.items():
            if english.get(section, {}).get(identifier) == text:
                continue
            for literal, _, _, _ in Formatter().parse(text):
                piece = literal.strip(LITERAL_STRIP)
                if re.search(r"[^\W\d_]{2,}", piece):
                    chunks.add(piece)
    return frozenset(chunks)
