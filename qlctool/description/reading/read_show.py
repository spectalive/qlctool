"""[show]: the show's name and the language its names are written in."""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ...names.default_language import DEFAULT_LANGUAGE
from ...names.shipped_languages import shipped_languages
from .reject_unknown_keys import reject_unknown_keys


def read_show(table: Mapping[str, Any], path: Path) -> tuple[str, str]:
    """(name, language). The name defaults to the file's stem, the language to Spanish (B11)."""
    where = f"{path}: [show]"
    reject_unknown_keys(table, ("name", "language"), where)
    name = table.get("name", path.stem)
    language = table.get("language", DEFAULT_LANGUAGE)
    if not isinstance(name, str) or not name:
        raise ValueError(f"{where} name must be a non-empty string")
    if language not in shipped_languages():
        raise ValueError(
            f"{where} no catalogue for language {language!r}; "
            f"shipped: {', '.join(shipped_languages())}"
        )
    return name, language
