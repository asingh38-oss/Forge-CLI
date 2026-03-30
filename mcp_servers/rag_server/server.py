"""
mcp_servers/rag_server/server.py
----------------------------------
FastMCP server exposing RAG tools to the Forge agent.

Tools:
  - search_docs(query, top_k)   — HyDE-enhanced search
  - ingest_document(file_path)  — ingest a single file
  - list_sources()              — list indexed sources
"""

import os
from mcp.server.fastmcp import FastMCP

from mcp_servers.rag_server.retrieval import search, format_results
from mcp_servers.rag_server.ingestion import ingest_file, get_collection

mcp = FastMCP("forge-rag")


@mcp.tool()
def search_docs(query: str, top_k: int = 5) -> str:
    """
    Search the documentation vector database using HyDE-enhanced retrieval.
    Returns the most relevant documentation chunks for the given query.
    Use this when you need to look up how a library or API works.
    """
    try:
        chunks = search(query, top_k=top_k, use_hyde=True)
        return format_results(chunks)
    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def ingest_document(file_path: str) -> str:
    """
    Ingest a document into the vector database.
    Supported formats: PDF, TXT, MD, PY, JS, TS, JSON.
    Only needs to be run once per document.
    """
    try:
        result = ingest_file(file_path)
        if result.get("status") == "ok":
            return (
                f"Ingested '{result['source']}' — "
                f"{result['chunks']} chunks added to vector DB."
            )
        return f"Warning: {result}"
    except Exception as e:
        return f"Ingest error: {e}"


@mcp.tool()
def list_sources() -> str:
    """
    List all document sources currently indexed in the vector database.
    """
    try:
        collection = get_collection()
        if collection.count() == 0:
            return "No documents indexed yet. Use ingest_document to add files."
        results = collection.get(include=["metadatas"])
        sources = sorted({m["source"] for m in results["metadatas"]})
        lines = [f"- {s}" for s in sources]
        return f"Indexed sources ({len(sources)}):\n" + "\n".join(lines)
    except Exception as e:
        return f"Error listing sources: {e}"


if __name__ == "__main__":
    print("[RAG Server] Starting Forge RAG MCP server...")
    mcp.run(transport="stdio")