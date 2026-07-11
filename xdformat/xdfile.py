"""Core model, parser, and serializer for the .xd crossword format.

See doc/xd-format.md for the format specification.
"""

import re
import string

from .utils import parse_pathname, parse_pubid, warn


class Error(Exception):
    pass


class IncompletePuzzleParse(Error):
    """Error while parsing source puzzle"""
    def __init__(self, xd, msg=""):
        Error.__init__(self, msg)
        self.xd = xd


class PuzzleParseError(Error):
    pass


REBUS_SEP = " "


UNKNOWN_CHAR = '.'
BLOCK_CHAR = '#'
OPEN_CHAR = '_'
ASIAN_BLOCK_CHAR = '■'  # U+25A0
ASIAN_OPEN_CHAR = '＿'  # U+FF3F
NON_ANSWER_CHARS = [BLOCK_CHAR, OPEN_CHAR, ASIAN_BLOCK_CHAR, ASIAN_OPEN_CHAR]  # UNKNOWN_CHAR is a wildcard answer character
EOL = '\n'
SECTION_SEP = EOL + EOL
HEADER_ORDER = ['title', 'author', 'editor', 'copyright', 'number', 'date',
                'relation', 'special', 'rebus', 'cluegroup', 'description', 'notes']


def parse(fn):
    return xdfile(open(fn).read(), filename=fn)


class xdfile:
    def __init__(self, xd_contents=None, filename=None, pubid=None):
        self.filename = filename
        self.headers = {}  # [key] -> value or list of values
        self.grid = []  # list of string rows
        self.clues = []  # list of (("A", 21), "{*Bold*}, {/italic/}, {_underscore_}, or {-overstrike-}", "MARKUP")
        self.notes = ""

        if filename:
            self._publication_id = pubid or parse_pubid(filename)
        else:
            self._publication_id = pubid

        if xd_contents:
            self.parse_xd(xd_contents)

    def __str__(self):
        return self.filename or "<unknown xd puzzle>"

    def width(self):
        return self.grid and len(self.grid[0]) or 0

    def height(self):
        return len(self.grid)

    # returns (w, h)
    def size(self):
        return (self.width(), self.height())

    def sizestr(self):
        return "%dx%d%s%s" % (self.width(), self.height(), self.get_header("Rebus") and "R" or "", self.get_header("Special") and "S" or "")

    def xdid(self):
        if not self._publication_id:
            raise Error("No Publication Id in '%s'" % self.filename)

        num = self.get_header("Number")
        if num:
            return '%s-%03d' % (self._publication_id, int(num))

        assert self.date()
        return '%s%s' % (self._publication_id, self.date())

    def date(self):
        dt = self.get_header("Date")
        if not dt and self.filename and self._publication_id:
            dt = parse_pathname(self.filename).base[len(self._publication_id):]
        return dt

    def year(self):
        return self.date().split('-')[0]

    def publication_id(self):  # "nyt"
        return self._publication_id

    def iterdiffs(self, other):
        for k in set(self.headers.keys()) | set(other.headers.keys()):
            if self.get_header(k) != other.get_header(k):
                yield self.get_header(k), other.get_header(k)

        for a, b in zip(self.grid, other.grid):
            if a != b:
                yield a, b

        for a, b in zip(self.clues, other.clues):
            if a != b:
                yield a, b

    def diffs(self, other):
        return [(a, b) for a, b in self.iterdiffs(other)]

    def get_header(self, fieldname):
        v = self.headers.get(fieldname)
        assert v is None or isinstance(v, str), v
        return (v or "").strip()

    def set_header(self, fieldname, newvalue=None):
        if newvalue:
            newvalue = str(newvalue).strip()
            newvalue = " ".join(newvalue.splitlines())
            newvalue = newvalue.replace("\t", "  ")

            self.headers[fieldname] = newvalue
        else:
            if fieldname in self.headers:
                del self.headers[fieldname]

    def add_header(self, fieldname, value):
        if fieldname in self.headers:
            assert isinstance(self.headers[fieldname], list)
            self.headers[fieldname].append(value)
        else:
            self.headers[fieldname] = [value]

    def get_clue_for_answer(self, target):
        clues = []
        for pos, clue, answer in self.clues:
            if answer == target:
                clues.append(clue)

        if not clues:
            return None
        if clues and len(clues) > 1:
            warn("multiple clues for %s: %s" % (target, " | ".join(clues)))
        return clues[0]

    def get_clue(self, clueid):
        for pos, clue, answer in self.clues:
            posdir, n = pos
            if clueid == posdir + str(n):
                return clue

    def append_clue_break(self):
        self.clues.append((("", ""), "", ""))

    def cell(self, r, c):
        if r < 0 or c < 0 or r >= len(self.grid) or c >= len(self.grid[0]):
            return BLOCK_CHAR
        return self.grid[r][c]

    def is_redacted(self):
        # True when the puzzle's letter cells are all 'X' — typically a contest
        # puzzle published before answers were released. Useful for excluding
        # from grid/answer/clue analysis while still counting it in metadata.
        letters = ''.join(c for row in self.grid for c in row if c not in '#_.')
        return bool(letters) and all(c == 'X' for c in letters)

    def rebus(self):
        """returns rebus dict of only special (non A-Z) characters"""
        rebusstr = self.get_header("Rebus")
        r = {}
        if rebusstr:
            # comma-form separator: legacy but present in the corpus (xdlint XD109)
            for p in re.split(r'[ ,]', rebusstr):
                if not p:
                    continue
                cellchar, _, replstr = p.partition("=")
                assert len(cellchar) == 1, (rebusstr, cellchar)
                replstr = replstr.strip()
                r[cellchar] = replstr

        return r

    def iterclues(self):
        for pos, clue, answer in self.clues:
            if pos:  # skip cluegroup breaks
                yield "%s%s" % pos, clue, answer

    def numberedPuzzle(self):
        puzzle = []
        for r in range(self.height()):
            puzzle.append(['#' if c == '#' else None for c in self.grid[r]])

        for _, clue_num, _, r, c in self.iteranswers_full():
            puzzle[r][c] = clue_num

        return puzzle

    # generates: "A" or "D", clue_num, answer, r, c
    def iteranswers_full(self):

        # construct rebus dict with all grid possibilities so that answers are complete
        rebus = {}
        for c in string.ascii_letters:
            assert c not in rebus, c
            rebus[c] = c.upper()
        rebus.update(self.rebus())

        # traverse grid and yield (dir, pos, answer)
        clue_num = 1

        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                # compute number shown in box
                new_clue = False
                if self.cell(r, c - 1) in NON_ANSWER_CHARS:  # across clue start
                    ncells = 0
                    answer = ""
                    while self.cell(r, c + ncells) not in NON_ANSWER_CHARS:
                        cellval = self.cell(r, c + ncells)
                        answer += rebus.get(cellval, cellval)
                        ncells += 1

                    if ncells > 1:
                        new_clue = True
                        yield "A", clue_num, answer, r, c

                if self.cell(r - 1, c) in NON_ANSWER_CHARS:  # down clue start
                    ncells = 0
                    answer = ""
                    while self.cell(r + ncells, c) not in NON_ANSWER_CHARS:
                        cellval = self.cell(r + ncells, c)
                        answer += rebus.get(cellval, cellval)
                        ncells += 1

                    if ncells > 1:
                        new_clue = True
                        yield "D", clue_num, answer, r, c

                if new_clue:
                    clue_num += 1

    def iteranswers(self):
        for direction, clue_num, answer, r, c in self.iteranswers_full():
            yield direction, clue_num, answer

    def get_answer(self, clueid):
        for pos, clue, answer in self.clues:
            posdir, n = pos
            if clueid == posdir + str(n):
                return answer

    def parse_xd(self, xd_contents):
        # placeholders, actual numbering starts at 1
        section = 0
        subsection = 0

        # fake blank line at top to allow leading actual blank lines before headers
        nblanklines = 2

        for line in xd_contents.splitlines():
            # leading whitespace is decorative
            line = line.strip()

            # collapse consecutive lines of whitespace into one line and start next group
            if not line:
                nblanklines += 1
                continue
            else:
                if nblanklines >= 2:
                    section += 1
                    subsection = 1
                    nblanklines = 0
                elif nblanklines == 1:
                    subsection += 1
                    nblanklines = 0

            if section == 1:
                # headers first
                if ":" in line:
                    k, v = line.split(":", 1)
                    k, v = k.strip(), v.strip()

                    if k in self.headers:
                        if isinstance(self.headers[k], str):
                            self.headers[k] = [self.headers[k], v]
                        else:
                            self.headers[k].append(v)
                    else:
                        self.set_header(k, v)
                else:
                    self.notes += line + "\n"

            elif section == 2:
                assert self.headers, "no headers"
                # grid second
                self.grid.append(line)
            elif section == 3:
                # across or down clues
                answer_idx = line.rfind("~")
                if answer_idx > 0:
                    clue = line[:answer_idx]
                    answer = line[answer_idx + 1:]
                else:
                    clue, answer = line, ""

                clue_idx = clue.find(".")

                assert clue_idx > 0, "no clue number: " + clue
                pos = clue[:clue_idx].strip()
                clue = clue[clue_idx + 1:]

                try:
                    cluedir = pos[0]
                    cluenum = int(pos[1:])
                except Exception:
                    cluedir = ""
                    cluenum = pos  # fallback to strings for non-numeric clue "numbers"
                self.clues.append(((cluedir, cluenum), clue.strip(), answer.strip()))
            else:  # anything remaining
                if line:
                    self.notes += line + EOL

    def iterheaders(self):
        def header_sort_key(item):
            if item[0].lower() not in HEADER_ORDER:
                return 1000

            return HEADER_ORDER.index(item[0].lower())

        for k, v in sorted(list(self.headers.items()), key=header_sort_key):
            yield k, v

    def to_unicode(self, emit_clues=True):
        # headers (section 1)

        r = ""

        if self.headers:
            for k, v in self.iterheaders():
                assert isinstance(v, str), v

                r += "%s: %s" % (k, v)
                r += EOL
        else:
            r += "Title: %s" % parse_pathname(self.filename).base
            r += EOL

        r += SECTION_SEP

        # grid (section 2)
        r += EOL.join(self.grid)
        r += EOL + EOL + EOL

        # clues (section 3)
        if emit_clues:
            prevdir = None
            for pos, clue, answer in self.clues:
                if not answer:
                    r += EOL
                    continue

                cluedir, cluenum = pos
                if prevdir and prevdir != cluedir:  # Blank line between cluedirs
                    r += EOL
                prevdir = cluedir

                cluetext = (clue or "[XXX]").strip()
                cluetext = " ".join(cluetext.splitlines())
                r += "%s%s. %s ~ %s" % (cluedir, cluenum, cluetext, answer)
                r += EOL

            if self.notes:
                r += EOL + EOL
                r += self.notes

        r += EOL

        # some Postscript CE encodings can be caught here
        r = r.replace('\x91', "'")
        r = r.replace('\x92', "'")
        r = r.replace('\x93', '"')
        r = r.replace('\x94', '"')
        r = r.replace('\x96', '___')
        r = r.replace('\x85', '...')

        # these are always supposed to be double-quotes
        r = r.replace("''", '"')

        return r

    def transpose(self):
        def get_col(g, n):
            return "".join([r[n] for r in g])

        flipxd = xdfile()
        flipxd.filename = (self.filename or "unknown") + ".transposed"
        flipxd.headers = self.headers.copy()

        g = []
        for i in range(len(self.grid[0])):
            g.append(get_col(self.grid, i))

        flipxd.grid = g

        for posdir, posnum, answer in flipxd.iteranswers():
            clue = self.get_clue_for_answer(answer)
            if clue is None:  # '' might be the actual clue
                clue = '[XXX]'
            flipxd.clues.append(((posdir, posnum), clue, answer))

        flipxd.clues = sorted(flipxd.clues)
        return flipxd
