"""Command-line entry point for qlctool, kept at its published import path.

`pyproject.toml` and the projects that pin qlctool import `qlctool.cli:main`.
"""

from .main import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
