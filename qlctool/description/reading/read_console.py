"""[console]: the canvas, the held functions, and [console.keys]."""

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from ...names.names import Names
from ..console_settings import ConsoleSettings
from .identified_keys import identified_keys
from .list_at import list_at
from .named import named
from .reject_unknown_keys import reject_unknown_keys
from .table_at import table_at


def read_console(
    table: Mapping[str, Any], base: ConsoleSettings, names: Names, where: str
) -> ConsoleSettings:
    """The base console with the canvas, the keys or the held functions replaced whole (F7)."""
    here = f"{where}: [console]"
    reject_unknown_keys(table, ("canvas", "keys", "flash_functions"), here)
    changes: dict[str, Any] = {}
    if "canvas" in table:
        canvas = table_at(table, "canvas", here)
        reject_unknown_keys(canvas, ("width", "height"), f"{here} canvas")
        size = (canvas.get("width"), canvas.get("height"))
        if not all(isinstance(v, int) and not isinstance(v, bool) and v > 0 for v in size):
            raise ValueError(f"{here} canvas needs a positive width and height in pixels")
        changes["canvas"] = size
    if "keys" in table:
        keys = table_at(table, "keys", here)
        for name, key in keys.items():
            if not isinstance(key, str) or not key:
                raise ValueError(f'{here} keys.{name} must be a key name such as "Q" or "F1"')
        spelled = identified_keys(keys, names, "functions", f"{here} keys")
        changes["keys"] = {identifier: keys[name] for identifier, name in spelled.items()}
    if "flash_functions" in table:
        changes["flash_functions"] = tuple(
            named(names, n, "functions", f"{here} flash_functions")
            for n in list_at(table, "flash_functions", here)
        )
    return replace(base, **changes)
