"""
providers/openai_provider.py — OpenAI GPT provider with tool calling.
"""

from typing import Any
from openai import OpenAI
from src.codepilot import config


class OpenAIProvider:
    """Wraps the OpenAI chat completions API."""

    def __init__(self, model: str = ""):
        self._model = model or config.OPENAI_MODEL
        self._client = OpenAI(api_key=config.OPENAI_API_KEY)

    @property
    def model_name(self) -> str:
        return self._model

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self._client.chat.completions.create(**kwargs)
        choice = response.choices[0].message

        tool_calls = None
        if choice.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in choice.tool_calls
            ]

        return {
            "content": choice.content,
            "tool_calls": tool_calls,
        }