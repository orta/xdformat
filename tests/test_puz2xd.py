"""End-to-end .puz conversion, using a puzzle synthesized with puzpy
(no copyrighted .puz binaries shipped)."""

import puz

from xdformat.puz2xd import parse_puz
from xdformat.xdfile import xdfile as XDFile


def make_puz_bytes():
    p = puz.Puzzle()
    p.width = 3
    p.height = 3
    p.solution = 'ABCD.EFGH'
    p.fill = '----.----'
    p.title = 'Test Puzzle'
    p.author = 'Test Author'
    p.copyright = '(c) 2024'
    # puz clue order: interleaved across/down by cell number
    p.clues = ['First across', 'First down', 'Second down', 'Second across']
    return p.tobytes()


def test_parse_puz():
    xd = parse_puz(make_puz_bytes(), 'test2024-01-01.puz')
    assert xd.get_header('Title') == 'Test Puzzle'
    assert xd.get_header('Author') == 'Test Author'
    assert xd.grid == ['ABC', 'D#E', 'FGH']
    assert dict((d + str(n), (clue, answer)) for (d, n), clue, answer in xd.clues) == {
        'A1': ('First across', 'ABC'),
        'A3': ('Second across', 'FGH'),
        'D1': ('First down', 'ADF'),
        'D2': ('Second down', 'CEH'),
    }


def test_puz_output_reparses():
    xd = parse_puz(make_puz_bytes(), 'test2024-01-01.puz')
    out = xd.to_unicode()
    xd2 = XDFile(out, filename='test2024-01-01.xd')
    assert xd2.grid == xd.grid
    assert xd2.to_unicode() == out
