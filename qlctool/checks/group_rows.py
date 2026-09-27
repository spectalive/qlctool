"""One fixture group's heads, grouped by row, in patch order."""

from lxml import etree


def group_rows(root: etree._Element, group_id: int) -> dict[int, list[tuple[int, int]]]:
    rows: dict[int, list[tuple[int, int]]] = {}
    for group in root.iter():
        if group.tag.rpartition("}")[2] != "FixtureGroup":
            continue
        if group.attrib.get("ID") != str(group_id):
            continue
        for head in group:
            if head.tag.rpartition("}")[2] != "Head":
                continue
            rows.setdefault(int(head.attrib["Y"]), []).append(
                (int(head.attrib["X"]), int(head.attrib["Fixture"]))
            )
    return rows
