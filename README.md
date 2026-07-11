# xdformat

.xd is a plain-text format for crossword puzzles, modeled after the simplicity of markdown.  A complete puzzle -- metadata, grid, clues, answers, notes -- is one small UTF-8 file that can be read, edited, diffed, and grepped like any other text file:

    Title: New York Times, Saturday, January 1, 1955
    Author: Anthony Morse
    Editor: Margaret Farrar
    Rebus: 1=HEART 2=DIAMOND 3=SPADE 4=CLUB
    Date: 1955-01-01


    1ACHE#ADAM#2LIL
    BLUER#GULL#MATA
    EATIN#APEX#ICER
    [...]


    A1. Sadness. ~ HEARTACHE
    A6. Progenitor. ~ ADAM
    A10. Mae West stand-by. ~ DIAMONDLIL
    [...]

    D1. Vital throb. ~ HEARTBEAT
    D2. Having wings. ~ ALATE
    [...]

The format supports 99.99% of published crosswords and is intended to be convenient for bulk analysis by both humans and machines, from the present and into the future.

This repo holds the format specification and the reference tools for parsing .xd and converting other puzzle formats into it.

## The spec

- [doc/xd-format.md](doc/xd-format.md) -- the format specification (v3.0)
- [doc/rebus-conventions.md](doc/rebus-conventions.md) -- rebus/quantum/Schrödinger conventions observed in the corpus (extensions to the spec, not yet formalized)
- [doc/character-encoding.md](doc/character-encoding.md) -- character-encoding oddities inherited from source formats, and how the converters clean them up

## The xdformat Python package

The core package parses and emits .xd with no dependencies:

    pip install xdformat

```python
import xdformat

xd = xdformat.parse("nyt1955-01-01.xd")
xd.get_header("Title")        # "New York Times, Saturday, January 1, 1955"
xd.grid                       # list of row strings
for pos, clue, answer in xd.iterclues():
    ...
print(xd.to_unicode())        # canonical .xd text
```

The converters need the `[convert]` extra (pulls in [puzpy](https://github.com/alexdej/puzpy) and [ipuz](https://pypi.org/project/ipuz/)):

    pip install xdformat[convert]

    puz2xd foo.puz > foo.xd
    puz2xd -o xd/ *.puz
    ipuz2xd bar.ipuz > bar.xd

`xdformat/crossword/` is a vendored fork of Simeon Visser's [crossword](https://github.com/svisser/crossword) library, updated for changes in the ipuz module.

## Related repos

- [century-arcade/xd](https://github.com/century-arcade/xd) -- the corpus pipeline: downloads puzzles from many sources, converts them (using additional publisher-specific converters), analyzes grids and clues, validates with `xdlint.py`, and builds the website at [xd.saul.pw](https://xd.saul.pw)
- gxd -- the corpus itself, 95k+ puzzles in .xd format (private; join [#crosswords on the Discord](https://saul.pw/chat) to discuss getting access)
- [century-arcade/xdcontrib](https://github.com/century-arcade/xdcontrib) -- deprecated; its minimal converters were merged into this repo

## Citing xd

If you publish any research or results using the xd crossword corpus, please cite xd accordingly:

    Pwanson, Saul. (2019). "xd Crossword Corpus." Retrieved from http://xd.saul.pw

The year of publication should be the year that the corpus was accessed.

## License

MIT; see [LICENSE](LICENSE).
