"""Character-encoding cleanup for text pulled out of source puzzle files.

See doc/character-encoding.md for the full taxonomy of mojibake patterns
these functions handle.  Kept in lockstep with the XD009/XD010 fixers in
century-arcade/xd's xdlint.py.
"""

import html
import re
import urllib.parse


# C1 control codepoints (U+0080..U+009F) appear in puzzle text whenever bytes
# from a non-latin-1 source were decoded as latin-1. Most are cp1252 mojibake
# (em dashes, smart quotes, š), but a handful are Mac Roman ('é' for U+008E),
# UTF-8 trailers (\xe2\x80\xXX with the lead byte lost or surviving as 'â'),
# or symbols neither encoding represents (°, ÷). Kept in lockstep with the
# XD010 fixer in xdlint.py.
_CP1252_OVERRIDES = {chr(0x8e): "é"}  # cp1252's 'Ž' is wrong in our corpus
_CP1252_SKIP_SINGLE = {chr(0x80), chr(0x98)}  # too ambiguous to auto-decide
_C1_RE = re.compile(r"[\x80-\x9f]")
_UTF8_TRAILER_RE = re.compile(r"â?\x80[\x80-\x9f]")
# Orphan smart-quote trailer: U+009C/D after any close-quote variant is the
# trailing byte of a UTF-8 smart quote whose lead bytes were already turned
# into a quote upstream. Strip it. Must run BEFORE the cp1252 pass because
#   - U+009D is undefined in cp1252 and survives, but
#   - U+009C is cp1252's 'œ' so the cp1252 pass would consume it.
# Lead-quote variants matched: straight ASCII ", cp1252's curly bytes
# U+0093/U+0094 (which only become real curly quotes during the cp1252
# pass), and the already-converted curly U+201C/U+201D. The trailer is
# always U+009C (left) or U+009D (right).
_ORPHAN_QUOTE_TRAILER_RE = re.compile(r'["\x93\x94“”][\x9c\x9d]')


# UTF-8 byte sequence \xc2\xXX or \xc3\xXX (encoding U+0080-U+00FF, the
# latin supplement) misread as latin-1 produces 'Â' or 'Ã' followed by a
# char in U+0080-U+00BF (the continuation-byte range). Re-encoding as
# latin-1 and decoding as UTF-8 reverses the corruption. Common in puzzle
# text from sources where UTF-8 .puz contents got decoded as ISO-8859-1
# by puzpy. Real text rarely has 'Â'/'Ã' followed by a U+0080-U+00BF
# char, so the false-positive rate is low.
_LATIN1_UTF8_RE = re.compile(r'[\xc2\xc3][\x80-\xbf]')


def clean_latin1_utf8_mojibake(s: str) -> str:
    """Re-decode UTF-8 byte pairs that were misread as latin-1. Catches
    accented vowels and other latin-supplement characters that survived
    a wrong-encoding round-trip (e.g. 'Ãª' -> 'ê', 'Ã©' -> 'é')."""
    def repl(m):
        try:
            return m.group(0).encode('latin-1').decode('utf-8')
        except UnicodeDecodeError:
            return m.group(0)
    return _LATIN1_UTF8_RE.sub(repl, s)


def clean_c1_controls(s: str) -> str:
    """Clean C1 control codepoints (U+0080-U+009F) out of a string.

    Four passes:
    1. UTF-8 trailer: optional 'â' + \\u0080 + another C1 control gets
       reconstructed by latin-1 encoding then UTF-8 decoding (with an
       \\xe2 prefix added if 'â' was missing). Recovers smart quotes,
       en/em dashes, etc. that lost their lead byte.
    2. Orphan smart-quote trailer: U+009C/D right after a straight " is
       a stray UTF-8 byte from a curly quote whose \\xe2\\x80 lead got
       replaced with the straight " upstream. Drop the trailer.
    3. Per-codepoint overrides where cp1252 maps wrong (U+008E -> 'é').
    4. cp1252 default for the rest, except U+0080 and U+0098 which the
       caller must resolve manually (cp1252 says '€' / '˜' but the corpus
       uses these for '°' / '÷' / etc.).

    Codepoints undefined in cp1252 (U+0081, U+008D, U+008F, U+0090, U+009D)
    that survive pass 2 pass through unchanged.
    """
    def utf8_repl(m):
        s = m.group(0)
        bs = s.encode("latin-1")
        if not bs.startswith(b"\xe2"):
            bs = b"\xe2" + bs
        try:
            return bs.decode("utf-8")
        except UnicodeDecodeError:
            return s
    s = _UTF8_TRAILER_RE.sub(utf8_repl, s)
    # Orphan strip runs BEFORE cp1252 so U+009C (which cp1252 maps
    # to a real char) isn't consumed before we recognize it as a stray
    # trailer. Preserves the lead-quote char, drops only the orphan.
    s = _ORPHAN_QUOTE_TRAILER_RE.sub(lambda m: m.group(0)[0], s)

    def repl(m):
        ch = m.group(0)
        if ch in _CP1252_OVERRIDES:
            return _CP1252_OVERRIDES[ch]
        if ch in _CP1252_SKIP_SINGLE:
            return ch
        try:
            return ch.encode("latin-1").decode("cp1252")
        except UnicodeDecodeError:
            return ch
    s = _C1_RE.sub(repl, s)
    return s


def decode(s):
    """Full cleanup pipeline for clue/header text from a source puzzle file."""
    # UTF-8-encoded characters read as latin-1 surface as 'Â' + trailing
    # byte. Strip the orphan 'Â' before a C1 control (then clean_c1_controls
    # handles the trailer). E.g. .puz bytes \xc2\x92 (UTF-8 U+0092) read as
    # latin-1 -> 'Â' -> '' -> "'".
    s = re.sub(r'Â([\x80-\x9f])', r'\1', s)
    # UTF-8 NBSP read as latin-1 surfaces as 'Â\xa0'; collapse to space.
    s = s.replace('\xc2\xa0', ' ')
    s = s.replace('\xa0', ' ')
    # Stray 'Ã\x82' (puz bytes \xc3\x82 read as latin-1) is a known mojibake
    # artifact in this corpus -- not real text. The 2016-era decode() stripped
    # it explicitly; without that, clean_latin1_utf8_mojibake below would re-
    # decode it as 'Â' (U+00C2), inserting a literal capital-A-circumflex in
    # the middle of clue text. Strip before the systematic mojibake pass.
    s = s.replace('\xc3\x82', '')
    # \xc3\xa8 = UTF-8 byte sequence for U+00E8 (è) misread as latin-1 ('Ã¨').
    # Targeted because real 'Ã¨' is unusual in puzzle text.
    s = s.replace('Ã¨', 'è')
    # MacRoman left/right curly double quotes.
    s = s.replace('\xd3', '"')
    s = s.replace('\xd4', '"')
    # UTF-8 latin-supplement bytes (\xc3\xXX, \xc2\xXX) misread as latin-1
    # leave 'Ã'/'Â' + continuation byte. Re-decode before C1 cleanup so any
    # 'Â' + C1 sequence collapses cleanly into the C1 path below.
    s = clean_latin1_utf8_mojibake(s)
    # Systematic C1-control cleanup (cp1252 + Mac Roman + UTF-8 trailers).
    # Replaces the per-byte hand-coded list this function used to carry.
    s = clean_c1_controls(s)
    # The corpus convention is ASCII typography (em dash is the lone Unicode
    # exception, matching the legacy `\x97 -> "—"` mapping). Flatten the
    # other smart-typography chars that clean_c1_controls produced.
    s = s.translate(str.maketrans({
        '‘': "'", '’': "'",  # curly single quotes
        '“': '"', '”': '"',  # curly double quotes
        '…': '...',               # horizontal ellipsis
    }))
    s = urllib.parse.unquote(s)
    s = html.unescape(s)
    # Remove spurious semicolons from invalid HTML entity refs
    # (e.g. html2text converts "B&O" to "B&O;")
    s = re.sub(r'&([A-Za-z0-9]+);', r'&\1', s)
    # Collapse any run of whitespace to a single space (clue text shouldn't have tabs or multi-space runs)
    s = re.sub(r'\s+', ' ', s)
    return s
