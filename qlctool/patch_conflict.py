"""Find DMX address overlaps in a workspace's patch.

Two fixtures sharing a channel on the same universe is the classic patch bug:
QLC+ loads it happily and the show misbehaves on stage. Every re-patch operation
checks this before writing, and it is worth running on its own after any manual
edit.
"""

from dataclasses import dataclass

from .patched_fixture import PatchedFixture


@dataclass(frozen=True)
class PatchConflict:
    first: PatchedFixture
    second: PatchedFixture
    universe: int
    overlap: range  # 0-based channel numbers both fixtures claim

    def describe(self) -> str:
        start = self.overlap.start + 1  # 1-based, as QLC+ shows addresses
        stop = self.overlap.stop  # inclusive end in 1-based terms
        return (
            f"U{self.universe} channels {start}-{stop}: "
            f"[{self.first.fixture_id}] {self.first.name} overlaps "
            f"[{self.second.fixture_id}] {self.second.name}"
        )
