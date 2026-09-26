"""A description the generator will not build, said in the show's words.

Some refusals can only be made while the show is built: whether a fixture
group has a rigged colour cell depends on the stage plot, and the plot is
applied by the build itself. `newshow` reports this like the refusals it makes
before building - the message and nothing else.
"""


class BuildRefusalError(ValueError):
    """Raised by a build stage with the message `newshow` exits with."""
