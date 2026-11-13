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

Digits, most symbols other than '#', '.', '\_' and '?', and printable unicode
characters (if needed) can be used to indicate rebus cells.  The 'Rebus'
field provides the translation:

    Rebus: 1=ONE 2=TWO 3=THREE

The field's grammar is:

    field  := group (ws group)*
    group  := rule ("," rule)*
    rule   := key "=" option ("|" option)*
    option := (char | "\|" | "\," | "\\")*

Here `ws` is one or more spaces or tabs, `key` is one grid character, and
`char` is any character other than whitespace, '|', ',' or '\'.  A parser
reads the field in the grammar's order.  It splits on whitespace, then on
unescaped ',', then separates each key from its value, then splits on
unescaped '|', and resolves escapes last.

Every rebus key in the grid is declared, and no key is declared twice.  A key
cannot be A-Z, '#', '.', '\_', '=', '|', ',' or '\'.  An empty rule, such as
one left by a trailing ',', is an error.  So is a backslash before anything
other than '|', ',' or '\'.

The value is plain text, and xdown markup is not read in it.

#### Options

Each option is a string that is correct in the cell.  The first is the cell's
solution, which an app shows when the cell is revealed, and the others are
also accepted:

    Rebus: 1=HEART 2=EIGHT|8

A cell with several options takes any of them.  The field doesn't record
whether the options are different answers, as in a Schrödinger cell, or
different ways of typing one answer, such as EIGHT and 8.  The answers on the
clue lines record that.

An option may be empty, which means the cell is correct when left empty.  The
cell is still a white cell, numbered and counted in its entries like any
other.  Here cell 1 is always empty, cell 2 is empty with H also accepted, and
cell 3 is H with empty also accepted:

    Rebus: 1= 2=|H 3=H|

A backslash escapes '|', ',' or another backslash.  Every other character is
literal, including '/' and '=':

    Rebus: 1=/ 2=\| 3=\, 4=\\

#### Schrödinger cells

A Schrödinger cell is one whose options are different answers.  The solver
may enter any of them, and every entry through the cell is built to work
either way:

    Rebus: 1=O|A

    TILE
    APEX
    C1NE
    ODDS

    A6. Sugar ____ ~ CONE ~ CANE
    D2. Apple tech ~ IPOD ~ IPAD

Cells that share a key share its options, but each cell chooses among them on
its own.  In HEIGHTANDWEIGHT, either EIGHT may be written as 8:

    Rebus: 1=EIGHT|8

    H1ANDW1

#### Linked cells

Cells that change together are linked, and must hold the options at the same
position.  This keeps a slot reading CIGAR or PENIS, and never CEGIR.

Cells are linked only by joining their rules with ',', with no whitespace,
into a group.  The rules of a group must have the same number of options:

    Rebus: 1=C|P,2=I|E,3=G|N,4=A|I,5=R|S

The first options spell CIGAR and the second spell PENIS.  A group links every
cell marked with any of its keys.  Those cells don't have to be adjacent, in
one entry, or in grid order.

A cell in a group may hold several characters.  In SHORTLINE/CHORTLING, the
cells read SC and EG down, and S or C and E or G across:

    Rebus: 1=SC|S|C,2=EG|E|G

A cell in a group may also hold nothing, as in a slot that reads TEN or is
left empty:

    Rebus: 1=|T,2=|E,3=|N

Groups are independent of one another.  In `THE[N|S]O[R|U]TH[E|W][A|E]ST`,
either of NORTH or SOUTH can go with either of EAST or WEST:

    Rebus: 1=N|S,2=R|U 3=E|W,4=A|E

#### Checking a solve

The grid is solved when every A-Z cell holds its letter, and every rebus cell
is solved.  A rebus cell outside a group is solved when it holds one of its
options.  A group is solved when there is a position p at which every cell
marked with one of its keys holds option p of its own rule.  An empty cell
holds the empty string.

Two positions may hold the same option.  Here cells 1 and 2 accept LAT, LUG
and LAG, but not LUT:

    Rebus: 1=A|U|A,2=T|G|G

    L12

Only the grid and the 'Rebus' field decide whether a grid is solved.  Answers
on clue lines are not to be used in the verification.

#### Readings that differ by direction

A cell holds one string, and its across and down entries both read it.  Where
a puzzle reads a cell one way across and another way down, such as PH across
and F down, the field lists each string the cell accepts, and the answers
carry the direction:

    Rebus: 1=PH|F

    AL1A
    CARD
    EGOS

    A1. First in a series ~ ALPHA
    D3. To and ____ ~ FRO

#### Converted puzzles

A source format may list alternates for a cell without saying how they relate.
They might be different answers, a reading per direction, or the outlet's
shortcuts for typing a rebus.  A converter that can't tell which leaves the
cells unlinked, with the source's solution first and its alternates after:

    Rebus: 1=W/T|T/W|WT|TW|W|T 2=A/R|R/A|AR|RA|A|R

This accepts exactly what the source accepts.  Linking cells says something
about the puzzle that the source doesn't, so it is left to someone who knows
the puzzle.  An editor who knows these cells spell STARWARS or STARTREK joins
the rules.  They also move the two readings to the front, so that reveal shows
a letter, and line up the other typings position by position:

    Rebus: 1=W|T|W/T|T/W|WT|TW,2=A|R|A/R|R/A|AR|RA

Linking narrows what is accepted.  A typing in one cell must sit at the same
position as the typings in its partners, so W/T beside AR is now rejected.

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

The reference runs to the first '.' on the line, and the clue body from
there to the first ' ~ ', or to the end of the line if it has none.  (A line
ending in ' ~' has an empty answer; see below.)  After each ' ~ ' the answer
is the first word;
this includes non-ASCII characters and ends at the first whitespace.

Anything else in that segment is ignored:

    A6. Book look-up ~ INDEX (5 letters)

is the clue 'Book look-up' with the single answer INDEX.  Trailing text has
no defined meaning in .xd and should be ignored.

A clue body may carry inline markup for italics, links, images and more; the
syntax is given in [xdown Formatting](#xdown-formatting) below.

The clue is followed by a list of one or more full answers, all separated by
a tilde with spaces on both sides (' ~ ').  An answer is what the clue means,
written out in full with any rebuses expanded; rebus keys never appear in
answers.  [This makes clue/answer lines independently useful.]  Most clues
have exactly one answer.

A clue whose slot has several fills that answer it (a Schrödinger slot) lists
each of them, and should list first the one the cells' solutions spell.
Other typings of the same answer, such as 8 for EIGHT, add no answers:

    Rebus: 1=O|A
  

    C1NE


    A1. Sugar ___ ~ CONE ~ CANE

Answers never decide whether a grid is solved, and an answer doesn't have to
be something its slot can spell.  A theme can read a cell twice, as in
TEENSYWEENSY in a six-cell slot `1EENSY` with `1=TW`, or supply letters that
appear in no cell, as in SILVERBACK in a slot spelling BACK, with SILVER
supplied by the grid's border:

    A7. Minuscule, in cutesy lingo ~ TEENSYWEENSY
    A1. Kind of gorilla ~ SILVERBACK

A tool that compares answers with their slots should report these as
unverified, not as errors.

An empty answer is written as a ' ~' that ends the line.  The ' ~' is removed,
the rest of the line is read as above, and the empty answer comes after any
others.  [A trailing space would be lost to editors that trim whitespace.]

    A5. What's uttered by a mime ~

A slot that reads TEN or is left empty can list both answers, or leave the
empty one out:

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
  the solution.  '/' has no meaning in it.  [v3 corpus files that used '/' by
  convention for Schrödinger or directional cells read differently now, and
  need migrating; see [rebus-conventions.md](rebus-conventions.md).]
* [BREAKING] ',' in the 'Rebus' field joins rules into a linked group instead
  of separating them.  For rules with one option each, as in the v3 corpus,
  the meaning is unchanged, but ', ' leaves an empty rule and is now an error.
* Cells that change together are linked only by ','-joined rules
  (`1=C|P,2=I|E,3=G|N,4=A|I,5=R|S`).  Cells that share a key choose among its
  options independently.
* The 'Rebus' field has a formal grammar.
* An option may be empty, for a cell that is correct when left empty, and a
  clue line ending in ' ~' has an empty answer.
* The `## Design` section (adopted from Puzzmo's extension, without its
  `<style>` wrapper) replaces the 'Special' field and lowercase special cells.
* It is now possible to represent barred-grid Crosswords
* It is possible to represent background images in the grid
* A clue line holds a ' ~ '-separated list of answers, usually of size one;
  a Schrödinger slot lists all valid fills.  Answers always spell out rebus
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
