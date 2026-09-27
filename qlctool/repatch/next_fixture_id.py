"""The next free fixture ID a workspace can patch a new fixture at."""

from lxml import etree

from ..fixture import patched_fixtures


def next_fixture_id(root: etree._Element) -> int:
    """One past the highest patched fixture ID, or 0 when the workspace has none."""
    ids = [f.fixture_id for f in patched_fixtures(root)]
    return max(ids) + 1 if ids else 0
