"""
mcp_servers/rag_server/ingestion.py
------------------------------------
Load documents, chunk them, embed, and store in ChromaDB.
Run this once to build the vector database before using the assistant.
"""
from dotenv import load_dotenv
load_dotenv()

import hashlib
import os
import re
from pathlib import Path
from typing import Literal

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHROMA_DIR     = os.getenv("CHROMA_DIR", "./data/chroma")
EMBED_MODEL    = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHUNK_SIZE     = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP  = int(os.getenv("CHUNK_OVERLAP", "150"))

ChunkStrategy = Literal["fixed", "sentence", "recursive"]


# ---------------------------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------------------------

def _embedding_fn():
    return OpenAIEmbeddingFunction(
        api_key=OPENAI_API_KEY,
        model_name=EMBED_MODEL,
    )


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(
        name="docs",
        embedding_function=_embedding_fn(),
        metadata={"hnsw:space": "cosine"},
    )


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text(file_path: str) -> str:
    """Extract text from PDF, PPTX, TXT, or MD files."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        import pdfplumber
        texts = []
        with pdfplumber.open(str(path)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)
        return "\n\n".join(texts)

    elif suffix in (".txt", ".md", ".py", ".js", ".ts", ".json"):
        return path.read_text(encoding="utf-8", errors="ignore")

    else:
        return path.read_text(encoding="utf-8", errors="ignore")


# ---------------------------------------------------------------------------
# Chunking strategies
# ---------------------------------------------------------------------------

def _recursive_chunks(text: str) -> list[str]:
    """
    Recursive character splitter — tries paragraph → sentence → word.
    This is the advanced RAG chunking technique used by this server.
    Produces semantically coherent chunks better suited for embedding.
    """
    separators = ["\n\n", "\n", ". ", " ", ""]

    def _split(t: str, seps: list[str]) -> list[str]:
        if len(t) <= CHUNK_SIZE:
            return [t] if t.strip() else []
        if not seps:
            # Hard split as last resort
            chunks, start = [], 0
            while start < len(t):
                chunks.append(t[start: start + CHUNK_SIZE])
                start += CHUNK_SIZE - CHUNK_OVERLAP
            return chunks
        sep = seps[0]
        parts = t.split(sep)
        result, current = [], ""
        for part in parts:
            candidate = current + (sep if current else "") + part
            if len(candidate) <= CHUNK_SIZE:
                current = candidate
            else:
                if current:
                    result.extend(_split(current, seps[1:]))
                current = part
        if current:
            result.extend(_split(current, seps[1:]))
        return result

    raw = _split(text, separators)

    # Add overlap between adjacent chunks
    overlapped = []
    for i, chunk in enumerate(raw):
        if i > 0 and CHUNK_OVERLAP > 0:
            chunk = raw[i - 1][-CHUNK_OVERLAP:] + " " + chunk
        overlapped.append(chunk.strip())
    return [c for c in overlapped if c]


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------

def ingest_file(file_path: str) -> dict:
    """Ingest a single file into ChromaDB. Returns stats."""
    text = extract_text(file_path)
    if not text.strip():
        return {"source": file_path, "chunks": 0, "status": "empty"}

    chunks = _recursive_chunks(text)
    source_name = Path(file_path).name

    ids, documents, metadatas = [], [], []
    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.md5(
            f"{source_name}_{i}_{chunk[:40]}".encode()
        ).hexdigest()
        ids.append(chunk_id)
        documents.append(chunk)
        metadatas.append({
            "source": source_name,
            "chunk_index": i,
            "total_chunks": len(chunks),
        })

    collection = get_collection()
    for start in range(0, len(ids), 100):
        collection.upsert(
            ids=ids[start: start + 100],
            documents=documents[start: start + 100],
            metadatas=metadatas[start: start + 100],
        )

    return {"source": source_name, "chunks": len(chunks), "status": "ok"}


def ingest_directory(docs_dir: str) -> list[dict]:
    """Ingest all supported files in a directory."""
    root = Path(docs_dir)
    if not root.exists():
        return [{"error": f"Directory not found: {docs_dir}"}]

    results = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in (
            ".pdf", ".txt", ".md", ".py", ".js", ".ts", ".json"
        ):
            try:
                result = ingest_file(str(path))
                results.append(result)
                print(f"[RAG] Ingested {result['source']} — {result['chunks']} chunks")
            except Exception as e:
                print(f"[RAG] Error on {path}: {e}")
                results.append({"source": str(path), "error": str(e)})
    return results


if __name__ == "__main__":
    import sys
    docs_dir = sys.argv[1] if len(sys.argv) > 1 else os.getenv("RAG_DOCS_DIR", "./data/docs")
    print(f"[RAG] Ingesting from: {docs_dir}")
    results = ingest_directory(docs_dir)
    ok = sum(1 for r in results if r.get("status") == "ok")
    print(f"[RAG] Done — {ok}/{len(results)} files ingested successfully.")