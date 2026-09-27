"""What generate_vc_layout built: the group frames and their buttons."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedLayout:
    frame_ids: list[int]
    button_ids: list[int]
