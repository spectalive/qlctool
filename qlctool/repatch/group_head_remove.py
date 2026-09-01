"""Take a fixture out of a fixture group without disturbing the rest of it.

A fixture group is two things at once: the set a colour bank and a matrix are
generated for, and the X/Y grid a matrix paints across. Putting a fixture in a
group to fill the grid therefore also puts it in the colour bank, which is how
the four BEAM 230W 7R - no RGB, nothing for a matrix to paint on them, in the
`BarrasLed` group purely so its third row existed - ended up with two of the
show's colour wheels writing their colour wheel at once.

The cells the fixture leaves behind stay empty rather than being closed up. A
matrix paints the grid the group *declares*, so shuffling the survivors would
change where every remaining head sits in every pattern; leaving the hole moves
nothing.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local


def remove_group_head(root: etree._Element, group_id: int, fixture_id: int) -> int:
    """Remove every head of one fixture from a group; returns how many.

    Raises when the group does not exist, when the fixture is not in it, or
    when removing it would leave the group empty - an empty group generates a
    matrix that paints nothing and a colour bank with no fixtures.
    """
    group = _group(root, group_id)
    heads = findall_local(group, "Head")
    doomed = [head for head in heads if head.attrib.get("Fixture") == str(fixture_id)]
    if not doomed:
        raise ValueError(f"fixture {fixture_id} is not in group {group_id} ({_name(group)!r})")
    if len(doomed) == len(heads):
        raise ValueError(
            f"removing fixture {fixture_id} would leave group {group_id} "
            f"({_name(group)!r}) with no heads at all"
        )
    for head in doomed:
        group.remove(head)
    return len(doomed)


def _group(root: etree._Element, group_id: int) -> etree._Element:
    for element in iter_local(root, "FixtureGroup"):
        if element.attrib.get("ID") == str(group_id):
            return element
    raise KeyError(f"no fixture group with ID {group_id}")


def _name(group: etree._Element) -> str:
    name = find_local(group, "Name")
    return (name.text or "").strip() if name is not None else ""
