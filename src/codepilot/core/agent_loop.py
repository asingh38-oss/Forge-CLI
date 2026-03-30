"""
core/agent_loop.py — The core think-act-observe agentic loop.

Flow:
  1. Send conversation history + tool schemas to LLM
  2. If LLM returns tool calls → confirm (if needed) → execute → append results
  3. Repeat until LLM returns text-only response or max iterations reached
"""

import json
from typing import Any

from rich.console import Console

from src.codepilot.core.conversation import Conversation
from src.codepilot.core.tool_registry import ToolRegistry
from src.codepilot.ui.renderer import (
    render_tool_call,
    render_tool_result,
    render_assistant_message,
    render_error,
    confirm_tool_execution,
)
from src.codepilot import config

# Tools that are destructive and require confirmation by default
DESTRUCTIVE_TOOLS = {"write_file", "edit_file", "run_shell", "delete_file"}


class AgentLoop:
    """
    Drives the agentic loop for a single user task.
    """

    def __init__(
        self,
        provider,
        registry: ToolRegistry,
        console: Console,
        auto_execute: bool = False,
    ):
        self.provider   = provider
        self.registry   = registry
        self.console    = console
        self.auto_execute = auto_execute

    def run(self, task: str, conversation: Conversation) -> str:
        """
        Run the agentic loop for a given task.
        Mutates conversation in place and returns the final assistant reply.
        
        Steps:
        1. Add the user task to the conversation history.
        2. Retrieve available tool schemas from the tool registry.
        3. Perform a loop operation up to a maximum number of iterations as defined in configuration:
            a. Call the Language Learning Model (LLM) with the current conversation history and tool schemas.
            b. Check if the LLM has returned only a text response:
                - If yes, append this as an assistant message in the conversation and render the message, then terminate the loop by returning this response.
            c. If tool calls are returned by the LLM:
                - Record the assistant message including these tool calls.
                - Iterate through each tool call:
                    i. Extract and render the tool name and arguments.
                    ii. Check if confirmation is needed for destructive tools:
                        - If confirmation is required and not granted, skip execution for this tool.
                    iii. Retrieve the handler for the tool and execute it:
                        - Handle errors during execution gracefully.
                    iv. Render the tool result and store the outcome in the conversation history.
        4. If the maximum iterations are reached without a text-only response, indicate that the task may be incomplete.
        """
        conversation.add_user(task)
        schemas = self.registry.get_schemas()

        for iteration in range(config.MAX_ITERATIONS):
            # --- Call LLM ---
            response = self.provider.chat(
                messages=conversation.messages,
                tools=schemas if schemas else None,
            )

            # --- Text only response → done ---
            if not response.get("tool_calls"):
                text = response.get("content", "")
                conversation.add_assistant(text)
                render_assistant_message(self.console, text)
                return text

            # --- Tool calls ---
            tool_calls = response["tool_calls"]

            # Record assistant message with tool calls
            conversation.messages.append({
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            })

            # Execute each tool call
            for tc in tool_calls:
                tool_id   = tc["id"]
                tool_name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                render_tool_call(self.console, tool_name, args)

                # Confirmation check
                needs_confirm = (
                    tool_name in DESTRUCTIVE_TOOLS
                    and not self.auto_execute
                )
                if needs_confirm:
                    approved = confirm_tool_execution(self.console, tool_name)
                    if not approved:
                        result = f"Tool '{tool_name}' was cancelled by the user."
                        conversation.add_tool_result(tool_id, result)
                        render_tool_result(self.console, tool_name, result)
                        continue

                # Execute tool
                handler = self.registry.get_handler(tool_name)
                if handler is None:
                    result = f"Error: tool '{tool_name}' not found in registry."
                else:
                    try:
                        result = handler(**args)
                        if not isinstance(result, str):
                            result = json.dumps(result)
                    except Exception as e:
                        result = f"Error executing {tool_name}: {e}"

                render_tool_result(self.console, tool_name, result)
                conversation.add_tool_result(tool_id, result)

        return "Max iterations reached. Task may be incomplete."