"""Whether this Mac can execute a binary, before QLC+ is launched to find out.

An x86_64-only QLC+ on an arm64 Mac without Rosetta fails with "Bad CPU type"
before it logs anything, which the validator would read as a QLC+ that never
finished loading.
"""

import platform
from pathlib import Path

from .mach_o_architectures import mach_o_architectures


def runs_here(executable: str, machine: str | None = None, rosetta: bool | None = None) -> bool:
    """True when the file exists and its Mach-O slices include one this CPU runs.

    A file that is not Mach-O (a script, a Linux ELF) is left to the system: True.
    """
    try:
        with Path(executable).open("rb") as handle:
            header = handle.read(4096)
    except OSError:
        return False
    architectures = mach_o_architectures(header)
    if architectures is None:
        return True
    cpu = machine or platform.machine()
    if cpu in architectures:
        return True
    translated = (
        Path("/Library/Apple/usr/libexec/oah/libRosettaRuntime").exists()
        if rosetta is None
        else rosetta
    )
    return cpu == "arm64" and "x86_64" in architectures and translated
