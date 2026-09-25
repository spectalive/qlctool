"""What `qlctool check` prints, in the workspace's language (ruling B10, 2026-09-25).

The rule names are already the workspace's (`named_in_order`); the summary
lines around them come from the same catalogue, so an English show reads
"199 buttons checked, no problems" and Vibra still reads "522 botones
revisados, ningun problema".
"""

from lxml import etree

from .checks.entry_points import entry_points
from .checks.finding import Finding
from .names.shipped_names import shipped_names
from .names.workspace_language import workspace_language


def print_check_report(
    where: str, root: etree._Element, findings: list[Finding], limit: int
) -> int:
    """Print the findings grouped by rule, at most `limit` each; the exit code."""
    names = shipped_names(workspace_language(root))
    if not findings:
        print(f"{where}: {names.render('check_clean', count=len(entry_points(root)))}")
        return 0

    by_rule: dict[str, list[Finding]] = {}
    for finding in findings:
        by_rule.setdefault(finding.rule, []).append(finding)
    print(f"{where}: {names.render('check_problems', count=len(findings), rules=len(by_rule))}")
    for rule, group in by_rule.items():
        print(f"\n  {rule} ({len(group)}):")
        for finding in group[:limit]:
            spot = f"  [{', '.join(finding.fixtures)}]" if finding.fixtures else ""
            print(f"    {finding.function}: {finding.message}{spot}")
        if len(group) > limit:
            print(f"    {names.render('check_more', count=len(group) - limit)}")
    return 1
