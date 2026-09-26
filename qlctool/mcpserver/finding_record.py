"""One check finding, as the structured record the `check` tool returns."""

from typing import Any

from ..checks.finding import Finding
from .json_value import json_value


def finding_record(finding: Finding) -> dict[str, Any]:
    """Rule id and name, severity, the function a person would press, and what is wrong."""
    return {
        "rule_id": finding.rule_id,
        "rule": finding.rule,
        "severity": finding.severity,
        "function": finding.function,
        "message": finding.message,
        "fixtures": list(finding.fixtures),
        "fields": {key: json_value(value) for key, value in finding.fields.items()},
    }
