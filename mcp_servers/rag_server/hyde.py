"""
mcp_servers/rag_server/hyde.py
--------------------------------
HyDE — Hypothetical Document Embeddings.

Advanced RAG technique:
  Instead of embedding the raw query, we ask the LLM to generate a
  hypothetical document that would answer the query, then embed THAT.
  The hypothetical document is semantically closer to real documentation
  in embedding space, producing better retrieval results.
"""

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")


def generate_hypothetical_document(query: str) -> str:
    """
    Ask GPT to write a hypothetical documentation passage that would
    answer the query. This is the core of HyDE.
    """
    prompt = (
        "Write a concise technical documentation passage that directly answers "
        "the following question. The passage should sound like real library "
        "documentation — include relevant APIs, methods, and a short example "
        "if appropriate. Focus on retrieval usefulness, not conversational tone.\n\n"
        f"Question: {query}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=400,
        )
        return response.choices[0].message.content or query
    except Exception:
        # Fall back to raw query if LLM call fails
        return query


def embed_text(text: str) -> list[float]:
    """Get the embedding vector for a text string."""
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=[text],
    )
    return response.data[0].embedding


def hyde_embed(query: str) -> tuple[list[float], str]:
    """
    Full HyDE pipeline:
    1. Generate hypothetical document from query
    2. Embed the hypothetical document
    Returns (embedding_vector, hypothetical_document)
    """
    hyp_doc = generate_hypothetical_document(query)
    embedding = embed_text(hyp_doc)
    return embedding, hyp_doc