"""
providers/ollama_provider.py — Ollama local model provider with tool calling.
"""

import json
import requests
from typing import Any
from src.codepilot import config


class OllamaProvider:
    """Wraps the Ollama chat API for local models."""

    def __init__(self, model: str = ""):
        self._model = model or config.OLLAMA_MODEL
        self._base_url = config.OLLAMA_BASE_URL

    @property
    def model_name(self) -> str:
        return self._model

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        try:
            resp = requests.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return {"content": f"Ollama error: {e}", "tool_calls": None}

        msg = data.get("message", {})
        content = msg.get("content", "")

        # Normalize Ollama tool calls to OpenAI format
        raw_tool_calls = msg.get("tool_calls")
        tool_calls = None
        if raw_tool_calls:
            tool_calls = []
            for i, tc in enumerate(raw_tool_calls):
                fn = tc.get("function", {})
                args = fn.get("arguments", {})
                tool_calls.append({
                    "id": f"ollama_tc_{i}",
                    "type": "function",
                    "function": {
                        "name": fn.get("name", ""),
                        "arguments": json.dumps(args) if isinstance(args, dict) else args,
                    },
                })

        return {"content": content, "tool_calls": tool_calls}