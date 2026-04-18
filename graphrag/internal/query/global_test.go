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
		Entities: []model.Entity{
			{ID: "e1", Name: "GraphRAG", Type: "Concept"},
			{ID: "e2", Name: "Microsoft", Type: "Org"},
		},
		Communities: []model.Community{
			{ID: "c0", Summary: "Theme A: GraphRAG indexing.", MemberIDs: []string{"e1"}},
			{ID: "c1", Summary: "Theme B: unrelated cooking recipes.", MemberIDs: []string{"e2"}},
		},
	}
	e := Engine{Completer: llm.StubCompleter{}}
	ans, err := e.Global(ctx, "What are the main themes about GraphRAG?", idx)
	if err != nil {
		t.Fatal(err)
	}
	if ans.Final == "" {
		t.Fatal("expected final")
	}
}

func TestSelectCommunitiesKeywordOverlap(t *testing.T) {
	idx := &model.IndexArtifacts{
		Entities: []model.Entity{
			{ID: "e1", Name: "GraphRAG", Type: "Concept"},
			{ID: "e2", Name: "Cooking", Type: "Topic"},
		},
		Communities: []model.Community{
			{ID: "c0", Summary: "GraphRAG and retrieval.", MemberIDs: []string{"e1"}},
			{ID: "c1", Summary: "Cooking pasta.", MemberIDs: []string{"e2"}},
		},
	}
	names := entityNames(idx)
	out := selectCommunities("Tell me about GraphRAG retrieval", idx, names)
	if len(out) != 1 || out[0].ID != "c0" {
		t.Fatalf("got %+v", out)
	}
}
