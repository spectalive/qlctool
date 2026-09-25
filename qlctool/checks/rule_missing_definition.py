"""A patched fixture whose definition could not be found.

2026-09-25, Plan C final review: `qlctool check examples/small-club/club.qxw`
run from the toolkit root warned "no fixture definition ... searched no
folder" and then printed `199 botones revisados, ningun problema`. Every other
rule reasons about a fixture's channels, and a fixture with no definition has
none they can see: their silence was not a clean result, it was no result.

So the missing definition is itself the finding, one per model, naming the
fixtures and the folders searched, and the run exits non-zero. A known model
patched in a mode its definition lacks is the same blindness
(`definition_outcome_of`, 2026-09-25 review) and is reported with its mode. It
is asked of the library, never of a model's name.
"""

from lxml import etree

from ..definition_outcome_of import definition_outcome_of
from ..fixture import patched_fixtures
from ..library import FixtureLibrary
from ..names.default_names import default_names
from ..names.names import Names
from ..searched_folders import searched_folders
from .finding import ERROR, Finding

RULE_ID = "missing_fixture_definition"


def check_missing_definitions(
    root: etree._Element, library: FixtureLibrary, names: Names | None = None
) -> list[Finding]:
    vocabulary = default_names() if names is None else names
    searched = searched_folders(library, vocabulary)
    unresolved: dict[tuple[str, str], list[str]] = {}
    for fixture in patched_fixtures(root):
        outcome = definition_outcome_of(fixture, library)
        if outcome.resolved:
            continue
        model = f"{fixture.manufacturer} {fixture.model}"
        if not outcome.model_known:
            message = vocabulary.render("missing_definition", searched=searched)
        else:
            model = f"{model} ({fixture.mode})"
            message = vocabulary.render("missing_mode", mode=fixture.mode)
        unresolved.setdefault((model, message), []).append(fixture.name)
    return [
        Finding(RULE_ID, ERROR, model, message, tuple(fixtures))
        for (model, message), fixtures in unresolved.items()
    ]
