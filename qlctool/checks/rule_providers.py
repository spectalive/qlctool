"""Every rule provider installed under `qlctool.rules`, the toolkit's own and a show's.

The group is read from installed package metadata, so a checkout whose
`pyproject.toml` gained a provider has to be reinstalled (`pip install -e`)
before the provider exists. That is exactly the failure that would pass in
silence - a desk check that stops running looks like a desk with no problems -
so a provider this checkout's `pyproject.toml` declares and the install lacks
is an error.
"""

from functools import cache
from importlib.metadata import entry_points as installed_entry_points

from .declared_rule_providers import declared_rule_providers
from .rule_group import RULE_GROUP
from .rule_provider import RuleProvider


@cache
def rule_providers() -> tuple[RuleProvider, ...]:
    """The installed providers, by name."""
    providers = []
    for point in sorted(installed_entry_points(group=RULE_GROUP), key=lambda p: p.name):
        provider = point.load()
        if not isinstance(provider, RuleProvider):
            raise TypeError(
                f"{RULE_GROUP} entry point {point.name!r} is not a RuleProvider: {point.value}"
            )
        providers.append(provider)
    missing = sorted(set(declared_rule_providers()) - {p.name for p in providers})
    if missing:
        raise RuntimeError(
            f"qlctool's own rule providers are not installed ({', '.join(missing)}): "
            "run `.venv/bin/pip install -e '.[dev]'` in the qlctool checkout so its entry points are written"
        )
    return tuple(providers)
