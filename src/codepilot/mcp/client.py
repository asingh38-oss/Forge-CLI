"""
mcp/client.py — MCP client manager.
Connects to MCP servers via stdio transport and loads their tools.
"""

import asyncio
import json
import os
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from src.codepilot.mcp.config import load_mcp_servers


class MCPClientManager:
    """
    Manages connections to multiple MCP servers.
    Loads tools from each server and provides a unified call interface.
    """

    def __init__(self):
        self._tools: list[dict] = []
        self._server_configs: list[dict] = []

    def load_tools_sync(self) -> list[dict]:
        """
        Synchronously load all tools from configured MCP servers.
        Returns list of OpenAI-compatible tool schemas.
        """
        servers = load_mcp_servers()
        all_tools = []

        for server in servers:
            try:
                tools = asyncio.run(self._load_server_tools(server))
                all_tools.extend(tools)
                self._server_configs.append(server)
            except Exception as e:
                print(f"[MCP] Failed to load server '{server.get('name')}': {e}")

        self._tools = all_tools
        return all_tools

    async def _load_server_tools(self, server: dict) -> list[dict]:
        """Connect to one MCP server and retrieve its tool list."""
        name    = server.get("name", "unknown")
        command = server.get("command", "")
        args    = server.get("args", [])
        env     = {**os.environ, **server.get("env", {})}

        params = StdioServerParameters(
            command=command,
            args=args,
            env=env,
        )

        tools = []
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                for tool in result.tools:
                    # Convert MCP tool schema to OpenAI format
                    schema = {
                        "type": "function",
                        "function": {
                            "name": f"{name}__{tool.name}",
                            "description": tool.description or "",
                            "parameters": tool.inputSchema or {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                        "_mcp_server": name,
                        "_mcp_tool": tool.name,
                    }
                    tools.append(schema)

        return tools

    def call_tool_sync(self, full_tool_name: str, args: dict) -> str:
        """
        Call an MCP tool by its full name (server__toolname).
        Returns the result as a string.
        """
        if "__" not in full_tool_name:
            return f"Error: invalid MCP tool name format: {full_tool_name}"

        server_name, tool_name = full_tool_name.split("__", 1)

        # Find server config
        server = next(
            (s for s in self._server_configs if s.get("name") == server_name),
            None,
        )
        if server is None:
            return f"Error: MCP server '{server_name}' not found."

        try:
            result = asyncio.run(self._call_tool(server, tool_name, args))
            return result
        except Exception as e:
            return f"Error calling MCP tool {full_tool_name}: {e}"

    async def _call_tool(self, server: dict, tool_name: str, args: dict) -> str:
        """Connect to an MCP server and call one tool."""
        command = server.get("command", "")
        s_args  = server.get("args", [])
        env     = {**os.environ, **server.get("env", {})}

        params = StdioServerParameters(
            command=command,
            args=s_args,
            env=env,
        )

        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, args)

                # Extract text content from result
                content = result.content
                if isinstance(content, list):
                    parts = []
                    for item in content:
                        if hasattr(item, "text"):
                            parts.append(item.text)
                        elif isinstance(item, dict):
                            parts.append(json.dumps(item))
                        else:
                            parts.append(str(item))
                    return "\n".join(parts)
                return str(content)