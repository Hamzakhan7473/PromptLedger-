# GraphRAG (Go)

This module implements a **local → global** retrieval workflow aligned with Microsoft’s GraphRAG idea: build an entity graph from text, cluster entities into **communities**, precompute **community summaries**, then answer **global** questions by generating partial answers per community and consolidating them ([Microsoft Research publication](https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/)).

**Note on arXiv:** [arXiv:2407.01219](https://arxiv.org/abs/2407.01219) is a different paper (“Searching for Best Practices in Retrieval-Augmented Generation”). If you want the GraphRAG manuscript PDF, use the Microsoft page above or the official GraphRAG project materials.

## Run

```bash
cd graphrag
go test ./...
go run ./cmd/graphrag
go run ./cmd/graphrag -index-text ./sample.txt -question "What are the main themes?"
```

The default `llm.StubCompleter` is deterministic and requires no API keys. Swap in your own `llm.Completer` for production (OpenAI-compatible HTTP, Azure OpenAI, etc.).

## Pipeline

1. **Chunk** documents.
2. **Extract** entities/relationships (JSON contract) via the `Completer`.
3. **Graph**: link entities that co-occur in the same chunk.
4. **Communities**: connected components (swap for Leiden/Louvain later).
5. **Summarize** each community into a cached summary.
6. **Query (global)**: partial answers from relevant communities → final consolidated answer.
