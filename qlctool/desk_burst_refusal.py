"""Why the desk map refuses a show whose bursts are broken, in the show's words."""

from .checks.finding import Finding
from .checks.phrase import Phrase
from .checks.rendered_value import rendered_value
from .names.names import Names


def desk_burst_refusal(findings: list[Finding], names: Names) -> str:
    """The refusal, its frame and each finding's message in `names`' language.

    `Finding.message` is the Spanish rendering outside `check_workspace`, so an
    English show would be refused in Spanish (2026-09-25); the frame around
    them stayed English on a Spanish show until 2026-09-26.
    """
    messages = (
        str(rendered_value(names, Phrase(f.message_id, f.fields))) if f.message_id else f.message
        for f in findings
    )
    return names.render("desk_bursts_invalid", findings="; ".join(messages))
