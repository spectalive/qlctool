"""Refuse an override that drops or invents a template's fields."""

from collections.abc import Mapping

from .load_catalogue import load_catalogue
from .template_fields import template_fields


def check_override_fields(overrides: Mapping[str, Mapping[str, str]], where: str) -> None:
    """Raise naming the identifier whose override's fields differ from the catalogue's."""
    reference = load_catalogue("en")
    for language, entries in overrides.items():
        for identifier, text in entries.items():
            here = f"{where}: [names.{language}] {identifier}"
            shipped = next((e[identifier] for e in reference.values() if identifier in e), "")
            try:
                given = sorted(template_fields(text))
            except ValueError as error:
                raise ValueError(f"{here} is not a valid template ({error}): {text!r}") from error
            expected = sorted(template_fields(shipped))
            if expected != given:
                raise ValueError(f"{here} must keep the catalogue's fields {expected}, not {given}")
