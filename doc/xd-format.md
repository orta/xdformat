# .xd futureproof crossword format 4.0-draft

.xd is a corpus-oriented format, modeled after the simplicity and intuitiveness of the markdown format.  It supports 99.99% of published crosswords, and is intended to be convenient for bulk analysis of crosswords by both humans and machines, from the present and into the future.

## Tools

* The [`xdformat`](../README.md) Python package in this repo has the reference parser and serializer, and converters from Across-Lite .puz (`puz2xd`) and .ipuz (`ipuz2xd`).

* The full download/convert/analyze pipeline, including converters for other publisher-specific formats and the `xdlint.py` validator, lives at [century-arcade/xd](https://github.com/century-arcade/xd).

## Full Example

This is the oldest rebus crossword from the New York Times (found by `grep -r Rebus crosswords/nytimes | sort`), available thanks to the huge effort of the [Pre-Shortzian Puzzle Project](http://www.preshortzianpuzzleproject.com/):

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

## Format specification

The .xd format is a simple UTF-8 text file, and can often be 7-bit ASCII clean.

The file is specified using `## [Section Name]` to declare the lines after as a certain section.
Sections with case-insensitive headers which are not `"metadata"`, `"grid"`,  `"clues"` or
`"design"` are ignored. Order is unimportant.

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

### Metadata

The first section is a set of key:value pairs, one per line.  Title, Author,
Editor, Copyright, and Date are the standard headers in the meta section.  Other
headers describing the puzzle semantics are given below.  Additional headers are
allowed but will be ignored.  Multiple entries with the same key are not allowed.

Header keys are case-insensitive: `Title:`, `title:`, and `TITLE:` are
equivalent.

Header values may carry inline markup for italics, links, images and more; the
syntax is given in [xdown Formatting](#xdown-formatting) below.

### Grid

Optional leading whitespace and trailing whitespace on each line.  Never any
whitespace between characters in a grid line.

One line per row.  One Unicode codepoint per cell.  Cell contents of more
than one codepoint -- including multi-codepoint graphemes, such as emoji with
modifiers -- are represented as rebuses.

For the grid:

* Uppercase A-Z refer to that letter in the solution
* Either '#' or '.' is a block
* '\_' means a spacer or non-existing block (usually on the edges)
* Any other character is assumed to be a rebus lookup

Digits, most symbols, and printable unicode characters (if needed) can be used
to indicate rebus cells.  The 'Rebus' header provides the translation:

    Rebus: 1=ONE 2=TWO 3=THREE

The same key may be assigned more than one value; such a cell accepts any one
of its values (a Schrödinger cell):

    Rebus: 1=O 1=A

### Clues

A leading uppercase letter indicates the group the clue is in. 'A' or 'D'
indicate Across or Down; the full heading for other letters would be specified
in the 'Cluegroup' header.  For uniclues, the cluegroup letter is omitted.

The clues should be sorted, with a single newline separating clue groups (Across and Down).

#### Clue Bodies

The format is:

    A1. Big name in bricks? ~ LEGO
    ^^  ^^^^^^^^^^^^^^^^^^^   ^^^^
    |   |                     answer
    |   clue body
    clue reference

The reference runs to the first '.' on the line, and the clue body from
there to the first ' ~ '.  After each ' ~ ' the answer is the first word;
anything else in that segment is ignored:

    A6. Book look-up. ~ INDEX (5 letters)

is the clue 'Book look-up.' with the single answer ADAM.  Trailing text has
no defined meaning in .xd and should be ignored.

A clue body may carry inline markup for italics, links, images and more; the
syntax is given in [xdown Formatting](#xdown-formatting) below.

The clue is followed by a list of one or more full answers, all separated by
a tilde with spaces on both sides (' ~ ').  Each answer is given with any
rebuses expanded; rebus keys never appear in answers.  [This makes
clue/answer lines independently useful.]  Most clues have exactly one answer.

A clue whose slot has multiple valid fills (a Schrödinger slot) lists each of
them:

    Rebus: 1=O 1=A
  

    C1NE


    A1. Sugar ___ ~ CONE ~ CANE

#### Clue Metdata

If you need to attach metadata to a clue, on a new line after the clue replace the ". "
with a " ^" - the key for the metadata is determined as being in-between the hat and
colon:

    A1. Gardener's concerns with A2 and D4. ~ BULB
    A1 ^Refs: A2 D4

The xd spec does not reserve any keys.

### Design (optional section)

A `## Design` section describes per-cell visual attributes: circles, shading,
bars, and images.  [It replaces the v3 'Special' header, which designated
lowercase a-z grid cells as "shaded" or "circle"; parsers may still encounter
the v3 form in older files.]

The section starts with one or more style definitions, each assigning
CSS-like properties to a single character, followed by a design grid
of the same dimensions as the puzzle grid, marking each styled cell with its
style character and each unstyled cell with '.':

    O { background: circle }
    S { background: shaded }

    ...O...
    ..OSO..
    ...O...

No delimiter is needed between the definitions and the design grid: a
definition line always contains whitespace, and a design-grid line never does.

Style characters are case-sensitive: a design may use both 'A'-'Z' and
'a'-'z'.  [An illustrated puzzle can need more than 26 distinct styles.]

Defined properties:

* `background: circle` -- a circle in the cell
* `background: shaded` -- the cell is shaded; the renderer chooses the color
* `background-image: url('...')` -- an image drawn in the cell
* `background-size: N M` -- the image spans N cells to the right and M cells
  downward; defaults to `1 1`
* `bar-top: true` -- a bar on the top edge of the cell (barred grids)
* `bar-left: true` -- a bar on the left edge of the cell

An image is given as a CSS `url()` with a quoted argument.  The url is either
a data URI, which keeps the image in the file, or a reference to an image
elsewhere:

    A { background-image: url('data:image/png;base64,iVBORw0KGgo=') }
    B { background-image: url('https://example.com/petal.png') }

    ..A..
    ..B..

The quotes are required.  A quoted value is taken literally, so the ':', ';'
and ',' inside either form of url are not read as delimiters.

Prefer a data URI.  An .xd file aims to be a single self-contained document,
and an external image makes the puzzle depend on a host that may not answer
for as long as the file exists.

An image covering more than one cell is marked at its top-left cell only,
with 'background-size' giving its size in cells, width first.  The cells it
covers are left unstyled:

    B { background-image: url('data:image/png;base64,iVBORw0KGgo='); background-size: 2 2 }

    B....
    .....

[The two counts are in cells, not the lengths or percentages CSS allows.  A
crossword is drawn on a grid and a renderer sizes the cells, so an image's
size is only meaningful as a count of them.]

A cell may carry an image and a background together; the image is drawn over
the background.

The CSS-like parser should be able to handle:

* Whitespace around a selector, key or value being trimmed -- but whitespace
  *within* a value is kept, which is what separates the two counts in
  `background-size: 2 2`
* Re-opening a character:

    ```css
    A { background: circle }
    A { bar-top: true }
    ```

* Opening many characters at once with a comma: `A,B { background: circle }
* Separating many properties via semi colons: `A { background: circle; bar-top: true }
* Quoted values inside a rule body, within which none of `}`, `:`, `;` or
  `,` delimits
* Rejecting a comma inside a rule body, where it is never a separator:
  `background-size: 2 2`, never `background-size: 2, 2`

[Explicit colors and light/dark variants are under discussion; see [#5](https://github.com/century-arcade/xdformat/issues/5).]

### xdown Formatting

Clue bodies may contain inline markup, known as xdown.  A markup span is an
opening '{', a type character, the content, the same type character again,
and a closing '}'.

Markup is available only in clue bodies.  Headers, answers, and notes are
plain text; markup syntax appearing in them is not interpreted.  [The markup
represents the rendered form, as it appeared in the original medium.]

There are eleven type characters.  A '{' followed by any other character is
literal text, so most clue bodies need no escaping.

Seven of them style their content as text:

* `{/italic/}`
* `{*bold*}`
* `{_underscore_}`
* `{-strike-through-}`
* `{~subscript~}`
* `{^superscript^}`
* `{=small caps=}`

An example clue line:

    A51. {/Italic/}, {*bold*}, {_underscore_}, or {-strike-thru-} ~ MARKUP

Text spans nest, and a renderer applies every enclosing style:

    A15. Captain in {/{*Moby-Dick*}/} ~ AHAB

The remaining three type characters take structured content, with '|'
separating the parts.

A link is `{@` text `|` url `@}`:

    A16. See {@the notes|https://example.com@} ~ AHAB

The parts are separated at the first '|' outside of any nested span, so the
text may itself contain markup:

    A16. See {@{*the notes*}|https://example.com@} ~ AHAB

An image is `{!` `[` url `|` alt `|` width `|` height `]` `!}`.  The square
brackets are part of the syntax, only the url is required, and the url and
alt are literal text:

    A17. Pictured: {![https://example.com/whale.png|A sperm whale]!} ~ AHAB

Doubling the opening '!' makes it a block image, rendered on its own line
rather than inline.  The closing delimiter is unchanged:

    A17. Pictured: {!![https://example.com/whale.png|A sperm whale]!} ~ AHAB

<!-- A color is `{#` text `|` light `|` dark `#}`, giving the color to render the
text in under a light theme and under a dark theme:

    A18. The {#red|#c00000|#ff6666#} planet ~ MARS

All three parts are required.  Unlike a link, a color is separated at every
'|', so its text cannot contain one. -->

You should assume typoes or malformed markup, and it those cases render plaintext.

The backslash ('\\') is the escape character: `\{` and `\}` give literal
braces, and `\\` gives a literal backslash.  Only a '{' before a type
character needs escaping.  A backslash before any other character is
reserved.

A newline is represented as `{\}`

## CHANGELOG

### 4.0-draft

Decisions from the 2026-07-10 spec discussion with Puzzmo and Ingrid; details
still open are tracked in [issues](https://github.com/century-arcade/xdformat/issues).

* [BREAKING] Headers need to be set for sections
* [BREAKING] Dropping using capitals in the grid to indicate special blocks (use `## Design`)
* [BREAKING] `.` can now be used as a block
* A grid cell holds exactly one Unicode codepoint; larger graphemes are rebuses.
* Header keys are case-insensitive.
* Header values can now be xdown formatted
* A rebus key may be assigned multiple values, declaring a Schrödinger cell.
* The `## Design` section (adopted from Puzzmo's extension, without its
  `<style>` wrapper) replaces the 'Special' header and lowercase special cells.
* It is now possible to represent barred-grid Crosswords
* It is possible to represent background images in the grid
* A clue line holds a ' ~ '-separated list of answers, usually of size one;
  a Schrödinger slot lists all valid fills.  Answers always spell out rebus
  expansions.  An answer is a single word; text following it is ignored.
* Markup adds subscript, superscript, and small caps, and formally nests.
* Backslash is the markup escape character, no longer a line separator.
* `{\}` is added as a line separator

### 3.0

Includes syntax support for arbitrary clue metadata.

### 2.0

The 2.0 version of the specification adds support for `## [headers]` for sections of xd content. You can read more in [format specification](#format-specification) above.
