"""xdformat: the .xd crossword format — parser, serializer, converters.

The core (this package, no dependencies) parses and emits .xd files.
Converters from other puzzle formats need the [convert] extra:

    pip install xdformat[convert]
"""

__version__ = '0.1.0'

from .xdfile import (
    xdfile, parse,
    Error, IncompletePuzzleParse, PuzzleParseError,
    BLOCK_CHAR, OPEN_CHAR, UNKNOWN_CHAR, NON_ANSWER_CHARS, REBUS_SEP,
)

__all__ = [
    'xdfile', 'parse',
    'Error', 'IncompletePuzzleParse', 'PuzzleParseError',
    'BLOCK_CHAR', 'OPEN_CHAR', 'UNKNOWN_CHAR', 'NON_ANSWER_CHARS', 'REBUS_SEP',
]
