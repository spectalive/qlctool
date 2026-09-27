"""One button's family-frame problem: which function, and what to say."""

from dataclasses import dataclass

from .phrase import Phrase


@dataclass(frozen=True)
class Problem:
    function_id: int
    # A `[findings]` entry and its fields (ruling B10, round 2).
    said: Phrase
