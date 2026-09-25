"""The two rules that read the console's frames and captions, not the functions behind them.

Split out of `check_workspace` when the second one came (2026-09-25) so that
`run.py` stays under the module cap: an empty frame promises something to
press, and a caption promises something on the rig.
"""

from lxml import etree

from .finding import Finding
from .rule_caption_promise import check_caption_promise
from .rule_empty_frame import check_empty_frames
from .show_graph import ShowGraph


def console_caption_findings(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    """What `marco vacio` and `rotulo que promete lo que no hay` report, in that order."""
    return check_empty_frames(root) + check_caption_promise(graph, root)
