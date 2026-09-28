"""The beams' two static rests, and what a pick starts beside them.

generate_rest_positions fills one of these; the beam rotation reads fan_id and
cross_id as rest steps, and the final GeneratedFamilies reads fan_id and
companions straight off it.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RestPositions:
    fan_id: int | None
    cross_id: int | None
    hold_id: int | None
    companions: dict[int, list[int]] = field(default_factory=dict)
