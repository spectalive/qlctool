"""The OSC surface's rule provider, registered under `qlctool.rules` as `osc`."""

from ..checks.rule_provider import RuleProvider
from .osc_applies import osc_applies
from .osc_check import osc_check

OSC_RULES = RuleProvider(name="osc", applies=osc_applies, check=osc_check)
