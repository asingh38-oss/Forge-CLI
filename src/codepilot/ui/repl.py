"""
ui/repl.py — Interactive terminal REPL for Forge.
Handles user input, slash commands, and routes tasks to the agent loop.
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console

from src.codepilot.core.agent_loop import AgentLoop
from src.codepilot.core.conversation import Conversation
from src.codepilot.core.tool_registry import ToolRegistry
from src.codepilot.ui.renderer import (
    render_banner,
    render_info,
    render_error,
    render_model_switch,
)
from src.codepilot import config

PROMPT_STYLE = Style.from_dict({
    "prompt": "bold ansicyan",
})

SYSTEM_PROMPT = """You are Forge, an autonomous CLI coding assistant.

Given a task, you reason about the codebase and autonomously:
- Read files to understand context
- Write and edit files to implement changes
- Run shell commands to test and verify your work
- Search through codebases using grep and glob
- Look up documentation using MCP servers

Keep going until the task is fully complete. Be thorough and precise.
Always read relevant files before making changes.
Show your reasoning briefly before taking action.
"""


class REPL:
    """Interactive REPL for Forge."""

    def __init__(
        self,
        provider,
        registry: ToolRegistry,
        console: Console,
        auto_execute: bool = False,
    ):
        self.provider     = provider
        self.registry     = registry
        self.console      = console
        self.auto_execute = auto_execute
        self.conversation = Conversation(system_prompt=SYSTEM_PROMPT)
        self.agent        = AgentLoop(
            provider=provider,
            registry=registry,
            console=console,
            auto_execute=auto_execute,
        )
        self._session = PromptSession(
            history=FileHistory(".forge_history"),
            style=PROMPT_STYLE,
        )

    def _handle_slash_command(self, cmd: str, provider_ref: list) -> bool:
        """
        Handle slash commands. Returns True if handled, False otherwise.
        provider_ref is a mutable list so we can swap the provider.
        """
        parts = cmd.strip().split()
        command = parts[0].lower()

        if command == "/help":
            self.console.print("""
[bold cyan]Forge — Slash Commands[/]

  [yellow]/help[/]                    Show this help message
  [yellow]/tools[/]                   List all available tools
  [yellow]/model <provider> <model>[/] Switch LLM provider and model
                           e.g. /model ollama qwen2.5:7b
                           e.g. /model openai gpt-4o
  [yellow]/auto[/]                    Toggle auto-execute mode
  [yellow]/clear[/]                   Clear conversation history
  [yellow]/quit[/]                    Exit Forge
""")
            return True

        elif command == "/tools":
            tools = self.registry.list_tools()
            self.console.print(f"\n[bold cyan]Available Tools ({len(tools)}):[/]")
            for t in tools:
                self.console.print(f"  [yellow]•[/] {t}")
            self.console.print()
            return True

        elif command == "/model":
            if len(parts) < 3:
                render_error(self.console, "Usage", "/model <provider> <model>")
                return True
            p_name = parts[1].lower()
            m_name = parts[2]
            try:
                if p_name == "openai":
                    from src.codepilot.providers.openai_provider import OpenAIProvider
                    new_provider = OpenAIProvider(model=m_name)
                elif p_name == "ollama":
                    from src.codepilot.providers.ollama_provider import OllamaProvider
                    new_provider = OllamaProvider(model=m_name)
                else:
                    render_error(self.console, "Unknown provider", f"'{p_name}' — use openai or ollama")
                    return True
                provider_ref[0] = new_provider
                self.agent.provider = new_provider
                render_model_switch(self.console, p_name, m_name)
            except Exception as e:
                render_error(self.console, "Model switch failed", str(e))
            return True

        elif command == "/auto":
            self.auto_execute = not self.auto_execute
            self.agent.auto_execute = self.auto_execute
            state = "[green]ON[/]" if self.auto_execute else "[red]OFF[/]"
            render_info(self.console, f"Auto-execute mode: {state}")
            return True

        elif command == "/clear":
            self.conversation.clear()
            render_info(self.console, "Conversation history cleared.")
            return True

        elif command in ("/quit", "/exit", "/q"):
            raise KeyboardInterrupt

        return False

    def run(self):
        """Start the REPL loop."""
        render_banner(self.console)

        auto_state = "[green]ON[/]" if self.auto_execute else "[red]OFF[/]"
        render_info(
            self.console,
            f"Provider: [yellow]{self.provider.model_name}[/] | "
            f"Auto-execute: {auto_state} | "
            f"Type [yellow]/help[/] for commands"
        )
        self.console.print()

        provider_ref = [self.provider]

        while True:
            try:
                user_input = self._session.prompt("forge> ", style=PROMPT_STYLE)
            except (KeyboardInterrupt, EOFError):
                self.console.print("\n[dim]Goodbye.[/]")
                break

            user_input = user_input.strip()
            if not user_input:
                continue

            # Slash commands
            if user_input.startswith("/"):
                try:
                    self._handle_slash_command(user_input, provider_ref)
                except KeyboardInterrupt:
                    self.console.print("\n[dim]Goodbye.[/]")
                    break
                continue

            # Regular task — run agentic loop
            try:
                self.agent.run(user_input, self.conversation)
            except KeyboardInterrupt:
                render_info(self.console, "Task interrupted.")
            except Exception as e:
                render_error(self.console, "Agent error", str(e))