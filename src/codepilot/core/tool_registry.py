"""
core/tool_registry.py — Central registry for all tools (built-in + MCP).
"""

from typing import Callable, Any


class ToolRegistry:
    """Holds all available tools and their schemas."""

    def __init__(self):
        self._tools: dict[str, dict] = {}         # name → OpenAI tool schema
        self._handlers: dict[str, Callable] = {}  # name → callable

    def register(self, schema: dict, handler: Callable):
        """Register a tool with its OpenAI schema and a callable handler."""
        name = schema["function"]["name"]
        self._tools[name] = schema
        self._handlers[name] = handler

    def get_schemas(self) -> list[dict]:
        """Return all tool schemas for the LLM."""
        return list(self._tools.values())

    def get_handler(self, name: str) -> Callable | None:
        return self._handlers.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())