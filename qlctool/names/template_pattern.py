"""A catalogue value as a pattern that matches every text `render` can make of it."""

import re
from string import Formatter


def template_pattern(text: str) -> re.Pattern[str]:
    """ "the panels' {count} effects" matches "the panels' 42 effects"; a plain name, itself.

    The literals are unescaped as `render` unescapes them ("{{" reads "{"), and
    each field matches any non-empty text.
    """
    parts = [
        re.escape(literal) + ("" if field is None else "(.+?)")
        for literal, field, _, _ in Formatter().parse(text)
    ]
    return re.compile("".join(parts))
