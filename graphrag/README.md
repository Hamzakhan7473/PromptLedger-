# GraphRAG (Go)

Local → global GraphRAG pipeline: entity graph, **label-propagation** communities, optional **hierarchical** meta-summaries, persisted index JSON, REST API, and **PromptLedger**-compatible `{retrieved_context}` export ([Microsoft GraphRAG](https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/)).

## CLI

```bash
cd graphrag
go test ./...

# Index one file (default algo: labelprop)
go run ./cmd/graphrag index -text ../README.md -o /tmp/index.json -stub

# Batch index a directory of .txt/.md (default algo: hierarchical)
go run ./cmd/graphrag batch -dir ./docs -o /tmp/index.json -stub

# Global query
go run ./cmd/graphrag query -index /tmp/index.json -question "What are the main themes?" -stub

# Export context for PromptLedger scenarios / render --graphrag-index
go run ./cmd/graphrag context -index /tmp/index.json -question "legal risks"

# Validate index integrity
go run ./cmd/graphrag validate -index /tmp/index.json

# REST API: GET /health, GET /v1/context?question=..., POST /v1/query, GET /v1/index/meta
go run ./cmd/graphrag serve -index /tmp/index.json -addr :8080 -stub
```

### Community algorithms (`-algo`)

| Value | Behavior |
|--------|----------|
| `labelprop` | Weighted label propagation (default for `index`) |
| `hierarchical` | Label propagation + level-1 meta-community summaries |
| `components` | Connected components only (legacy MVP) |

## OpenAI

Set `OPENAI_API_KEY` (optional `OPENAI_BASE_URL`, `OPENAI_MODEL`) or pass `-stub` for offline CI.

## Public Go API

```go
import "promptledger/graphrag/pkg/graphrag"

svc, _ := graphrag.NewService(true)
art, _ := svc.BuildIndex(ctx, docs)
ctx := graphrag.ContextForPrompt(art, "your question")
_ = graphrag.SaveIndex("/tmp/index.json", art)
```

## PromptLedger integration

1. Build an index: `graphrag index` or `graphrag batch`
2. In scenario YAML: `graphrag_index: "path/to/index.json"` and optional `question: "..."`
3. Or: `prompt-ledger render -p legal.contract_review --graphrag-index path/to/index.json`

Python `prompt_ledger.graphrag_bridge` reads the same index JSON format as `graphrag context`.
