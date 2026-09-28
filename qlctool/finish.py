"""Report where a generated workspace went and, on request, validate it."""

from pathlib import Path

from .validate_workspace import validate_workspace


def finish(out: Path, validate: bool) -> int:
    """Report where the file went and, on request, that QLC+ accepts it."""
    print(f"Wrote {out}")
    if not validate:
        print("Open it in QLC+ to verify before using it in a show.")
        return 0
    result = validate_workspace(out)
    if result.ok:
        print("Validated: QLC+ loaded it with no complaints")
        return 0
    print("QLC+ reported problems loading it:")
    for error in result.errors:
        print(f"  {error}")
    return 1
