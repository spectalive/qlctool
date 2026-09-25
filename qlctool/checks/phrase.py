"""A catalogue entry and its fields, before anyone knows which language to say it in.

A rule does not know the workspace's language (ruling B10): it states what it
found as an identifier of the `[findings]` catalogue section and the fields
that fill it, and `named_findings` renders it once the language is known. A
field may itself be a `Phrase` - a word the catalogue owns, such as "prisma" -
so that no Spanish reaches a finding from code.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Phrase:
    """An identifier of a catalogue entry and the values of its `{fields}`."""

    message_id: str
    fields: Mapping[str, object] = field(default_factory=dict, hash=False)
