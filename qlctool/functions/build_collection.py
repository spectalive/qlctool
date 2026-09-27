"""Build a QLC+ Collection <Function> - several functions running at once.

Where a chaser plays its members one after another, a collection starts all of
them together. That is what an unattended show needs at the top: one thing to
start, which brings up the colour wheels, the movement and the smoke together.
"""

from lxml import etree

from ..constants import QLC_NS


def build_collection(
    function_id: int,
    name: str,
    member_function_ids: list[int],
    path: str | None = None,
) -> etree._Element:
    """Return a `<Function Type="Collection">` running the given functions."""
    function = etree.Element(f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("Type", "Collection")
    function.set("Name", name)
    if path is not None:
        function.set("Path", path)

    for number, member in enumerate(member_function_ids):
        step = etree.SubElement(function, f"{{{QLC_NS}}}Step")
        step.set("Number", str(number))
        step.text = str(member)

    return function
