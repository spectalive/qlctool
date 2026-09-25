"""One thing wrong with a show, said in a sentence somebody can act on.

A finding is not a stack trace: it names the function an operator would press,
the fixture that misbehaves, and what will be seen in the room. "BLANCO TOTAL
leaves BEAM 230W 7R #1 dark" is a finding; "missing offset 6" is not.

A rule says which rule it is by `rule_id`, the English identifier of its
`[checks]` catalogue entry, and what it found by `message_id` and `fields`, an
entry of `[findings]` and the values that fill it. `rule` and `message` are
what a person reads, in the workspace's language: `check_workspace` fills both
(`named_findings`). Until then `message` reads in Spanish, the language every
show was checked in before ruling B10, so a rule called on its own still says
something. A provider's own rule that no catalogue names may pass its display
name as the identifier and its text as `message`: both are shown as given.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

from ..names.default_names import default_names
from .phrase import Phrase
from .rendered_value import rendered_value

ERROR = "error"
WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    """One problem, attributed to the function somebody would press."""

    rule_id: str
    severity: str
    function: str
    message: str = ""
    fixtures: tuple[str, ...] = field(default_factory=tuple)
    rule: str = ""
    message_id: str = ""
    fields: Mapping[str, object] = field(default_factory=dict, hash=False)

    def __post_init__(self) -> None:
        if self.message_id and not self.message:
            said = rendered_value(default_names(), Phrase(self.message_id, self.fields))
            object.__setattr__(self, "message", str(said))

    def __str__(self) -> str:
        where = f" [{', '.join(self.fixtures)}]" if self.fixtures else ""
        return f"{self.severity}: {self.function}: {self.message}{where}"
