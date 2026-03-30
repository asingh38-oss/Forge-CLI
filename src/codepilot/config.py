"""
config.py — Forge configuration loaded from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# LLM providers
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str   = os.getenv("OPENAI_MODEL", "gpt-4o")
OLLAMA_MODEL: str   = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Default provider — "openai" or "ollama"
DEFAULT_PROVIDER: str = os.getenv("FORGE_PROVIDER", "openai")

# Agentic loop
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "25"))
AUTO_EXECUTE: bool  = os.getenv("AUTO_EXECUTE", "false").lower() == "true"

# RAG server
CHROMA_DIR: str     = os.getenv("CHROMA_DIR", "./data/chroma")
RAG_DOCS_DIR: str   = os.getenv("RAG_DOCS_DIR", "./data/docs")

# MCP config file
MCP_CONFIG_PATH: str = os.getenv("MCP_CONFIG_PATH", "./configs/mcp_servers.json")