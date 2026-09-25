"""An override may reword a frame's explanation, never the head the frame is found by."""

from collections.abc import Mapping

from ...names.frame_caption_head import frame_caption_head
from ...names.load_catalogue import load_catalogue


def reject_frame_head_renames(overrides: Mapping[str, Mapping[str, str]], where: str) -> None:
    """Raise when a `frames` override changes the text before " — ", ignoring case.

    `qlctool check` and the desk find frames by their shipped head (ruling
    B12): a renamed head builds a console the checker cannot read, and the
    desk bursts vanish without a finding (2026-09-25, final review of Plan B).
    """
    for language, entries in overrides.items():
        frames = load_catalogue(language)["frames"]
        for identifier, word in entries.items():
            if identifier not in frames:
                continue
            if frame_caption_head(word) != frame_caption_head(frames[identifier]):
                raise ValueError(
                    f"{where}: [names.{language}] {identifier} = {word!r} renames the frame "
                    f"head {frames[identifier].split(' — ')[0]!r}: frame heads cannot be renamed "
                    "yet, because the checker and the desk find frames by their shipped head; "
                    "reword only the text after ' — '"
                )
