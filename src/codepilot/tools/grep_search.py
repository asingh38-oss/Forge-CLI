"""
tools/grep_search.py — Search for a pattern across files in a directory.
"""

import re
from pathlib import Path
from src.codepilot.tools.base import make_schema

SCHEMA = make_schema(
    name="grep_search",
    description="Search for a regex pattern across files in a directory. Returns matching lines with file and line number.",
    properties={
        "pattern": {
            "type": "string",
            "description": "The regex pattern to search for.",
        },
        "directory": {
            "type": "string",
            "description": "Directory to search in. Defaults to current directory.",
        },
        "file_glob": {
            "type": "string",
            "description": "Glob pattern to filter files, e.g. '*.py'. Defaults to all files.",
        },
    },
    required=["pattern"],
)


def grep_search(
    pattern: str,
    directory: str = ".",
    file_glob: str = "**/*",
) -> str:
    """Search for a regex pattern across files."""
    try:
        regex = re.compile(pattern)
        root = Path(directory)
        if not root.exists():
            return f"Error: directory not found: {directory}"

        matches = []
        for path in sorted(root.glob(file_glob)):
            if not path.is_file():
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
                for i, line in enumerate(lines, start=1):
                    if regex.search(line):
                        matches.append(f"{path}:{i}: {line.strip()}")
            except Exception:
                continue

        if not matches:
            return f"No matches found for pattern: {pattern}"
        return "\n".join(matches[:100])  # cap at 100 results

    except re.error as e:
        return f"Invalid regex pattern: {e}"
    except Exception as e:
        return f"Error during search: {e}"