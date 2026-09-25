"""A patched fixture whose definition could not be found.

2026-09-25, Plan C final review: `qlctool check examples/small-club/club.qxw`
run from the toolkit root warned "no fixture definition ... searched no
folder" and then printed `199 botones revisados, ningun problema`. Every other
rule reasons about a fixture's channels, and a fixture with no definition has
none they can see: their silence was not a clean result, it was no result.

So the missing definition is itself the finding, one per model, naming the
fixtures and the folders searched, and the run exits non-zero. It is asked of
the library, never of a model's name.
"""

from lxml import etree

from ..fixture import patched_fixtures
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from .finding import ERROR, Finding

RULE = "sin definicion"


def check_missing_definitions(
    root: etree._Element, library: FixtureLibrary, names: Names | None = None
) -> list[Finding]:
    vocabulary = default_names() if names is None else names
    searched = ", ".join(str(folder) for folder in library.sources) or vocabulary.display(
        "searched_no_folder"
    )
    message = vocabulary.render("missing_definition", searched=searched)
    unresolved: dict[str, list[str]] = {}
    for fixture in patched_fixtures(root):
        if library.get(fixture.manufacturer, fixture.model) is None:
            model = f"{fixture.manufacturer} {fixture.model}"
            unresolved.setdefault(model, []).append(fixture.name)
    return [
        Finding(RULE, ERROR, model, message, tuple(fixtures))
        for model, fixtures in unresolved.items()
    ]
