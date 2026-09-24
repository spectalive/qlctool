"""Whether a workspace was generated with the tablet desk."""

from lxml import etree

from ..desk_frame_identifier import desk_frame_identifier
from ..desk_function_path import DESK_FUNCTION_PATH
from ..desk_widgets import desk_widgets
from ..names.default_names import default_names
from ..xmlutil import find_local, iter_local


def tablet_desk_applies(root: etree._Element) -> bool:
    """True when the desk's burst frame or any of its burst cues is in the workspace.

    Either is enough: a burst frame deleted by hand leaves its cues behind, and
    that half-removed desk is exactly what `rule_desk_bursts` must still see.
    """
    names = default_names()
    for widget in desk_widgets(root):
        if (
            widget.kind in ("Frame", "SoloFrame")
            and desk_frame_identifier(widget.caption, names) == "desk_bursts"
        ):
            return True
    engine = find_local(root, "Engine")
    return engine is not None and any(
        function.get("Path") == DESK_FUNCTION_PATH for function in iter_local(engine, "Function")
    )
