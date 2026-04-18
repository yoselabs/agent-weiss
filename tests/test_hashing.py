"""Tests for file hashing utility."""
from pathlib import Path
from agent_weiss.lib.hashing import sha256_file, sha256_bytes


def test_sha256_bytes_known_vector():
    """sha256_bytes returns hex digest matching standard test vector."""
    assert sha256_bytes(b"abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_sha256_bytes_empty():
    """Empty input has known hash."""
    assert sha256_bytes(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_sha256_file_roundtrip(tmp_path: Path):
    """sha256_file reads file content and matches sha256_bytes."""
    f = tmp_path / "x.txt"
    f.write_bytes(b"hello\n")
    assert sha256_file(f) == sha256_bytes(b"hello\n")


def test_sha256_file_streaming(tmp_path: Path):
    """sha256_file works for files larger than chunk size."""
    f = tmp_path / "big.bin"
    payload = b"x" * (1024 * 1024)  # 1 MiB
    f.write_bytes(payload)
    assert sha256_file(f) == sha256_bytes(payload)
