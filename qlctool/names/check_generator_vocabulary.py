"""Refuse a vocabulary the generator cannot write yet, instead of writing a broken show."""

from .generator_language import GENERATOR_LANGUAGE
from .load_catalogue import load_catalogue
from .names import Names


def check_generator_vocabulary(names: Names) -> None:
    """Raise unless every display name `names` gives is the Spanish catalogue's.

    The generators still spell their own function, frame and caption names in
    Spanish, and look the description's names up against those spellings: a
    key bound to "Party Moment" would never reach the "Momento Fiesta" button.
    Until those literals come from the catalogue (TODO.md), only the Spanish
    vocabulary produces a correct show.
    """
    problems = []
    if names.language != GENERATOR_LANGUAGE:
        problems.append(f"language {names.language!r}")
    spanish = load_catalogue(GENERATOR_LANGUAGE)
    for identifier, text in names.overrides.get(names.language, {}).items():
        expected = next((e[identifier] for e in spanish.values() if identifier in e), None)
        if text != expected:
            problems.append(f"{identifier} = {text!r}")
    if problems:
        raise ValueError(
            "the generator still writes its Spanish vocabulary literally and cannot produce "
            + "; ".join(problems)
            + " yet (TODO.md: generator names through the catalogue)"
        )
