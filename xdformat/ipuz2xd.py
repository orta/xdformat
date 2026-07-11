#!/usr/bin/env python3
"""Convert .ipuz crossword files to .xd.  Requires ipuz (pip install xdformat[convert])."""

import string
import sys

import ipuz

from . import crossword
from .xdfile import (
    xdfile, PuzzleParseError, IncompletePuzzleParse,
    REBUS_SEP, BLOCK_CHAR, OPEN_CHAR, UNKNOWN_CHAR,
)
from .encoding import decode
from .utils import warn, parse_pathname, parse_date_from_filename


def parse_ipuz(contents, filename):
    rebus_shorthands = list("⚷⚳♇♆⛢♄♃♂♁♀☿♹♸♷♶♵♴♳⅘⅗⅖⅕♚♛♜♝♞♟⚅⚄⚃⚂⚁⚀♣♦♥♠+&%$@?*zyxwvutsrqponmlkjihgfedcba0987654321")

    ipuz_dict = ipuz.read(contents.decode("utf-8"))
    puzzle = crossword.from_ipuz(ipuz_dict)

    grid_dict = dict(list(zip(string.ascii_uppercase, string.ascii_uppercase)))

    xd = xdfile('', filename)

    xd.set_header("Author", puzzle.meta.creator)
    xd.set_header("Editor", puzzle.meta.contributor)
    xd.set_header("Copyright", puzzle.meta.rights)
    dt = parse_date_from_filename(parse_pathname(filename).base)
    if dt:
        xd.set_header("Date", dt)
    xd.set_header("Notes", puzzle.meta.description)

    xd.set_header("Title", puzzle.meta.title)

    for r, row in enumerate(puzzle):
        rowstr = ""
        for c, cell in enumerate(row):
            if puzzle.block is None and cell.solution == '#':
                rowstr += BLOCK_CHAR
            elif cell.solution == puzzle.block:
                rowstr += BLOCK_CHAR
            elif cell.solution == ':':
                rowstr += OPEN_CHAR
            elif cell == puzzle.empty:
                rowstr += UNKNOWN_CHAR
            else:
                ch = cell.solution
                if ch not in grid_dict:
                    if ch in rebus_shorthands:
                        cellch = ch
                        rebus_shorthands.remove(ch)
                        warn("%s: unknown grid character '%s', assuming rebus of itself" % (filename, ch))
                    else:
                        cellch = rebus_shorthands.pop()
                        warn("%s: unknown grid character '%s', assuming rebus (as '%s')" % (filename, ch, cellch))
                    xd.set_header("Rebus", xd.get_header("Rebus") + " %s=%s" % (cellch, ch))

                    grid_dict[ch] = cellch
                rowstr += grid_dict[ch]

        xd.grid.append(rowstr)

    assert xd.size() == (puzzle.width, puzzle.height), "non-matching grid sizes"

    # clues
    answers = {}

    for posdir, posnum, answer in xd.iteranswers():
        answers[posdir[0] + str(posnum)] = answer

    try:
        for number, clue in puzzle.clues.across():
            cluenum = "A" + str(number)
            if cluenum not in answers:
                raise IncompletePuzzleParse(xd, "Clue number doesn't match grid: " + cluenum)
            xd.clues.append((("A", number), decode(clue), answers.get(cluenum, "")))

        for number, clue in puzzle.clues.down():
            cluenum = "D" + str(number)
            if cluenum not in answers:
                raise IncompletePuzzleParse(xd, "Clue doesn't match grid: " + cluenum)
            xd.clues.append((("D", number), decode(clue), answers.get(cluenum, "")))
    except KeyError as e:
        raise IncompletePuzzleParse(xd, "Clue doesn't match grid: " + str(e))

    return xd


def main(argv=None):
    from .cli import convert_main
    return convert_main(parse_ipuz, 'convert .ipuz crossword files to .xd', mode='rb', argv=argv)


if __name__ == "__main__":
    sys.exit(main())
