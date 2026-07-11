# .xd futureproof crossword format 4.0-draft

.xd is a corpus-oriented format, modeled after the simplicity and intuitiveness of the markdown format.  It supports 99.99% of published crosswords, and is intended to be convenient for bulk analysis of crosswords by both humans and machines, from the present and into the future.

## Tools

  * The [`xdformat`](../README.md) Python package in this repo has the reference parser and serializer, and converters from Across-Lite .puz (`puz2xd`) and .ipuz (`ipuz2xd`).

  * The full download/convert/analyze pipeline, including converters for other publisher-specific formats and the `xdlint.py` validator, lives at [century-arcade/xd](https://github.com/century-arcade/xd).

## Full Example

This is the oldest rebus crossword from the New York Times (found by `grep -r Rebus crosswords/nytimes | sort`), available thanks to the huge effort of the [Pre-Shortzian Puzzle Project](http://www.preshortzianpuzzleproject.com/):

    Title: New York Times, Saturday, January 1, 1955
    Author: Anthony Morse
    Editor: Margaret Farrar
    Rebus: 1=HEART 2=DIAMOND 3=SPADE 4=CLUB
    Date: 1955-01-01


    1ACHE#ADAM#2LIL
    BLUER#GULL#MATA
    EATIN#APEX#ICER
    ATAR#TILE#SNEAK
    TEN#MANI#ITE###
    ##DRUB#CANASTAS
    FADED#BAGGY#OIL
    ONES#KATES#TUNA
    ETA#JOKER#JORUM
    SILLABUB#SOON##
    ###ACE#RUIN#ARK
    3WORK#JINX#4MAN
    BIRD#WADS#SCENE
    ISLE#EDGE#PANEL
    DEER#BEET#ARTEL


    A1. Sadness. ~ HEARTACHE
    A6. Progenitor. ~ ADAM
    A10. Mae West stand-by. ~ DIAMONDLIL
    [...]

    D1. Vital throb. ~ HEARTBEAT
    D2. Having wings. ~ ALATE
    D3. Start the card game. ~ CUTANDDEAL
    [...]

## Format specification

The .xd format is a simple UTF-8 text file, and can often be 7-bit ASCII clean.

The file is specified in one of two methods:

- Using an implicit order, with sections being delineated by two or more blank 
  lines (3 consecutive newlines (0x0A)).

- Using `## [Section Name]` to declare the lines after as a certain section. 
  Sections with case-insensitive headers which are not `"metadata"`, `"grid"`, 
  `"clues"` or `"design"` are ignored.  Order is unimportant.

  <details>
    <summary>An example of the previous full example using the explicit headers.</summary>

      ## Metadata

      Title: New York Times, Saturday, January 1, 1955
      Author: Anthony Morse
      Editor: Margaret Farrar
      Rebus: 1=HEART 2=DIAMOND 3=SPADE 4=CLUB
      Date: 1955-01-01

      ## Grid

      1ACHE#ADAM#2LIL
      BLUER#GULL#MATA
      EATIN#APEX#ICER
      ATAR#TILE#SNEAK
      TEN#MANI#ITE###
      ##DRUB#CANASTAS
      FADED#BAGGY#OIL
      ONES#KATES#TUNA
      ETA#JOKER#JORUM
      SILLABUB#SOON##
      ###ACE#RUIN#ARK
      3WORK#JINX#4MAN
      BIRD#WADS#SCENE
      ISLE#EDGE#PANEL
      DEER#BEET#ARTEL

      ## Clues

      A1. Sadness. ~ HEARTACHE
      A6. Progenitor. ~ ADAM
      A10. Mae West stand-by. ~ DIAMONDLIL
      [...]

      D1. Vital throb. ~ HEARTBEAT
      D2. Having wings. ~ ALATE
      D3. Start the card game. ~ CUTANDDEAL
      [...]

  </details>


### Metadata (Section 1)

The first section is a set of key:value pairs, one per line.  Title, Author,
Editor, Copyright, and Date are the standard headers in the meta section.  Other 
headers describing the puzzle semantics are given below.  Additional headers are 
allowed but will be ignored.  Multiple entries with the same key are not allowed.

Header keys are case-insensitive: `Title:`, `title:`, and `TITLE:` are
equivalent.

### Grid (Section 2)

Optional leading whitespace and trailing whitespace on each line.  Never any
whitespace between characters in a grid line.

One line per row.  One Unicode codepoint per cell.  Cell contents of more
than one codepoint -- including multi-codepoint graphemes, such as emoji with
modifiers -- are represented as rebuses.

Uppercase A-Z refer to that letter in the solution; a '#' is a block.  In a few
puzzles, '\_' means a space or non-existing block (usually on the edges), and '.' would
be used for an empty cell (e.g. a partial solution).  [The choice of block and
empty-cell characters is under discussion; see [#1](https://github.com/century-arcade/xdformat/issues/1).]

Digits, most symbols, and printable unicode characters (if needed) can be used
to indicate rebus cells.  The 'Rebus' header provides the translation:

    Rebus: 1=ONE 2=TWO 3=THREE

The same key may be assigned more than one value; such a cell accepts any one
of its values (a Schrödinger cell):

    Rebus: 1=O 1=A

### Design (optional section)

A `## Design` section describes per-cell visual attributes: circles, shading,
and bars.  [It replaces the v3 'Special' header, which designated lowercase
a-z grid cells as "shaded" or "circle"; parsers may still encounter the v3
form in older files.]

The section starts with one or more style definitions, each assigning
CSS-like properties to a single lowercase letter, followed by a design grid
of the same dimensions as the puzzle grid, marking each styled cell with its
style letter and each unstyled cell with '.':

    O { background: circle }
    S { background: shaded }

    ...O...
    ..OSO..
    ...O...

No delimiter is needed between the definitions and the design grid: a
definition line always contains whitespace, and a design-grid line never does.

Defined properties:

  * `background: circle` -- a circle in the cell
  * `background: shaded` -- the cell is shaded; the renderer chooses the color
  * `bar-top: true` -- a bar on the top edge of the cell (barred grids)
  * `bar-left: true` -- a bar on the left edge of the cell

[Explicit colors and light/dark variants are under discussion; see [#5](https://github.com/century-arcade/xdformat/issues/5).]

### Clues (Section 3)

A leading uppercase letter indicates the group the clue is in. 'A' or 'D'
indicate Across or Down; the full heading for other letters would be specified
in the 'Cluegroup' header.  For uniclues, the cluegroup letter is omitted.

The clues should be sorted, with a single newline separating clue groups (Across and Down).

Minimal markup is available.  An example clue line:

    A51. {/Italic/}, {*bold*}, {_underscore_}, or {-strike-thru-} ~ MARKUP

Additional markup spans: `{~subscript~}`, `{^superscript^}`, and
`{=small caps=}`.

Markup spans nest:

    A15. Captain in {/{*Moby-Dick*}/} ~ AHAB

Markup is available only in clue text.  Headers and notes are plain text;
markup syntax appearing in them is not interpreted.  [The markup represents
the rendered form, as it appeared in the original medium.]

The backslash ('\\') is the escape character: `\{` and `\}` give literal
braces, and `\\` gives a literal backslash.  A backslash before any other
character is reserved.  [v3 used a bare backslash as a line separator within
a clue; the v4 syntax for line breaks is under discussion; see [#3](https://github.com/century-arcade/xdformat/issues/3).]

The clue is followed by a list of one or more full answers, all separated by
a tilde with spaces on both sides (' ~ ').  Each answer is given with any
rebuses expanded; rebus keys never appear in answers.  [This makes
clue/answer lines independently useful.]  Most clues have exactly one answer.
A clue whose slot has multiple valid fills (a Schrödinger slot) lists each of
them:

    Rebus: 1=O 1=A


    C1NE


    A1. Sugar ___ ~ CONE ~ CANE

If you need to attach metadata to a clue, on a new line after the clue replace the ". "
with a " ^" - the key for the metadata is determined as being inbetween the hat and 
colon:

    A1. Gardener's concerns with A2 and D4. ~ BULB
    A1 ^Refs: A2 D4

Editorial comments are attached the same way (e.g. `A1 ^Comment: ...`); .xd
has no other comment syntax.

### Notes (Section 4)

The free-format final section can contain any amount of notes.

## CHANGELOG

### 4.0-draft

Decisions from the 2026-07-10 spec discussion with Puzzmo and Ingrid; details
still open are tracked in [issues](https://github.com/century-arcade/xdformat/issues).

- A grid cell holds exactly one Unicode codepoint; larger graphemes are rebuses.
- Header keys are case-insensitive.
- A rebus key may be assigned multiple values, declaring a Schrödinger cell.
- The `## Design` section (adopted from Puzzmo's extension, without its
  `<style>` wrapper) replaces the 'Special' header and lowercase special cells.
- A clue line holds a ' ~ '-separated list of answers, usually of size one;
  a Schrödinger slot lists all valid fills.  Answers always spell out rebus
  expansions.
- Markup adds subscript, superscript, and small caps, and formally nests.
- Backslash is the markup escape character, no longer a line separator.

### 3.0

Includes syntax support for arbitrary clue metadata.

### 2.0

The 2.0 version of the specification adds support for `## [headers]` for sections of xd content. You can read more in [format specification](#format-specification) above.
