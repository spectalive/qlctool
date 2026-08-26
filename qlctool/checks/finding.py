"""One thing wrong with a show, said in a sentence somebody can act on.

A finding is not a stack trace: it names the function an operator would press,
the fixture that misbehaves, and what will be seen in the room. "BLANCO TOTAL
leaves BEAM 230W 7R #1 dark" is a finding; "missing offset 6" is not.
"""

from dataclasses import dataclass, field

ERROR = "error"
WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    """One problem, attributed to the function somebody would press."""

    rule: str
    severity: str
    function: str
    message: str
    fixtures: tuple[str, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        where = f" [{', '.join(self.fixtures)}]" if self.fixtures else ""
        return f"{self.severity}: {self.function}: {self.message}{where}"
