"""Say which fixtures will be skipped, instead of skipping them in silence.

2026-09-25: a known model patched in a mode its definition lacks was warned
as "no fixture definition ... pass --fixtures", advice that cannot help. The
fixtures `resolved_definition` rejects are told apart the way
`rule_missing_definition` tells them: no definition for the model, or a
definition without the patched mode, which is to be repatched.
"""

import sys

from lxml import etree

from .library import FixtureLibrary
from .names.names import Names
from .names.shipped_names import shipped_names
from .searched_folders import searched_folders
from .unresolved_fixtures import unresolved_fixtures


def warn_unresolved(
    root: etree._Element, library: FixtureLibrary, names: Names | None = None
) -> None:
    """One stderr line for the unknown models, and one per known model in a missing mode."""
    vocabulary = shipped_names("en") if names is None else names
    unknown: dict[str, None] = {}
    lines: list[str] = []
    for fixture in unresolved_fixtures(root, library):
        model = f"{fixture.manufacturer} {fixture.model}"
        definition = library.get(fixture.manufacturer, fixture.model)
        if definition is None:
            unknown[model] = None
            continue
        lines.append(
            vocabulary.render(
                "unresolved_mode", model=model, mode=fixture.mode, modes=", ".join(definition.modes)
            )
        )
    if unknown:
        searched = searched_folders(library, vocabulary)
        lines.insert(
            0, vocabulary.render("unresolved_models", models=", ".join(unknown), searched=searched)
        )
    for line in lines:
        print(f"qlctool: {line}", file=sys.stderr)
