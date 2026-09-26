"""One EFX as the room sees it: its figure's settings and its rigged heads."""

from .efx_head import EfxHead

MovementFigure = tuple[tuple[bytes, ...], tuple[EfxHead, ...]]
