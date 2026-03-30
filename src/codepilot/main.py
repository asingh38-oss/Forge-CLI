"""
main.py — Forge entry point.
Initializes provider, tools, MCP servers, and starts the REPL.
"""

import sys
from rich.console import Console

from src.codepilot import config
from src.codepilot.core.tool_registry import ToolRegistry
from src.codepilot.ui.renderer import render_info, render_error
from src.codepilot.ui.repl import REPL

# Built-in tools
from src.codepilot.tools.file_read    import SCHEMA as READ_SCHEMA,   read_file
from src.codepilot.tools.file_write   import SCHEMA as WRITE_SCHEMA,  write_file
from src.codepilot.tools.file_edit    import SCHEMA as EDIT_SCHEMA,   edit_file
from src.codepilot.tools.shell        import SCHEMA as SHELL_SCHEMA,  run_shell
from src.codepilot.tools.grep_search  import SCHEMA as GREP_SCHEMA,   grep_search
from src.codepilot.tools.glob_search  import SCHEMA as GLOB_SCHEMA,   glob_search


def build_provider(name: str = ""):
    """Instantiate the LLM provider based on config or CLI arg."""
    p = name or config.DEFAULT_PROVIDER
    if p == "ollama":
        from src.codepilot.providers.ollama_provider import OllamaProvider
        return OllamaProvider()
    else:
        from src.codepilot.providers.openai_provider import OpenAIProvider
        return OpenAIProvider()


def build_registry(console: Console) -> ToolRegistry:
    """Register all built-in tools and MCP tools."""
    registry = ToolRegistry()

    # Built-in tools
    registry.register(READ_SCHEMA,  read_file)
    registry.register(WRITE_SCHEMA, write_file)
    registry.register(EDIT_SCHEMA,  edit_file)
    registry.register(SHELL_SCHEMA, run_shell)
    registry.register(GREP_SCHEMA,  grep_search)
    registry.register(GLOB_SCHEMA,  glob_search)

    render_info(console, f"Loaded {len(registry.list_tools())} built-in tools.")

    # MCP tools
    try:
        from src.codepilot.mcp.client import MCPClientManager
        from src.codepilot.mcp.tool_adapter import make_mcp_handler

        manager = MCPClientManager()
        mcp_schemas = manager.load_tools_sync()

        for schema in mcp_schemas:
            full_name = schema["function"]["name"]
            handler   = make_mcp_handler(manager, full_name)
            # Strip internal MCP metadata before registering
            clean_schema = {
                "type": schema["type"],
                "function": schema["function"],
            }
            registry.register(clean_schema, handler)

        render_info(console, f"Loaded {len(mcp_schemas)} MCP tools.")
    except Exception as e:
        render_error(console, "MCP load failed", str(e))
        render_info(console, "Continuing without MCP tools.")

    return registry


def main():
    console = Console()

    # Parse simple CLI args: forge [provider]
    provider_name = sys.argv[1] if len(sys.argv) > 1 else ""
    auto_execute  = "--auto" in sys.argv

    try:
        provider = build_provider(provider_name)
    except Exception as e:
        render_error(console, "Provider init failed", str(e))
        sys.exit(1)

    registry = build_registry(console)

    repl = REPL(
        provider=provider,
        registry=registry,
        console=console,
        auto_execute=auto_execute,
    )
    repl.run()


if __name__ == "__main__":
    main()