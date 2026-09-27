"""Two patched fixtures carrying one ID.

Round G review, 2026-09-26: the caption rule stepped aside on a rig with a
duplicated fixture ID, because it counted patched fixtures against the graph's
capabilities and the graph keys them by ID, so two fixtures were one entry.
That rule now looks each fixture up, but the patch itself was never judged.

QLC+ keeps one fixture per ID when it loads a workspace, and every rule here
reasons about the one the graph kept. So a scene lights the fixture QLC+ kept
and the other stays dark, and no rule can say so: their silence is one fixture
fewer than the patch. The duplicated ID is the finding, naming the fixtures
that share it.
"""

from lxml import etree

from ..patched_fixtures import patched_fixtures
from .finding import ERROR, Finding

RULE_ID = "duplicate_fixture_id"


def check_duplicate_fixture_ids(root: etree._Element) -> list[Finding]:
    names_by_id: dict[int, list[str]] = {}
    for fixture in patched_fixtures(root):
        names_by_id.setdefault(fixture.fixture_id, []).append(fixture.name)
    return [
        Finding(
            rule_id=RULE_ID,
            severity=ERROR,
            function=f"ID {fixture_id}",
            message_id="duplicate_fixture_id_shared",
            fields={"id": fixture_id, "count": len(names)},
            fixtures=tuple(names),
        )
        for fixture_id, names in sorted(names_by_id.items())
        if len(names) > 1
    ]
