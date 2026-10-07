"""A rectangle in raw DMX inside which a head is pointing at the audience."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AudienceWindow:
    """A rectangle in raw DMX: where a head is pointing at the people."""

    pan_min: int
    pan_max: int
    tilt_min: int
    tilt_max: int

    @property
    def pan_centre(self) -> int:
        return (self.pan_min + self.pan_max) // 2

    @property
    def tilt_centre(self) -> int:
        return (self.tilt_min + self.tilt_max) // 2

    @property
    def pan_span(self) -> int:
        return (self.pan_max - self.pan_min) // 2

    @property
    def tilt_span(self) -> int:
        return (self.tilt_max - self.tilt_min) // 2

    def holds(self, centre: int, span: int, axis: str) -> bool:
        """Whether a figure of this half-size around this centre stays inside."""
        low, high = (
            (self.pan_min, self.pan_max) if axis == "pan" else (self.tilt_min, self.tilt_max)
        )
        return low <= centre - span and centre + span <= high
