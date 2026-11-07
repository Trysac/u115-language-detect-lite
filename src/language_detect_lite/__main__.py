"""Command line interface for language-detect-lite."""

from __future__ import annotations

import argparse
import sys

from language_detect_lite import LanguageError, detect, rank


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Returns:
        0: Success with valid detection or rank
        1: Detection returned 'und' (no letters or below min_chars)
        2: Usage, IO, or parse error
    """
    parser = argparse.ArgumentParser(
        prog="language-detect-lite",
        description="Fast, dependency-free language detector using Cavnar-Trenkle n-grams.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="-",
        help="File path to inspect, or '-' to read from standard input (default).",
    )
    parser.add_argument(
        "--rank",
        action="store_true",
        help="Print all ranked language candidates and scores.",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=20,
        help="Minimum letters required for detection (default: 20).",
    )
    parser.add_argument(
        "--max-scan-chars",
        type=int,
        default=10_000,
        help="Maximum characters to scan (default: 10000).",
    )

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        return 2 if code != 0 else 0

    try:
        if args.path == "-":
            content = sys.stdin.read()
        else:
            with open(args.path, encoding="utf-8") as fh:
                content = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        sys.stderr.write(f"Error reading file: {exc}\n")
        return 2

    try:
        if args.rank:
            rankings = rank(content, max_scan_chars=args.max_scan_chars)
            for lang_code, score in rankings:
                sys.stdout.write(f"{lang_code}\t{score:.4f}\n")
            return 0

        res = detect(
            content,
            min_chars=args.min_chars,
            max_scan_chars=args.max_scan_chars,
        )
        if res is None:
            sys.stdout.write("und\n")
            return 1
        sys.stdout.write(f"{res}\n")
        return 0
    except LanguageError as err:
        sys.stderr.write(f"Language error: {err}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
