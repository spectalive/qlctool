"""Turn QLC+'s captured log output into a pass/fail verdict."""

from .validation_result import ValidationResult

# Lines that mean the workspace itself is wrong.
ERROR_MARKERS = (
    "cannot be created",
    "overlapping with fixture",
    "No fixture definition",
    "out of bounds",
    "Unable to read from",
    "failed:",
)
# Noise QLC+ prints on every start, regardless of the file.
IGNORED_MARKERS = (
    "libpng",
    "Window position",
    "Cache already contains",
    "Q Light Controller Plus",
    "licensed under",
    "Copyright",
)


def validation_verdict(output: str) -> ValidationResult:
    if not (output or "").strip():
        # QLC+ prints its banner before it does anything else, so an empty log
        # means it never ran. Reporting that as "no complaints" is the one
        # failure this whole safety net exists to avoid.
        raise RuntimeError("QLC+ produced no output; the workspace was never actually loaded")
    errors = [
        line.strip()
        for line in (output or "").splitlines()
        if any(marker in line for marker in ERROR_MARKERS)
        and not any(marker in line for marker in IGNORED_MARKERS)
    ]
    return ValidationResult(ok=not errors, errors=errors, log=output or "")
