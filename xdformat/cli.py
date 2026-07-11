"""Shared command-line driver for the format converters."""

import argparse
import os
import sys

from .utils import parse_pathname


def convert_main(parse_func, description, mode='rb', argv=None):
    p = argparse.ArgumentParser(description=description)
    p.add_argument('inputs', nargs='+', metavar='FILE', help='source puzzle file(s)')
    p.add_argument('-o', '--output-dir', metavar='DIR',
                   help='write one <base>.xd per input into DIR (default: stdout)')
    args = p.parse_args(argv)

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    nerrors = 0
    for fn in args.inputs:
        with open(fn, mode) as f:
            contents = f.read()

        try:
            xd = parse_func(contents, fn)
        except Exception as e:
            print("ERROR: %s: %s" % (fn, e), file=sys.stderr)
            nerrors += 1
            continue

        out = xd.to_unicode()
        if args.output_dir:
            outfn = os.path.join(args.output_dir, parse_pathname(fn).base + '.xd')
            with open(outfn, 'w', encoding='utf-8') as outf:
                outf.write(out)
        else:
            sys.stdout.write(out)

    return 1 if nerrors else 0
