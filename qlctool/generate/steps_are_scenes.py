"""Whether a named chaser steps only Scenes."""

from ..workspace import Workspace
from ..xmlutil import findall_local


def steps_are_scenes(workspace: Workspace, name: str) -> bool:
    """True when every step of the named chaser is a Scene.

    A chaser hands its own fade and duration to whatever it starts. A Scene
    has no clock of its own to corrupt; an EFX and an RGBMatrix both do.
    """
    by_id = {f.attrib.get("ID"): f for f in workspace.engine if f.tag.endswith("}Function")}
    function = next((f for f in workspace.engine if f.attrib.get("Name") == name), None)
    if function is None:
        return False
    steps = [by_id.get(step.text) for step in findall_local(function, "Step") if step.text]
    return bool(steps) and all(
        step is not None and step.attrib.get("Type") == "Scene" for step in steps
    )
