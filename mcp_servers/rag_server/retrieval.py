"""
mcp_servers/rag_server/retrieval.py
-------------------------------------
HyDE-enhanced retrieval from ChromaDB.
"""

import os
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from mcp_servers.rag_server.hyde import hyde_embed, embed_text

CHROMA_DIR  = os.getenv("CHROMA_DIR", "./data/chroma")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def _get_collection():
    fn = OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBED_MODEL,
    )
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(
        name="docs",
        embedding_function=fn,
        metadata={"hnsw:space": "cosine"},
    )


def search(query: str, top_k: int = 5, use_hyde: bool = True) -> list[dict]:
    """
    Search the vector store for chunks relevant to the query.

    If use_hyde=True, uses HyDE to generate a hypothetical document
    and embeds that instead of the raw query — improves retrieval quality.
    """
    collection = _get_collection()

    if collection.count() == 0:
        return [{"content": "No documents indexed yet.", "source": "none", "score": 0.0}]

    if use_hyde:
        query_embedding, hyp_doc = hyde_embed(query)
    else:
        from mcp_servers.rag_server.hyde import embed_text
        query_embedding = embed_text(query)
        hyp_doc = query

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    for doc, meta, dist in zip(docs, metas, distances):
        chunks.append({
            "content":  doc,
            "source":   meta.get("source", "unknown"),
            "chunk":    meta.get("chunk_index", 0),
            "score":    round(1 - dist, 4),  # convert distance to similarity
            "hyde_doc": hyp_doc if use_hyde else None,
        })

    return chunks


def format_results(chunks: list[dict]) -> str:
    """Format retrieved chunks as a readable string for the LLM context."""
    if not chunks:
        return "No relevant documentation found."

    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(
            f"[Chunk {i} | Source: {chunk['source']} | Score: {chunk['score']}]\n"
            f"{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)