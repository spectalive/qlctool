"""The fixed text around a template's fields: what the console strips when it parses a name.

"Ciclo Matrices BarrasLed" is shown as "Matrices BarrasLed" on a button: the
console removes the cycle template's prefix. Reading the prefix from the
catalogue is what lets the English show strip "Cycle " instead (ruling B8).
"""

from .names import Names


def template_affixes(names: Names, identifier: str) -> tuple[str, str]:
    """(text before the first field, text after the last) in the show's language."""
    text = names.display(identifier)
    head, brace, rest = text.partition("{")
    _, close, tail = rest.rpartition("}")
    if not brace or not close:
        raise ValueError(f"{identifier} is not a template: {text!r}")
    return head, tail
