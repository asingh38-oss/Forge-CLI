"""
tools/file_write.py — Write or overwrite a file.
"""

from pathlib import Path
from src.codepilot.tools.base import make_schema

SCHEMA = make_schema(
    name="write_file",
    description="Write content to a file, creating it if it does not exist. Overwrites existing content.",
    properties={
        "file_path": {
            "type": "string",
            "description": "Path to the file to write.",
        },
        "content": {
            "type": "string",
            "description": "The content to write to the file.",
        },
    },
    required=["file_path", "content"],
)


def write_file(file_path: str, content: str) -> str:
    """Write content to a file, creating parent dirs as needed."""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        lines = content.count("\n") + 1
        return f"Written {lines} lines to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"