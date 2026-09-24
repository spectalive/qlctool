"""The rule providers this checkout's `pyproject.toml` declares.

A checkout pulled without `pip install -e` has a stale entry-point list, and a
desk check that stops running looks like a desk with no problems (R10). The
names are read from the project file rather than spelled here, so core never
names a controller. An installed wheel has no project file beside it and
declares nothing - it cannot be stale.
"""

import tomllib
from pathlib import Path

from .rule_group import RULE_GROUP


def declared_rule_providers(project: Path | None = None) -> tuple[str, ...]:
    """Entry-point names under `qlctool.rules` in the qlctool project file, sorted."""
    folder = Path(__file__).resolve().parents[2] if project is None else project
    path = folder / "pyproject.toml"
    if not path.is_file():
        return ()
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    table = document.get("project", {})
    if table.get("name") != "qlctool":
        return ()
    return tuple(sorted(table.get("entry-points", {}).get(RULE_GROUP, {})))
