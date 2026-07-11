"""Small filename/date helpers and stderr logging for xdformat."""

import datetime
import os
import re
import sys
from collections import namedtuple


def info(s):
    print("INFO: %s" % s, file=sys.stderr)


def warn(s):
    print("WARNING: %s" % s, file=sys.stderr)


def error(s):
    print("ERROR: %s" % s, file=sys.stderr)


def parse_pathname(path):
    # Fix to proper split names like file.xml.1
    ext = os.extsep + os.extsep.join(os.path.basename(path).split(os.extsep)[1:])
    path, fn = os.path.split(path)
    ext = ext if fn else ''
    base = os.path.splitext(fn)[0]
    nt = namedtuple('Pathname', 'path base ext filename')
    return nt(path=path, base=base, ext=ext, filename=fn)


def parse_pubid(fn):
    m = re.search("(^[A-Za-z0-9][A-Za-z]*)", parse_pathname(fn).base)
    return m.group(1).lower() if m else None


def construct_date(y, m, d):
    thisyear = datetime.datetime.today().year
    year, mon, day = int(y), int(m), int(d)

    if year > 1900 and year <= thisyear:
        pass
    elif year < 100:
        if year >= 0 and year <= thisyear - 2000:
            year += 2000
        else:
            year += 1900
    else:
        return None

    if mon < 1 or mon > 12:
        return None

    if day < 1 or day > 31:
        return None

    return datetime.date(year, mon, day)


# from original filename
def parse_date_from_filename(fn):
    base = parse_pathname(fn).base
    m = re.search(r"(\d{2,4})-?(\d{2})-?(\d{2})", base)
    if m:
        g1, g2, g3 = m.groups()
        # try YYMMDD first, then MMDDYY
        return construct_date(g1, g2, g3) or construct_date(g3, g1, g2)
