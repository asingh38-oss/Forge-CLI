"""
tools/file_read.py — Read a file from the local filesystem.
"""

from pathlib import Path
from src.codepilot.tools.base import make_schema

SCHEMA = make_schema(
    name="read_file",
    description="Read the contents of a file. Returns the file content with line numbers.",
    properties={
        "file_path": {
            "type": "string",
            "description": "Path to the file to read.",
        },
        "start_line": {
            "type": "integer",
            "description": "Optional start line (1-indexed). Reads from here if provided.",
        },
        "end_line": {
            "type": "integer",
            "description": "Optional end line (inclusive). Reads to here if provided.",
        },
    },
    required=["file_path"],
)


def read_file(file_path: str, start_line: int = None, end_line: int = None) -> str:
    """Read a file and return its contents with line numbers."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: file not found: {file_path}"
        if not path.is_file():
            return f"Error: path is not a file: {file_path}"

        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

        # Apply line range if specified
        start = (start_line - 1) if start_line else 0
        end = end_line if end_line else len(lines)
        lines = lines[start:end]

        # Add line numbers
        offset = start + 1
        numbered = [f"{offset + i:4d} | {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered)

    except Exception as e:
        return f"Error reading file: {e}"