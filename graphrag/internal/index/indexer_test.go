package index

import (
	"context"
	"testing"
	"time"

	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
)

func TestIndexerBuildStub(t *testing.T) {
	ctx := context.Background()
	ix := Indexer{Completer: llm.StubCompleter{}}
	docs := []model.Document{
		{
			ID:        "d1",
			Title:     "Demo",
			Text:      "GraphRAG combines Microsoft Research ideas with Query Focused Summarization. London and Paris are mentioned here.",
			CreatedAt: time.Unix(1, 0),
		},
	}
	art, err := ix.Build(ctx, docs)
	if err != nil {
		t.Fatal(err)
	}
	if len(art.Chunks) == 0 {
		t.Fatal("expected chunks")
	}
	if len(art.Entities) == 0 {
		t.Fatal("expected entities")
	}
	if len(art.Communities) == 0 {
		t.Fatal("expected communities")
	}
}
