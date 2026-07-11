#!/usr/bin/env python3
"""Convert Across Lite .puz files to .xd.  Requires puzpy (pip install xdformat[convert])."""

import string
import sys

import puz

from . import crossword
from .xdfile import (
    xdfile, PuzzleParseError, IncompletePuzzleParse,
    REBUS_SEP, BLOCK_CHAR, OPEN_CHAR, UNKNOWN_CHAR,
)
from .encoding import decode
from .utils import warn


def parse_puz(contents, filename):
    rebus_shorthands = list("zyxwvutsrqponmlkjihgfedcba⚷⚳♇♆⛢♄♃♂♁♀☿♹♸♷♶♵♴♳⅘⅗⅖⅕♚♛♜♝♞♟⚅⚄⚃⚂⚁⚀♣♦♥♠+&%$@?*0987654321")

    try:
        puzobj = puz.load(contents)
        puzzle = crossword.from_puz(puzobj)
    except puz.PuzzleFormatError as e:
        emsg = e.message
        if "<html>" in contents.decode('utf-8').lower():
            emsg += " (looks like html)"
        raise PuzzleParseError(emsg)

    grid_dict = dict(list(zip(string.ascii_uppercase, string.ascii_uppercase)))

    xd = xdfile('', filename)

    xd.set_header("Author", decode(puzobj.author))
    xd.set_header("Copyright", decode(puzobj.copyright))
    xd.set_header("Notes", decode(puzobj.notes))

    xd.set_header("Title", decode(puzobj.title))

    used_rebuses = {}  # [puz_rebus_gridvalue_as_string] -> our_rebus_gridvalue
    rebus = {}  # [our_rebus_gridvalue] -> full_cell
    r = puzobj.rebus()
    if r.has_rebus():
        grbs = puzobj.extensions[b"GRBS"]
        if sum(x for x in grbs if x != 0) > 0:   # check for an actual rebus
            for pair in puzobj.extensions[b"RTBL"].decode("cp1252").split(";"):
                pair = pair.strip()
                if not pair:
                    continue
                key, value = pair.split(":")
                rebuskey = rebus_shorthands.pop()
                used_rebuses[key] = rebuskey
                rebus[rebuskey] = decode(value)

            rebustr = REBUS_SEP.join([("%s=%s" % (k, v)) for k, v in sorted(rebus.items())])
            xd.set_header("Rebus", rebustr)

    # check for circles and record them if they exist
    circles = []
    if b"GEXT" in puzobj.extensions:
        for i, c in enumerate(puzobj.extensions[b"GEXT"]):
            if c == 0x80:
                circles.append(i)
    if circles:
        xd.set_header("Special", "circle")

    for r, row in enumerate(puzzle):
        rowstr = ""
        for c, cell in enumerate(row):
            if puzzle.block is None and cell.solution == '.':
                rowstr += BLOCK_CHAR
            elif cell.solution == puzzle.block:
                rowstr += BLOCK_CHAR
            elif cell.solution == ':':
                rowstr += OPEN_CHAR
            elif cell == puzzle.empty:
                rowstr += UNKNOWN_CHAR
            else:
                n = r * puzobj.width + c
                reb = puzobj.rebus()
                if reb.has_rebus() and n in reb.get_rebus_squares():
                    ch = str(reb.table[n] - 1)
                    rowstr += used_rebuses[ch]
                    cell.solution = rebus[used_rebuses[ch]]
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
                    rowstr += grid_dict[ch].lower() if n in circles else grid_dict[ch]
                    # ^ assumes a cell is never rebus and circle.

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
    return convert_main(parse_puz, 'convert Across Lite .puz files to .xd', mode='rb', argv=argv)


if __name__ == "__main__":
    sys.exit(main())
