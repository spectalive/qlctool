"""The SMC-PAD's rule provider, registered under `qlctool.rules` as `smc-pad`."""

from ..checks.rule_provider import RuleProvider
from .smc_pad_applies import smc_pad_applies
from .smc_pad_check import smc_pad_check

SMC_PAD_RULES = RuleProvider(name="smc-pad", applies=smc_pad_applies, check=smc_pad_check)
