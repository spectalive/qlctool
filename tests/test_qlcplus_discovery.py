"""2026-09-25: the suite skipped ten QLC+ tests on a Mac with QLC+ 5.2.2 installed.

`DEFAULT_BINARIES` knew `QLC+ 4.app` and `QLC+.app`; the installers name their
bundles `QLC+ 4.13.1.app` and `QLC+ 5.2.2.app`, and the 4.13.1 binary is
x86_64-only on an arm64 Mac with no Rosetta. Discovery scans the versioned
bundles and keeps only what this CPU can execute.
"""

import struct
from pathlib import Path

from qlctool import validate
from qlctool.mach_o_architectures import mach_o_architectures
from qlctool.qlcplus_bundles import qlcplus_bundles
from qlctool.qlcplus_candidates import qlcplus_candidates
from qlctool.runs_here import runs_here

X86_64 = b"\xcf\xfa\xed\xfe" + struct.pack("<i", 0x01000007) + bytes(24)
ARM64 = b"\xcf\xfa\xed\xfe" + struct.pack("<i", 0x0100000C) + bytes(24)
FAT = (
    b"\xca\xfe\xba\xbe"
    + struct.pack(">I", 2)
    + struct.pack(">iiIII", 0x01000007, 3, 0, 0, 0)
    + struct.pack(">iiIII", 0x0100000C, 0, 0, 0, 0)
)


def _binary(applications: Path, bundle: str, name: str, header: bytes) -> str:
    path = applications / bundle / "Contents" / "MacOS" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header)
    return str(path)


def test_the_header_names_its_architectures():
    assert mach_o_architectures(X86_64) == frozenset({"x86_64"})
    assert mach_o_architectures(ARM64) == frozenset({"arm64"})
    assert mach_o_architectures(FAT) == frozenset({"x86_64", "arm64"})
    assert mach_o_architectures(b"#!/bin/sh\n") is None


def test_an_intel_binary_runs_on_arm_only_through_rosetta(tmp_path):
    intel = _binary(tmp_path, "QLC+ 4.13.1.app", "qlcplus", X86_64)
    assert not runs_here(intel, machine="arm64", rosetta=False)
    assert runs_here(intel, machine="arm64", rosetta=True)
    assert runs_here(intel, machine="x86_64", rosetta=False)
    assert not runs_here(str(tmp_path / "missing"), machine="arm64", rosetta=True)


def test_bundles_are_listed_newest_first(tmp_path):
    old = _binary(tmp_path, "QLC+ 4.13.1.app", "qlcplus", X86_64)
    new = _binary(tmp_path, "QLC+ 5.2.2.app", "qlcplus-qml", ARM64)
    _binary(tmp_path, "Not QLC+.app", "qlcplus", ARM64)
    assert qlcplus_bundles(tmp_path) == [((5, 2, 2), new), ((4, 13, 1), old)]
    assert qlcplus_bundles(tmp_path / "absent") == []


def test_the_widgets_build_wins_when_it_can_run(tmp_path):
    old = _binary(tmp_path, "QLC+ 4.13.1.app", "qlcplus", X86_64)
    new = _binary(tmp_path, "QLC+ 5.2.2.app", "qlcplus-qml", ARM64)
    with_rosetta = qlcplus_candidates((), tmp_path, lambda p: runs_here(p, "arm64", True))
    without = qlcplus_candidates((), tmp_path, lambda p: runs_here(p, "arm64", False))
    assert with_rosetta == [old, new]
    assert without == [new]


def test_fixed_paths_follow_the_versioned_bundles_without_repeats(tmp_path):
    new = _binary(tmp_path, "QLC+ 5.2.2.app", "qlcplus-qml", ARM64)
    fixed = _binary(tmp_path / "usr", "bin", "qlcplus-qml", ARM64)
    found = qlcplus_candidates((new, fixed, str(tmp_path / "nowhere")), tmp_path, lambda p: True)
    assert found == [new, fixed]


def test_the_override_still_wins(monkeypatch, tmp_path):
    chosen = _binary(tmp_path, "custom", "qlcplus", ARM64)
    monkeypatch.setenv("QLCTOOL_QLCPLUS", chosen)
    monkeypatch.setattr(validate, "qlcplus_candidates", lambda fixed: ["/elsewhere"])
    assert validate.qlcplus_binary() == chosen


def test_discovery_feeds_the_validator(monkeypatch):
    monkeypatch.delenv("QLCTOOL_QLCPLUS", raising=False)
    monkeypatch.setattr(validate, "qlcplus_candidates", lambda fixed: ["/first", "/second"])
    assert validate.qlcplus_binary() == "/first"
