# Forge — Autonomous CLI Coding Assistant

Forge is an AI-powered command-line coding assistant built for ITCS 4681 Senior Design at UNC Charlotte. You give it a task in plain English and it figures out what to do — reading files, making edits, running commands, and searching your codebase until the job is done.

---

## Features

- Autonomous agentic loop that works until the task is complete
- Reads, writes, and edits files on your local machine
- Runs shell commands to test and verify its own work
- Searches codebases with grep and glob
- Looks up library docs via MCP servers
- Supports OpenAI (GPT-4o) and local Ollama models
- Shows every tool call so you can see exactly what its doing

---

## Setup

### Requirements
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Install

```bash
git clone https://github.com/your-username/forge.git
cd forge
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -e .
```

### Configure

```bash
cp .env.example .env
```

Add your OpenAI key to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### Ingest docs for RAG (one time only)

```bash
mkdir -p data/docs
# drop any .txt .md .pdf .py files into data/docs
python mcp_servers/rag_server/ingestion.py data/docs
```

### Run

```bash
python -m src.codepilot.main
```

With Ollama:
```bash
python -m src.codepilot.main ollama
```

With auto-execute (skip confirmations):
```bash
python -m src.codepilot.main --auto
```

---

## Usage

```
forge> Read app.py and explain what it does
forge> Add input validation to the login function in auth.py
forge> Run the tests and fix whatever is failing
```

### Slash Commands

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/tools` | List all loaded tools |
| `/model openai gpt-4o` | Switch to GPT-4o |
| `/model ollama qwen2.5:7b` | Switch to local Ollama model |
| `/auto` | Toggle auto-execute mode |
| `/clear` | Clear conversation history |
| `/quit` | Exit |

---

## MCP Servers

**Filesystem** — direct file access on your machine

**Context7** — free library documentation lookup

**Custom RAG Server** — searches a local ChromaDB vector database using
HyDE (Hypothetical Document Embeddings). Instead of embedding the raw query,
it generates a hypothetical answer document first and embeds that, which gets
better retrieval results against real documentation chunks.

---

## Project Structure

```
forge/
├── src/codepilot/
│   ├── main.py
│   ├── config.py
│   ├── core/
│   │   ├── agent_loop.py
│   │   ├── conversation.py
│   │   └── tool_registry.py
│   ├── providers/
│   │   ├── openai_provider.py
│   │   └── ollama_provider.py
│   ├── tools/
│   │   ├── file_read.py
│   │   ├── file_write.py
│   │   ├── file_edit.py
│   │   ├── shell.py
│   │   ├── grep_search.py
│   │   └── glob_search.py
│   ├── mcp/
│   │   ├── client.py
│   │   ├── config.py
│   │   └── tool_adapter.py
│   └── ui/
│       ├── repl.py
│       └── renderer.py
├── mcp_servers/rag_server/
│   ├── server.py
│   ├── hyde.py
│   ├── ingestion.py
│   └── retrieval.py
├── configs/mcp_servers.json
├── data/docs/
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required. OpenAI API key |
| `FORGE_PROVIDER` | `openai` | `openai` or `ollama` |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model |
| `OLLAMA_MODEL` | `qwen2.5:7b` | Ollama model |
| `MAX_ITERATIONS` | `25` | Max loop iterations per task |
| `AUTO_EXECUTE` | `false` | Skip confirmation prompts |

---

## Advanced RAG — HyDE

The RAG server uses HyDE (Hypothetical Document Embeddings). Normal RAG embeds
the raw query which doesnt match well against longer documentation chunks.
HyDE fixes this by generating a hypothetical documentation passage first,
embedding that instead, and using it to search. Since the hypothetical passage
looks more like real docs, retrieval quality is noticeably better.

---

## Team

Built by [your team names] for ITCS 4681 Senior Design, Spring 2026.