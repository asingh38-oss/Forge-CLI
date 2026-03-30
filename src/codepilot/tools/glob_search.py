"""
tools/glob_search.py — Find files matching a glob pattern.
"""

from pathlib import Path
from src.codepilot.tools.base import make_schema

SCHEMA = make_schema(
    name="glob_search",
    description="Find files matching a glob pattern. Useful for exploring project structure.",
    properties={
        "pattern": {
            "type": "string",
            "description": "Glob pattern, e.g. '**/*.py' or 'src/**/*.ts'.",
        },
        "directory": {
            "type": "string",
            "description": "Root directory to search from. Defaults to current directory.",
        },
    },
    required=["pattern"],
)


def glob_search(pattern: str, directory: str = ".") -> str:
    """Find files matching a glob pattern."""
    try:
        root = Path(directory)
        if not root.exists():
            return f"Error: directory not found: {directory}"

        matches = sorted(root.glob(pattern))
        files = [str(p) for p in matches if p.is_file()]
        dirs  = [str(p) + "/" for p in matches if p.is_dir()]

        results = dirs + files
        if not results:
            return f"No files found matching: {pattern}"
        return "\n".join(results[:200])  # cap at 200 results

    except Exception as e:
        return f"Error during glob search: {e}"