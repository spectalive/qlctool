"""Findings in the order a person fixes them."""

from .finding import ERROR, Finding


def fixing_order(findings: list[Finding]) -> list[Finding]:
    """Errors first, then by rule name and function."""
    return sorted(findings, key=lambda f: (f.severity != ERROR, f.rule, f.function))
