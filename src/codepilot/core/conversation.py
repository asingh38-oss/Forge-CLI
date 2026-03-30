"""
core/conversation.py — Manages the message history for the agentic loop.
"""

from typing import Any


class Conversation:
    """Holds the full message history sent to the LLM each turn."""

    def __init__(self, system_prompt: str = ""):
        self.messages: list[dict[str, Any]] = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_call(self, tool_call_id: str, name: str, arguments: str):
        """Record a tool call made by the assistant."""
        self.messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {"name": name, "arguments": arguments},
            }],
        })

    def add_tool_result(self, tool_call_id: str, content: str):
        """Record the result of a tool execution."""
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })

    def clear(self):
        """Keep only the system message."""
        system = [m for m in self.messages if m["role"] == "system"]
        self.messages = system