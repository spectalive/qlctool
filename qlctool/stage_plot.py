"""Read a written stage plot: where each fixture of a real rig actually stands.

The generated band layout guesses a readable arrangement from what fixtures can
do. A plot is the opposite - somebody measured or remembered the get-in and
wrote it down, so the toolkit's job is to apply it verbatim, not to improve it.

The plot names the model it expects at every fixture ID and the loader refuses a
workspace where they do not match, because a plot is bound to a patch: re-address
or unpatch anything and the IDs move under it. Failing loudly beats hanging a
beam where a smoke machine is.
"""

from dataclasses import dataclass

from .monitor_item import MonitorItem
from .monitor_node import PropItem


@dataclass(frozen=True)
class StagePlot:
    name: str
    stage: tuple[int, int, int]
    point_of_view: str
    items: list[MonitorItem]
    # The scenery: a booth, its flightcases, a stand-in for the DJ. None of it
    # is a fixture; it is there so the preview looks like the room.
    props: list[PropItem]
    # fixture id -> the human description of where it hangs
    places: dict[int, str]

    @property
    def rigged(self) -> list[int]:
        return [item.fixture_id for item in self.items if not item.hidden]

    @property
    def spare(self) -> list[int]:
        return [item.fixture_id for item in self.items if item.hidden]
