#!/usr/bin/env python3
"""
Atomic file writer for neXco Chapter Dashboard.
Ensures files are written completely or not at all.
"""

import json
import os
from pathlib import Path


class WriteError(Exception):
    """Raised when file writing fails."""

    def __init__(self, filepath: str, message: str):
        self.filepath = filepath
        self.message = message
        super().__init__(message)


def atomic_write_json(data: dict, filepath: str) -> None:
    """
    Write JSON data atomically.

    Uses a temp file + rename pattern to ensure readers
    never see partial/corrupt data.

    Args:
        data: Dict to serialize as JSON
        filepath: Target file path

    Raises:
        WriteError: If write fails
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Use a temp file in the same directory
    temp_path = path.with_suffix(f".tmp.{os.getpid()}")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())

        # Atomic rename
        os.replace(temp_path, path)

        # Set web-accessible permissions (644)
        os.chmod(path, 0o644)

    except Exception as e:
        # Clean up temp file if it exists
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise WriteError(filepath, f"Failed to write JSON: {e}")


def atomic_write_text(content: str, filepath: str) -> None:
    """
    Write text content atomically.

    Args:
        content: Text content to write
        filepath: Target file path

    Raises:
        WriteError: If write fails
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    temp_path = path.with_suffix(f".tmp.{os.getpid()}")

    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temp_path, path)

        # Set web-accessible permissions (644)
        os.chmod(path, 0o644)

    except Exception as e:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise WriteError(filepath, f"Failed to write text: {e}")


if __name__ == "__main__":
    import tempfile

    # Test atomic write
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test", "data.json")
        atomic_write_json({"test": True}, test_file)
        print(f"Successfully wrote to: {test_file}")
        with open(test_file) as f:
            print(f"Content: {f.read()}")
