"""Put functions at the head of an existing Collection, renumbering its steps."""

from lxml import etree

from ..constants import QLC_NS
from ..findall_local import findall_local
from ..workspace import Workspace


def prepend_collection_steps(workspace: Workspace, collection_id: int, members: list[int]) -> None:
    """Start `members` first in the Collection `collection_id`, before its own steps."""
    collection = next(
        f
        for f in findall_local(workspace.engine, "Function")
        if f.get("ID") == str(collection_id) and f.get("Type") == "Collection"
    )
    steps = findall_local(collection, "Step")
    existing = [int(step.text or "") for step in steps]
    for step in steps:
        collection.remove(step)
    for number, member in enumerate([*members, *existing]):
        step = etree.SubElement(collection, f"{{{QLC_NS}}}Step")
        step.set("Number", str(number))
        step.text = str(member)
