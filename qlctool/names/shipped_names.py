"""A `Names` over every shipped catalogue, in one show language."""

from collections.abc import Mapping

from .load_catalogue import load_catalogue
from .name_resolution_error import NameResolutionError
from .names import Names
from .shipped_languages import shipped_languages


def shipped_names(
    language: str = "es", overrides: Mapping[str, Mapping[str, str]] | None = None
) -> Names:
    """The shipped catalogues, answering in `language`, with a show's overrides on top."""
    languages = shipped_languages()
    if language not in languages:
        raise NameResolutionError(
            f"no catalogue for language {language!r}; shipped: {', '.join(languages)}"
        )
    return Names(
        language=language,
        catalogues={code: load_catalogue(code) for code in languages},
        overrides=dict(overrides or {}),
    )
