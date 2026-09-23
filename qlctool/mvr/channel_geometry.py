"""The geometry a DMX channel drives: its head's beam, the yoke, the head, or
the parent of every beam when no head claims it.
"""

from .. import roles
from ..definition import Channel
from .geometry_plan import GeometryPlan


def channel_geometry(channel: Channel, head: int | None, plan: GeometryPlan) -> str:
    if head is not None and head < len(plan.beams):
        return plan.beams[head]
    if channel.role == roles.PAN and plan.pan:
        return plan.pan
    if channel.role == roles.TILT and plan.tilt:
        return plan.tilt
    return plan.emitter
