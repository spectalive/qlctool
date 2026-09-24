"""What an identifier looks like: English snake case, starting with a letter."""

import re

IDENTIFIER_PATTERN = re.compile(r"[a-z][a-z0-9_]*")
