"""
mcp/tool_adapter.py — Wraps MCP tools as callable handlers
so they plug into the ToolRegistry like built-in tools.
"""

from src.codepilot.mcp.client import MCPClientManager


def make_mcp_handler(manager: MCPClientManager, full_tool_name: str):
    """
    Return a callable that routes tool calls to the correct MCP server.
    """
    def handler(**kwargs) -> str:
        return manager.call_tool_sync(full_tool_name, kwargs)
    handler.__name__ = full_tool_name
    return handler