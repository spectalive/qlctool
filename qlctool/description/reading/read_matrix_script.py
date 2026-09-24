"""One `[[groups.<group>.matrices]]` entry: a script, its colours, its properties."""

from typing import Any

from ...matrix_algorithms import CuratedScript
from ...names.names import Names
from .named import named
from .reject_unknown_keys import reject_unknown_keys


def read_matrix_script(entry: Any, group: str, names: Names, where: str) -> CuratedScript:
    """The curated script `entry` describes for `group`; a ValueError saying what is wrong."""
    if not isinstance(entry, dict):
        raise ValueError(f"{where}: a matrix is a table with script, colors and properties")
    reject_unknown_keys(entry, ("script", "colors", "properties"), where)
    script, colors = entry.get("script"), entry.get("colors", [])
    properties = entry.get("properties", {})
    if not isinstance(script, str) or not script:
        raise ValueError(f"{where}: script is the RGB script's name as QLC+ has it")
    if not isinstance(colors, list) or not 1 <= len(colors) <= 2:
        raise ValueError(f"{where}: colors names one or two palette colours")
    if not isinstance(properties, dict) or not all(isinstance(v, str) for v in properties.values()):
        raise ValueError(f"{where}: properties are the script's own names with string values")
    identified = tuple(named(names, c, "colors", where) for c in colors)
    return CuratedScript(group, script, dict(properties), identified)
