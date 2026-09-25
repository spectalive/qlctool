"""Why the desk map refuses a show whose bursts are broken, in the show's words."""

from .checks.finding import Finding
from .checks.phrase import Phrase
from .checks.rendered_value import rendered_value
from .names.names import Names


def desk_burst_refusal(findings: list[Finding], names: Names) -> str:
    """The refusal, each finding's message rendered in `names`' language.

    `Finding.message` is the Spanish rendering outside `check_workspace`, so an
    English show would be refused in Spanish (2026-09-25).
    """
    messages = (
        str(rendered_value(names, Phrase(f.message_id, f.fields))) if f.message_id else f.message
        for f in findings
    )
    return "invalid desk bursts: " + "; ".join(messages)
