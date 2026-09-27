"""What generate_stage_layout wrote: the stage, its viewpoint and its rows."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedStage:
    stage: tuple[int, int, int]
    point_of_view: str
    # band -> fixture IDs placed on that row, left to right
    rows: dict[str, list[int]]

    @property
    def placed(self) -> int:
        return sum(len(ids) for ids in self.rows.values())
