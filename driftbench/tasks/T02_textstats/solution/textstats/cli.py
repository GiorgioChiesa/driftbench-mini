"""Command-line interface: python -m textstats.cli FILE"""
import argparse
import sys

from .counter import top_words, word_counts
from .readability import flesch_reading_ease
from .textio import read_text


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="textstats")
    p.add_argument("path")
    p.add_argument("--readability", action="store_true", help="print the Flesch reading ease")
    p.add_argument("--top", type=int, default=0)
    p.add_argument("--keep-stopwords", action="store_true")
    return p


def main(argv=None, out=sys.stdout) -> int:
    args = build_parser().parse_args(argv)
    text = read_text(args.path)
    counts = word_counts(text)
    print(f"words\t{sum(counts.values())}", file=out)
    print(f"unique\t{len(counts)}", file=out)
    if args.readability:
        print(f"flesch\t{flesch_reading_ease(text):.1f}", file=out)
    if args.top:
        for word, n in top_words(text, args.top, stopwords=set() if args.keep_stopwords else None):
            print(f"{word}\t{n}", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
