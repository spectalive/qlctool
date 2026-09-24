"""The fixed text around a template's fields: what the console strips when it parses a name.

"Ciclo Matrices BarrasLed" is shown as "Matrices BarrasLed" on a button: the
console removes the cycle template's prefix. Reading the prefix from the
catalogue is what lets the English show strip "Cycle " instead (ruling B8).
"""

from string import Formatter

from .names import Names
from .template_fields import template_fields


def template_affixes(names: Names, identifier: str) -> tuple[str, str]:
    """(text before the first field, text after the last) in the show's language.

    The affixes are unescaped ("{{" reads "{"), as in a rendered name; only
    `render` unescapes braces, `display` returns the value as written.
    """
    text = names.display(identifier)
    if not template_fields(text):
        raise ValueError(f"{identifier} is not a template: {text!r}")
    parts = list(Formatter().parse(text))
    fields = [index for index, part in enumerate(parts) if part[1] is not None]
    head = "".join(literal for literal, _, _, _ in parts[: fields[0] + 1])
    tail = "".join(literal for literal, _, _, _ in parts[fields[-1] + 1 :])
    return head, tail
