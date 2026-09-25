"""The one place a finding's words are rendered in a language (ruling B10, round 2)."""

from ..names.names import Names
from .joined import Joined
from .phrase import Phrase


def rendered_value(names: Names, value: object) -> object:
    """A `Phrase` or `Joined` as text in `names`' language; any other value as it is.

    Other values are left alone so a template's format spec still applies to
    them: `{rate:.1f}` formats the float the rule measured.
    """
    if isinstance(value, Phrase):
        fields = {key: rendered_value(names, field) for key, field in value.fields.items()}
        # Not `names.render`: a field may be called `identifier`, as its parameter is.
        return names.display(value.message_id).format(**fields)
    if isinstance(value, Joined):
        separator = str(rendered_value(names, value.separator))
        return separator.join(str(rendered_value(names, part)) for part in value.parts)
    return value
