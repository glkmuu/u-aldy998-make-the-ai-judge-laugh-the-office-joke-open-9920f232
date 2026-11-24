#!/usr/bin/env python3
"""Writes the Office Joke Open entry to /output/entry.txt and ./entry.txt.

Stdlib only. The entry is a fixed string; the program validates it against
the competition gate (UTF-8, 1-200 characters, exactly one line, not only
whitespace) before writing, then reads it back and fails hard on mismatch.

Run from anywhere with ``python3 main.py``. The entry is written with no
trailing newline, byte for byte, so the file's sha256 is stable across runs.
"""

import hashlib
import os
import sys

ENTRY = "I put 'per my last email' in my will so my family knows exactly how passive-aggressive I was."

PRIMARY_OUTPUT = "/output/entry.txt"
LOCAL_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.txt")


def validate_entry(entry):
    """Check the competition gate before writing. Raises ValueError on failure.

    Each failure message names the exact gate rule that was broken and the
    offending value, so a rejected entry can be fixed without guessing.
    """
    if not isinstance(entry, str):
        raise ValueError("entry must be a str, got %s" % type(entry).__name__)
    if not (1 <= len(entry) <= 200):
        raise ValueError(
            "entry must be 1-200 characters (gate limit), got %d characters"
            % len(entry)
        )
    if entry.strip() == "":
        raise ValueError("entry must not be only whitespace (gate: non-empty text)")
    if "\n" in entry or "\r" in entry:
        raise ValueError(
            "entry must be exactly one line (gate: no line breaks), "
            "found a newline at index %d"
            % min(i for i, ch in enumerate(entry) if ch in ("\n", "\r"))
        )
    for ch in entry:
        if ord(ch) < 0x20 and ch not in ("\t",):
            raise ValueError(
                "entry contains a control character U+%04X, which the gate "
                "rejects as non-text" % ord(ch)
            )
    entry.encode("utf-8")  # raises UnicodeEncodeError if not encodable
    return True


def write_and_verify(entry, path):
    """Write entry (no trailing newline), read it back, fail hard if it differs.

    Verifies both the decoded text and the exact bytes (sha256), so a
    trailing newline or encoding change cannot slip through.
    """
    validate_entry(entry)
    expected = entry.encode("utf-8")
    expected_digest = hashlib.sha256(expected).hexdigest()
    with open(path, "wb") as f:
        f.write(expected)
    with open(path, "rb") as f:
        raw = f.read()
    if raw != expected:
        raise RuntimeError("verification failed for %s: bytes differ" % path)
    if hashlib.sha256(raw).hexdigest() != expected_digest:
        raise RuntimeError("verification failed for %s: sha256 mismatch" % path)
    return path


OUTPUTS = (PRIMARY_OUTPUT, LOCAL_OUTPUT)


def main():
    """Validate the fixed entry once, then write and verify it everywhere."""
    validate_entry(ENTRY)
    for path in OUTPUTS:
        write_and_verify(ENTRY, path)
    digest = hashlib.sha256(ENTRY.encode("utf-8")).hexdigest()
    print("entry written to %d outputs: %d chars, sha256 %s"
          % (len(OUTPUTS), len(ENTRY), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
