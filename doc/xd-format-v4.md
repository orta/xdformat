# .xd futureproof crossword format 4.0-draft

.xd is a corpus-oriented format, modeled after the simplicity and intuitiveness of the markdown format.  It supports 99.99% of published crosswords, and is intended to be convenient for bulk analysis of crosswords by both humans and machines, from the present and into the future.

## Tools

* The [`xdformat`](../README.md) Python package in this repo has the reference parser and serializer, and converters from Across-Lite .puz (`puz2xd`) and .ipuz (`ipuz2xd`).

* The full download/convert/analyze pipeline, including converters for other publisher-specific formats, lives at [century-arcade/xd](https://github.com/century-arcade/xd). Its validator is on PyPI as [`xdlint`](https://pypi.org/project/xdlint/) (`pip install xdlint`, or `uvx xdlint`).

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

A file is divided into sections.  A section should start with a
`## [Section Name]` heading, which declares the lines after it as that section.
Headings are case-insensitive, and a section whose heading is not `"metadata"`,
`"grid"`, `"clues"` or `"design"` is ignored.  Order is unimportant.

### Implicit sections

Headings are not required.  In a file with no headings at all, sections are
delineated by two or more blank lines (3 consecutive newlines (0x0A)) and are
read in a fixed order: metadata, grid, clues, and then notes for anything
following.  The full example above can be written this way:

    Title: New York Times, Saturday, January 1, 1955
    Author: Anthony Morse
    Editor: Margaret Farrar
    Rebus: 1=HEART 2=DIAMOND 3=SPADE 4=CLUB
    Date: 1955-01-01


    1ACHE#ADAM#2LIL
    BLUER#GULL#MATA
    [...]


    A1. Sadness. ~ HEARTACHE
    A6. Progenitor. ~ ADAM
    [...]

A design section has no place in that order, so a file using one needs
headings.  [Nearly every .xd file written so far is headingless, so this form
stays supported; new files should use headings.]

### Metadata

The metadata section is a set of metadata fields, one per line, each a
`Key: value` pair.  Title, Author, Editor, Copyright, and Date are the standard
metadata fields.  Other fields describing the puzzle semantics are given
below.  Additional fields are allowed but will be ignored.  Multiple fields
with the same key are not allowed.

Field keys are case-insensitive: `Title:`, `title:`, and `TITLE:` are
equivalent.

The value of a metadata field may carry inline markup for italics, links,
images and more; the syntax is given in [xdown Formatting](#xdown-formatting)
below.  The 'Rebus' field is the exception, and is read as plain text.

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
* '?' is an unfilled cell: a cell that takes a letter, but whose solution is
  not known, as in a grid still being constructed, or a puzzle whose solution
  is missing or only partly recovered
* Any other character is a rebus key, declared in the 'Rebus' field

### Rebus

The 'Rebus' field gives each rebus key the strings its cells accept:

    Rebus: 1=ONE 2=TWO 3=THREE

The field's grammar is:

    field   := rule (ws rule)*
    rule    := key "=" text ("|" text)*
             | key key+ "=" linked ("|" linked)+
    linked  := segment*
    segment := char | escape | "(" text ")"
    text    := (char | escape)*
    escape  := "\" ("|" | "," | "(" | ")" | "\")

Here `ws` is one or more spaces or tabs, `key` is one grid character, and
`char` is any codepoint other than a space, a tab, '|', ',', '(', ')' or '\'.
On top of the grammar:

* Every rebus key in the grid is declared, and no key is declared twice,
  whether in two rules or twice in one.  A declared key that isn't in the grid
  is ignored.  A key cannot be '=', '|', ',', '(', ')' or '\', so those can't
  appear in the grid.
* An option of a rule with several keys has one segment per key, or is empty.
* A segment in parentheses doesn't hold exactly one codepoint, so `(S)` is an
  error.  `()` is an empty cell, and an option made only of `()` segments is
  written as the empty option instead.
* No rule lists the same option twice.

[',' separated rules in v3.  It is reserved so that a v3 field such as
`1=OIL,2=WATER` is an error, rather than one rule whose value is
`OIL,2=WATER`.]

#### Options

The first option is the cell's solution, which an app shows when the cell is
revealed.  The others are also accepted:

    Rebus: 1=HEART 2=EIGHT|8

The field doesn't record why a cell has several options.  They may be
different answers, as in a Schrödinger cell, a reading per direction, or ways
of typing one answer, such as EIGHT and 8.  The answers on the clue lines
record that.

An empty option means the cell is correct when left empty.  The cell is still
a white cell, numbered and counted in its entries like any other.  Here cell 1
is always empty, cell 2 is empty or H, and cell 3 is H or empty:

    Rebus: 1= 2=|H 3=H|

Apart from the escapes, every character is literal, including '/' and '=':

    Rebus: 1=/ 2=\| 3=\, 4=\( 5=\\

Cells that share the key of a rule with one key each choose among its options
on their own.  In HEIGHTANDWEIGHT, either EIGHT may be written as 8:

    Rebus: 1=EIGHT|8

    H1ANDW1

#### Schrödinger cells

A Schrödinger cell's options are different answers, and every entry through
the cell is built to work either way:

    Rebus: 1=O|A

    TILE
    APEX
    C1NE
    ODDS

    A6. Sugar ____ ~ CONE ~ CANE
    D2. Apple tech ~ IPOD ~ IPAD

#### Linked cells

A rule with several keys links every cell marked with any of them, wherever
they are in the grid.  Each option has one segment per key, in key order, and
the cells all take their segments from the same option:

    Rebus: 12345=CIGAR|PENIS

This accepts CIGAR or PENIS, and never CEGIR.

In SHORTLINE/CHORTLING, the cells read SC and EG down, and S or C and E or G
across:

    Rebus: 12=(SC)(EG)|SE|CG

A slot that reads TEN or is left empty:

    Rebus: 123=|TEN

Rules are independent of one another.  In `THE[N|S]O[R|U]TH[E|W][A|E]ST`,
either of NORTH or SOUTH can go with either of EAST or WEST:

    Rebus: 12=NR|SU 34=EA|WE

#### Checking a solve

The grid is solved when every A-Z cell holds its letter and every rule is
solved.  A rule with one key is solved when each of its cells holds one of its
options.  A rule with several keys is solved when there is a position p at
which every cell marked with one of its keys holds that key's segment of
option p.  An empty cell holds the empty string.  Strings are compared
codepoint by codepoint, so case matters.  Answers on clue lines are never
used.

A cell may hold the same segment at two positions, so cells 1 and 2 here
accept LAT, LUG and LAG, but not LUT:

    Rebus: 12=AT|UG|AG

    L12

#### Readings that differ by direction

A cell holds one string, which its across and down entries both read.  For a
cell read PH across and F down, the field lists both, and the answers carry
the direction:

    Rebus: 1=PH|F

    AL1A
    CARD
    EGOS

    A1. First in a series ~ ALPHA
    D3. To and ____ ~ FRO

#### Converted puzzles

A source format may list alternates for a cell without saying whether they
are different answers, a reading per direction, or the outlet's shortcuts for
typing a rebus.  A converter that can't tell leaves the cells unlinked, with
the source's solution first, so that the file accepts exactly what the source
accepts:

    Rebus: 1=W/T|T/W|WT|TW|W|T 2=A/R|R/A|AR|RA|A|R 3=R/E|E/R|RE|ER|R|E 4=S/K|K/S|SK|KS|S|K

Linking says something about the puzzle that the source doesn't, so it is left
to an editor who knows the puzzle.  An editor who knows these cells spell
STARWARS or STARTREK gives the four keys to one rule.  They put the two
readings first, so that reveal shows letters, and line up the other typings
position by position:

    Rebus: 1234=WARS|TREK|(W/T)(A/R)(R/E)(S/K)|(T/W)(R/A)(E/R)(K/S)|(WT)(AR)(RE)(SK)|(TW)(RA)(ER)(KS)

Linking narrows what is accepted, so W/T beside AR is now rejected.

### Clues

A leading 'A' or 'D' indicates whether the clue is Across or Down.

For [uniclue](https://www.xwordinfo.com/Uniclue) puzzles, where each number
carries a single clue covering both the Across and the Down entry starting at
that square, the letter is omitted:

    1. Reposition an icon, maybe ~ DRAGANDDROP
    2. Crowd's sound ~ ROAR

The clues should be sorted, with a single newline separating clue groups (Across and then Down).

#### Clue Bodies

The format is:

    A1. Big name in bricks? ~ LEGO
    ^^  ^^^^^^^^^^^^^^^^^^^   ^^^^
    |   |                     answer
    |   clue body
    clue reference

The reference runs to the first '.' on the line, and the clue body from there
to the first ' ~ ', or to the end of the line if it has none.  After each
' ~ ' the answer is the first word, which includes non-ASCII characters and
ends at the first whitespace.  The rest of that segment has no defined meaning
and is ignored:

    A6. Book look-up ~ INDEX (5 letters)

is the clue 'Book look-up' with the single answer INDEX.

A clue body may carry inline markup for italics, links, images and more; the
syntax is given in [xdown Formatting](#xdown-formatting) below.

An answer is what the clue means, written out in full with any rebuses
expanded; rebus keys never appear in answers.  [This makes clue/answer lines
independently useful.]  Most clues have exactly one answer.

A clue whose slot has several fills that answer it (a Schrödinger slot) lists
each of them, with the one the cells' solutions spell first.  Other typings
of the same answer, such as 8 for EIGHT, add no answers:

    Rebus: 1=O|A

    C1NE

    A1. Sugar ___ ~ CONE ~ CANE

An answer doesn't have to be something its slot can spell.  A theme can read
a cell twice, as in TEENSYWEENSY in a six-cell slot `1EENSY` with `1=TW`, or
supply letters that appear in no cell, as in SILVERBACK in a slot spelling
BACK, with SILVER supplied by the grid's border:

    A7. Minuscule, in cutesy lingo ~ TEENSYWEENSY
    A1. Kind of gorilla ~ SILVERBACK

A tool that compares answers with their slots should report these as
unverified, not as errors.

An empty answer is written as a ' ~' that ends the line, ignoring trailing
whitespace.  The ' ~' is removed, the rest of the line is read as above, and
the empty answer is listed last, even when it is the solution.  [A trailing
space would be lost to editors that trim whitespace.]

    A5. What's uttered by a mime ~

A slot that reads TEN or is left empty lists both answers:

    A5. Number that pulled a disappearing act ~ TEN ~

A line with no ' ~ ' and no ' ~' at its end states no answer.

Where the puzzle printed a separate clue for each fill of a slot, each clue
gets its own line at the same position:

    D1. Took a chair ~ SAT
    D1. Had dinner ~ EAT

#### Clue Metadata

If you need to attach metadata to a clue, on a new line after the clue replace the ". "
with a " ^" - the key for the metadata is determined as being in-between the hat and
colon:

    A1. Gardener's concerns with A2 and D4. ~ BULB
    A1 ^Refs: A2 D4

Metadata keys are case-insensitive: `^Refs:`, `^refs:` and `^REFS:` are the
same key.  Tools that write .xd should emit them in titlecase (`^Refs:`).

The xd spec does not reserve any keys.

### Design (optional section)

A `## Design` section describes per-cell visual attributes: circles, shading,
bars, and images.  [It replaces the v3 'Special' field, which designated
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

No delimiter is needed between the definitions and the design grid: the
design grid starts at the first non-blank line after the last definition's
closing '}'.

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
  `background-size: 2 2`.  Newlines count as whitespace, so a definition may
  span several lines:

    ```css
    A {
      background: circle;
      bar-top: true;
    }
    ```

* Re-opening a character:

    ```css
    A { background: circle }
    A { bar-top: true }
    ```

* Opening many characters at once with a comma: `A, B { background: circle }`
* Separating many properties via semi colons: `A { background: circle; bar-top: true }`
* An optional trailing semi colon after the last property: `A { background: circle; }`
* Quoted values inside a rule body, within which none of `}`, `:`, `;` or
  `,` delimits
* Rejecting a comma inside a rule body, where it is never a separator:
  `background-size: 2 2`, never `background-size: 2, 2`

Explicit colors and light/dark variants are under discussion in
[#5](https://github.com/century-arcade/xdformat/issues/5).

### xdown Formatting

Clue bodies and metadata fields may contain inline markup, known as xdown.
A markup span is an opening '{', a type character, the content, the same type
character again, and a closing '}'.

Markup is available only in clue bodies and the values of metadata fields.
Metadata field keys, answers, and the grid are plain text; markup syntax
appearing in them is not interpreted.  [The markup represents the rendered
form, as it appeared in the original medium.]

Every ASCII punctuation character is reserved as a type character:

    ! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~

Only some of them are defined below; the rest are held for future span types,
so that adding one never changes the meaning of an existing file.  A '{'
followed by any other character (a letter, digit, space, and so on) is literal
text, so most clue bodies need no escaping.

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

Two of them point at something outside the clue:

* `{@link@}` - text with somewhere to go
* `{!image!}` - an image with its alt text

These two take attributes as well as content: the content, then a '|', then a
list of `key: value` pairs separated by ';', written the same way as a rule
body in the [Design](#design-optional-section) section.  A value containing
';' must be quoted, as a data URI does:

    src: 'data:image/png;base64,iVBORw0KGgo='

The attributes start at the first '|' outside of any nested span, so the
content may itself contain markup.  A renderer ignores an attribute it does
not know, so a later version can add one without breaking a file.

A link is its text, with the target in `href`:

    A16. See {@the notes | href: https://example.com@} ~ AHAB
    A16. See {@{*the notes*} | href: https://example.com@} ~ AHAB

An image is its alt text, with the image in `src`.  `width` and `height` are
optional:

    A17. Pictured: {!A sperm whale | src: https://example.com/whale.png!} ~ AHAB

`display` says how the image sits in the clue: `inline`, the default, puts it
in the run of text, and `block` renders it on its own line:

    A17. Pictured: {!A sperm whale | src: https://example.com/whale.png; display: block!} ~ AHAB

<!-- A color is its text, with `light` and `dark` giving the color to render it
in under a light theme and under a dark theme:

    A18. The {#red | light: #c00000; dark: #ff6666#} planet ~ MARS

Both are required. -->

One of them turns markup off:

* `{\literal\}` -- content passed through untouched

Nothing inside a literal is interpreted, and it takes no attributes.

A clue body that needs ' ~ ' writes the tilde this way, leaving the spaces
outside the literal, so that the clue line can still be split on ' ~ ' before
any markup is read:

    A1. What {\~\} means in π {\~\} 3.14 ~ ROUGHLY

is the clue 'What ~ means in π ~ 3.14' with the answer ROUGHLY.  A literal is
also how to write a '{' followed by a type character:

    A2. Empty set {\{}\} ~ NULL

The backslash has no meaning of its own: outside a literal sequence it is
ordinary text.  Nothing else in a clue body needs escaping, since a bare '~'
is fine, and a '{' is literal unless a type character follows it.

An empty literal, `{\\}`, is a line break.

## CHANGELOG

### 4.0-draft

Decisions from the 2026-07-10 spec discussion with Puzzmo and Ingrid; details
still open are tracked in [issues](https://github.com/century-arcade/xdformat/issues).

* [BREAKING] Dropping using capitals in the grid to indicate special blocks (use `## Design`)
* [BREAKING] `.` can now be used as a block
* [BREAKING] `?` is reserved in the grid for an unfilled cell, and can no
  longer be a rebus key
* [BREAKING] The 'Cluegroup' field is dropped
* Section headings are recommended, and required to use a design section; the
  implicit section order is still valid
* A grid cell holds exactly one Unicode codepoint; larger graphemes are rebuses.
* Metadata field keys and clue metadata keys are case-insensitive; writers
  should emit titlecase.
* Metadata fields other than 'Rebus' can now be xdown formatted
* [BREAKING] A rebus value is a '|'-separated list of options, the first being
  the solution, and an option may be empty.  '/' has no meaning in it.  [v3
  corpus files that used '/' by convention for Schrödinger or directional
  cells read differently now, and need migrating; see
  [rebus-conventions.md](rebus-conventions.md).]
* [BREAKING] Rules in the 'Rebus' field are separated only by whitespace.
  ',', '(' and ')' are reserved and '\' escapes, so a v3 field such as
  `1=OIL,2=WATER` is now an error and needs migrating to `1=OIL 2=WATER`.
* Cells that change together are linked by giving their keys to one rule
  (`12345=CIGAR|PENIS`).
* A clue line ending in ' ~' has an empty answer.
* The `## Design` section (adopted from Puzzmo's extension, without its
  `<style>` wrapper) replaces the 'Special' field and lowercase special cells.
* It is now possible to represent barred-grid Crosswords
* It is possible to represent background images in the grid
* A clue line holds a ' ~ '-separated list of answers, usually of size one;
  a Schrödinger slot lists each fill that answers the clue.  Answers always spell out rebus
  expansions.  An answer is a single word; text following it is ignored.
* Answers are what the clue means, and are never used to check a solve.
* A slot the puzzle clued once per fill may have several clue lines at one
  position.
* Markup adds subscript, superscript, and small caps, and formally nests.
* Links and images take named attributes (`href`, `src`, `display`) rather
  than a positional list of parts.
* A `{\literal\}` span passes its content through untouched; it replaces
  backslash escapes, and is how a clue body writes ' ~ '.
* `{\\}`, an empty literal, is a line break.

### 3.0

Includes syntax support for arbitrary clue metadata.

### 2.0

The 2.0 version of the specification adds support for `## [Section Name]` headings for sections of xd content. You can read more in [format specification](#format-specification) above.
