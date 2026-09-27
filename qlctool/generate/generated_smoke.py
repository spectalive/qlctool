"""What generate_smoke_auto built: the on/off scenes and each rhythm's chaser."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GeneratedSmoke:
    on_id: int
    off_id: int
    chaser_id: int
    # name -> function id, default first: the solo frame the console builds.
    interval_ids: dict[str, int] = field(default_factory=dict)
