"""
Deterministic JSON utilities
Ensures canonical JSON output with sorted keys and compact formatting
"""

import json
from typing import Any, TextIO


def dumps(obj: Any) -> str:
    """
    Serialize object to deterministic JSON string.
    Uses sorted keys and compact separators for canonical output.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def dump(obj: Any, fp: TextIO) -> None:
    """
    Serialize object to deterministic JSON and write to file.
    Appends newline for readability.
    """
    fp.write(dumps(obj))
    fp.write("\n")


def loads(s: str) -> Any:
    """Load JSON from string."""
    return json.loads(s)


def load(fp: TextIO) -> Any:
    """Load JSON from file."""
    return json.load(fp)

