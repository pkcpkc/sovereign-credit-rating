# Humboldt Universität: High-Standard & Rich Sovereign Credit Rating

## System Overview

```mermaid
flowchart TD
    C[LLM-Compiler]
    P[Plugins]
    PC[Collections]
    PO[Overviews]
    PA[Applications]

    W[Wikis]

    A[SCR Agent]
    AO[Observability]
    AC[Capabilities]
    AS[Skills]
    AMCP[MCP]
    AG[I/O Guardrails and Caching]

    M[Methologies]
    MS[Methology Skills]
    MC[Methology MCP]

    subgraph Static Wikis
        W --- SCRW[Sovereign Credit Rating Wiki]
        W --- MW[Methology Wiki]
    end

    subgraph Sovereign Credit Rating Methologies
        M-- Execution Plan ---MS
        M-- Code ---MC
        MS-. references code tools .->MC
    end

    subgraph Compiler
        C-- extended by -->P
        P-->PC
        P-->PO
        P-->PA
        PA-- uses -->M
        C-- compiles -->W
    end

    subgraph Sovereign Credit Rating Agent
        AG ---> A
        AMCP--RAG via MCP-->W
        A---AO
        AO-.-RC[Recursive Crystallization\nSelf-Improvement]-.Human-in-the-Loop.->AC
        A---AC
        AC---AS
        AC---AMCP
        AC--uses-->M
        AO --- Monitoring
        AO --- Alarming
        AO --- Logging
        AO --- Tracing
        AO --- Analytics
    end

    User["fa:fa-user User"] -- prompts --> AG
    User -- browses --> W
```

## LLM Compiler

https://github.com/pkcpkc/mycelium-mind

### Switching between local and npmjs mycelium-mind

For development, you can toggle between using your local clone of `mycelium-mind` and the version published on npmjs:

- **Use local mycelium-mind:**

  ```bash
  # Ensure local changes are built in your mycelium-mind directory:
  # (In /Users/pkc/Projects/mycelium-mind): npm run build

  # Then in this repository:
  mise exec -- npm run link:local
  ```

- **Use published npmjs package:**
  ```bash
  mise exec -- npm run link:npm
  ```

## RAG

- Serves the LLM-Wiki content
- https://github.com/lyonzin/knowledge-rag via mycelium-mind
  - **Your docs, your machine, zero cloud.** Claude Code searches them natively.
    Drop your PDFs, markdown, code, notebooks — 1800+ files, 39K chunks, indexed in under 3 minutes.
    Hybrid search (BM25 + semantic vectors + cross-encoder reranking) through 13 MCP tools.
    Everything runs locally via ONNX. No Docker, no Ollama, no API keys, no data leaves your machine.
  - v4.0.0 — Enterprise concurrent access: **SSE/HTTP transport (1 server → N clients)**, thread-safe shared state, optional rate limiting + Prometheus metrics, ChromaDB WAL mode, --transport CLI

## MCP

- Provides access to financial data via DuckDB
- https://github.com/motherduckdb/mcp-server-motherduck
- Maybe a custom MCP, that returns all (or grouped) financial data of one country by country code would be more efficient in agentic use!

## Skills

- SVR methods

### Using with OpenCode

This repository includes a pre-configured `opencode.json` file that links the RAG command to **OpenCode** as a local MCP server.

When you launch OpenCode in this directory:

```bash
opencode
```

It automatically spawns the RAG server in `stdio` mode, indexes the files in the `wiki/` directory, and connects to the server tools (such as `search_knowledge`), making your offline wiki directly accessible inside the session.

## OpenAI API Settings

- https://ki.cms.hu-berlin.de/de/apis
  - llm3: Qwen/Qwen3.6-27B-FP8

## VPN Settings

https://www.cms.hu-berlin.de/de/dl/netze/vpn
