# GraphRAG (Go)

This module implements a **local → global** retrieval workflow aligned with Microsoft’s GraphRAG idea: build an entity graph from text, cluster entities into **communities**, precompute **community summaries**, then answer **global** questions by generating partial answers per community and consolidating them ([Microsoft Research publication](https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/)).

**Note on arXiv:** [arXiv:2407.01219](https://arxiv.org/abs/2407.01219) is a different paper (“Searching for Best Practices in Retrieval-Augmented Generation”). If you want the GraphRAG manuscript PDF, use the Microsoft page above or the official GraphRAG project materials.

## CLI

```bash
cd graphrag
go test ./...

# Offline demo (always stub LLM)
go run ./cmd/graphrag demo -question "What are the main themes in this corpus?"

# Build a persisted index from a text file
go run ./cmd/graphrag index -text ./your.txt -o /tmp/index.json

# Query a saved index (uses OPENAI_API_KEY if set; otherwise stub)
go run ./cmd/graphrag query -index /tmp/index.json -question "What are the main themes?"
```

Force the deterministic stub (CI / no network):

```bash
go run ./cmd/graphrag index -text ./your.txt -o /tmp/index.json -stub
go run ./cmd/graphrag query -index /tmp/index.json -question "..." -stub
```

## OpenAI-compatible LLM

If `OPENAI_API_KEY` is set, indexing and query use the Chat Completions API (`OPENAI_BASE_URL`, default `https://api.openai.com/v1`; `OPENAI_MODEL`, default `gpt-4o-mini`). Entity extraction uses `response_format: json_object` when supported.

## Pipeline

1. **Chunk** documents (`-chunk-runes` on `index`, default 800).
2. **Extract** entities/relationships (JSON contract) via the `Completer`; markdown code fences around JSON are stripped automatically.
3. **Graph**: link entities that co-occur in the same chunk.
4. **Communities**: connected components (swap for Leiden/Louvain later).
5. **Summarize** each community into a cached summary.
6. **Query (global)**: score communities by keyword overlap with the question (plus member entity names), take the top matches, partial answers → consolidated answer.

## Library

- `internal/persist` — save/load `IndexArtifacts` as JSON.
- `internal/llm` — `StubCompleter`, `OpenAIChat`, `CompleterFromEnv`.
