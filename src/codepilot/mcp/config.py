"""
mcp/config.py — Load MCP server definitions from configs/mcp_servers.json.
"""

import json
import os
from pathlib import Path
from src.codepilot import config


def load_mcp_servers() -> list[dict]:
    """Load and return MCP server configs."""
    path = Path(config.MCP_CONFIG_PATH)
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    servers = data.get("servers", [])

    # Expand env vars in the env block of each server
    for server in servers:
        env = server.get("env", {})
        expanded = {}
        for k, v in env.items():
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                var_name = v[2:-1]
                expanded[k] = os.getenv(var_name, "")
            else:
                expanded[k] = v
        server["env"] = expanded

    return servers