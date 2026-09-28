"""Lay out Virtual Console buttons for functions a generator just created, on request."""

from .generate.generate_vc_layout import generate_vc_layout
from .workspace import Workspace


def lay_out(ws: Workspace, function_ids: list[int], wanted: bool) -> None:
    """Add Virtual Console buttons for functions we just created, on request."""
    if not wanted or not function_ids:
        return
    layout = generate_vc_layout(ws, function_ids=function_ids)
    print(
        f"Laid out {len(layout.button_ids)} Virtual Console buttons "
        f"in {len(layout.frame_ids)} frame(s)"
    )
