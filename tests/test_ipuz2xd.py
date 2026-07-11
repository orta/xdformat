"""End-to-end .ipuz conversion, covering both ipuz clue entry forms."""

import json

from xdformat.crossword import from_ipuz
from xdformat.ipuz2xd import parse_ipuz

IPUZ_PAIR_CLUES = {
    "version": "http://ipuz.org/v2",
    "kind": ["http://ipuz.org/crossword#1"],
    "dimensions": {"width": 3, "height": 3},
    "title": "Test Puzzle",
    "author": "Test Author",
    "puzzle": [[1, 0, 2], [0, "#", 0], [3, 0, 0]],
    "solution": [["A", "B", "C"], ["D", "#", "E"], ["F", "G", "H"]],
    "clues": {
        "Across": [[1, "First across"], [3, "Second across"]],
        "Down": [[1, "First down"], [2, "Second down"]],
    },
}


def test_parse_ipuz_pair_clues():
    contents = json.dumps(IPUZ_PAIR_CLUES).encode('utf-8')
    xd = parse_ipuz(contents, 'test2024-01-01.ipuz')
    assert xd.get_header('Title') == 'Test Puzzle'
    assert xd.get_header('Author') == 'Test Author'
    assert xd.get_header('Date') == '2024-01-01'
    assert xd.grid == ['ABC', 'D#E', 'FGH']
    assert dict((d + str(n), (clue, answer)) for (d, n), clue, answer in xd.clues) == {
        'A1': ('First across', 'ABC'),
        'A3': ('Second across', 'FGH'),
        'D1': ('First down', 'ADF'),
        'D2': ('Second down', 'CEH'),
    }


def test_from_ipuz_dict_clues():
    """Newer ipuz libraries hand back {'number': n, 'clue': text} dicts."""
    ipuz_dict = json.loads(json.dumps(IPUZ_PAIR_CLUES))
    ipuz_dict['clues'] = {
        "Across": [{"number": 1, "clue": "First across"},
                   {"number": 3, "clue": "Second across"}],
        "Down": [{"number": 1, "clue": "First down"},
                 {"number": 2, "clue": "Second down"}],
    }
    puzzle = from_ipuz(ipuz_dict)
    assert dict(puzzle.clues.across) == {1: 'First across', 3: 'Second across'}
    assert dict(puzzle.clues.down) == {1: 'First down', 2: 'Second down'}
