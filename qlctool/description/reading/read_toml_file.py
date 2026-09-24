"""Parse a description file, naming the file when it is not TOML."""

import tomllib
from pathlib import Path
from typing import Any


def read_toml_file(path: Path) -> dict[str, Any]:
    """The parsed document; a ValueError naming the file on a syntax error or a missing file."""
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"{path}: cannot read the description: {error.strerror}") from error
    except tomllib.TOMLDecodeError as error:
        raise ValueError(f"{path}: not valid TOML: {error}") from error
