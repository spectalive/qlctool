"""Every promising caption identifier with its text in every shipped catalogue, as patterns."""

import re
from functools import cache

from ..names.load_catalogue import load_catalogue
from ..names.shipped_languages import shipped_languages
from ..names.template_pattern import template_pattern
from .caption_promises import CAPTION_PROMISES


@cache
def promise_patterns() -> tuple[tuple[str, re.Pattern[str]], ...]:
    """(identifier, pattern) for each identifier that promises something, each language."""
    found: list[tuple[str, re.Pattern[str]]] = []
    for language in shipped_languages():
        entries = {
            identifier: text
            for section in load_catalogue(language).values()
            for identifier, text in section.items()
        }
        found += [
            (identifier, template_pattern(entries[identifier]))
            for identifier, promises in CAPTION_PROMISES.items()
            if promises and identifier in entries
        ]
    return tuple(found)
