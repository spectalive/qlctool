"""The MCP server's refusals, from the `[messages]` catalogue."""

from ..names.shipped_names import shipped_names


def mcp_message(identifier: str, **fields: object) -> str:
    """The English sentence for `identifier`: the server answers an agent, not a show."""
    return shipped_names("en").render(identifier, **fields)
