"""Fixture group id -> the fixture ids in it."""

from lxml import etree

from ..fixture_groups import fixture_groups


def group_fixtures(root: etree._Element) -> dict[int, tuple[int, ...]]:
    return {group.group_id: group.fixture_ids for group in fixture_groups(root)}
