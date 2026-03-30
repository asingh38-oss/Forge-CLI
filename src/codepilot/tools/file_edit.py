"""
tools/file_edit.py — Edit a file by replacing a unique string with new content.
"""

from pathlib import Path
from src.codepilot.tools.base import make_schema

SCHEMA = make_schema(
    name="edit_file",
    description=(
        "Edit a file by replacing an exact string with new content. "
        "The old_str must appear exactly once in the file."
    ),
    properties={
        "file_path": {
            "type": "string",
            "description": "Path to the file to edit.",
        },
        "old_str": {
            "type": "string",
            "description": "The exact string to find and replace. Must be unique in the file.",
        },
        "new_str": {
            "type": "string",
            "description": "The replacement string.",
        },
    },
    required=["file_path", "old_str", "new_str"],
)


def edit_file(file_path: str, old_str: str, new_str: str) -> str:
    """Replace old_str with new_str in the file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: file not found: {file_path}"

        content = path.read_text(encoding="utf-8", errors="ignore")
        count = content.count(old_str)

        if count == 0:
            return f"Error: old_str not found in {file_path}"
        if count > 1:
            return (
                f"Error: old_str appears {count} times in {file_path}. "
                "Make it more specific so it appears exactly once."
            )

        new_content = content.replace(old_str, new_str, 1)
        path.write_text(new_content, encoding="utf-8")
        return f"Successfully edited {file_path}"

    except Exception as e:
        return f"Error editing file: {e}"