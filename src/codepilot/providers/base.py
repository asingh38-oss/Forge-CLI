"""
providers/base.py — Base protocol for LLM providers.
"""

from typing import Any, Protocol


class LLMProvider(Protocol):
    """Common interface all providers must implement."""

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        """
        Send messages to the LLM and return a normalized response dict:
        {
            "content": str | None,
            "tool_calls": list | None,
        }
        """
        ...

    @property
    def model_name(self) -> str:
        ...