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
from .finding import ERROR, Finding
from .phrase import Phrase
from .searched_folders_said import searched_folders_said

RULE_ID = "missing_fixture_definition"


def check_missing_definitions(root: etree._Element, library: FixtureLibrary) -> list[Finding]:
    # The folders, or the catalogue's word for none, said in the workspace's language.
    searched = searched_folders_said(library)
    unresolved: dict[str, list[str]] = {}
    said: dict[str, Phrase] = {}
    for fixture in patched_fixtures(root):
        outcome = definition_outcome_of(fixture, library)
        if outcome.resolved:
            continue
        model = f"{fixture.manufacturer} {fixture.model}"
        if not outcome.model_known:
            said[model] = Phrase("missing_definition", {"searched": searched})
        else:
            model = f"{model} ({fixture.mode})"
            said[model] = Phrase("missing_mode", {"mode": fixture.mode})
        unresolved.setdefault(model, []).append(fixture.name)
    return [
        Finding(
            rule_id=RULE_ID,
            severity=ERROR,
            function=model,
            message_id=said[model].message_id,
            fields=said[model].fields,
            fixtures=tuple(fixtures),
        )
        for model, fixtures in unresolved.items()
    ]
