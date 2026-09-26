"""The `check` tool: what the room will do, as structured findings."""

from typing import Any

from ..checks.check_workspace import check_workspace
from ..checks.entry_points import entry_points
from ..description.description_names import description_names
from ..description.load_show_description import load_show_description
from ..library_for import library_for
from ..names.shipped_names import shipped_names
from ..names.workspace_language import workspace_language
from ..workspace import Workspace
from .existing_path import existing_path
from .finding_record import finding_record
from .unresolved_models import unresolved_models


def tool_check(
    workspace: str,
    description: str | None = None,
    limit: int = 200,
    fixtures: list[str] | None = None,
) -> dict[str, Any]:
    """Every finding `qlctool check` reports, worst first; at most `limit` of them returned."""
    path = existing_path(workspace)
    loaded = Workspace.load(path)
    root = loaded.root
    library = library_for(fixtures, path)
    names = None
    if description is not None:
        names = description_names(load_show_description(existing_path(description), root))
    findings = check_workspace(loaded, library, names=names)
    said = shipped_names(workspace_language(root)) if names is None else names
    rules = {finding.rule for finding in findings}
    summary = (
        said.render("check_problems", count=len(findings), rules=len(rules))
        if findings
        else said.render("check_clean", count=len(entry_points(root)))
    )
    return {
        "workspace": str(path),
        "clean": not findings,
        "summary": summary,
        "count": len(findings),
        "findings": [finding_record(finding) for finding in findings[: max(limit, 0)]],
        "unresolved": unresolved_models(root, library),
    }
