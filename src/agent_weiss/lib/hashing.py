"""File and byte hashing utilities.

Used for prescribed_files content-addressing in .agent-weiss.yaml,
drift detection against bundle.yaml, and reconciliation.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

_CHUNK_SIZE = 64 * 1024


def sha256_bytes(data: bytes) -> str:
    """Return the lowercase hex sha256 of bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """Return the lowercase hex sha256 of a file's contents.

    Streams in 64 KiB chunks; safe for large files.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(_CHUNK_SIZE):
            h.update(chunk)
    return h.hexdigest()
