"""Minimal CLI: python3 -m gki_reference.cli --config <json> --input <file>..."""

import argparse
import json
import sys
from pathlib import Path

from .blocked import Blocked
from .pipeline import ReferencePipeline


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="gki-reference",
                                     description="GKI reference pipeline (profile: reference)")
    parser.add_argument("--config", required=True, help="path to config JSON")
    parser.add_argument("--input", required=True, nargs="+", help="input text/markdown file(s)")
    args = parser.parse_args(argv)

    with open(args.config, "r", encoding="utf-8") as f:
        config = json.load(f)

    try:
        pipeline = ReferencePipeline(config)
    except Blocked as b:
        print(str(b), file=sys.stderr)
        return 2

    exit_code = 0
    for input_file in args.input:
        try:
            result = pipeline.ingest_file(Path(input_file))
            print(json.dumps({"status": "published", **result}))
        except Blocked as b:
            print(json.dumps({"status": "blocked", "input": input_file,
                              "reason_code": b.code}))
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
