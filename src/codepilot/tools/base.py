"""
tools/base.py — Base class and schema builder for all built-in tools.
"""

from typing import Any


def make_schema(
    name: str,
    description: str,
    properties: dict[str, Any],
    required: list[str],
) -> dict:
    """Build an OpenAI-compatible tool schema."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }