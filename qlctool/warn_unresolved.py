"""Say which fixtures will be skipped, instead of skipping them in silence."""

import sys

from lxml import etree

from .library import FixtureLibrary
from .unresolved_fixtures import unresolved_fixtures


def warn_unresolved(root: etree._Element, library: FixtureLibrary) -> None:
    """One stderr line per missing model, and where the definitions were looked for."""
    missing = unresolved_fixtures(root, library)
    if not missing:
        return
    searched = ", ".join(str(folder) for folder in library.sources) or "no folder"
    print(
        f"qlctool: no fixture definition for {', '.join(missing)} (searched {searched}); "
        "pass --fixtures, set QLCTOOL_FIXTURES, or add a qlctool.toml",
        file=sys.stderr,
    )
