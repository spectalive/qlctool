"""The tablet desk's rule provider, registered under `qlctool.rules` as `tablet_desk`."""

from ..checks.rule_provider import RuleProvider
from .tablet_desk_applies import tablet_desk_applies
from .tablet_desk_bounded_latches import tablet_desk_bounded_latches
from .tablet_desk_check import tablet_desk_check

TABLET_DESK_RULES = RuleProvider(
    name="tablet_desk",
    applies=tablet_desk_applies,
    check=tablet_desk_check,
    bounded_latches=tablet_desk_bounded_latches,
)
