package query

import (
	"context"
	"testing"

	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
)

func TestEngineGlobal(t *testing.T) {
	ctx := context.Background()
	idx := &model.IndexArtifacts{
		Communities: []model.Community{
			{ID: "c0", Summary: "Theme A details."},
			{ID: "c1", Summary: "Theme B details."},
		},
	}
	e := Engine{Completer: llm.StubCompleter{}}
	ans, err := e.Global(ctx, "What are the main themes in this dataset?", idx)
	if err != nil {
		t.Fatal(err)
	}
	if ans.Final == "" {
		t.Fatal("expected final")
	}
}
