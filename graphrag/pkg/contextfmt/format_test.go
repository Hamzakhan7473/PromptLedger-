package contextfmt

import (
	"strings"
	"testing"

	"promptledger/graphrag/internal/model"
)

func TestForPromptIncludesCommunityID(t *testing.T) {
	art := &model.IndexArtifacts{
		Communities: []model.Community{
			{ID: "c0", Summary: "GraphRAG indexing themes.", MemberIDs: []string{"e1"}},
		},
		Entities: []model.Entity{{ID: "e1", Name: "GraphRAG", Type: "Concept"}},
	}
	out := ForPrompt(art, "What about GraphRAG?")
	if !strings.Contains(out, "[c0]") {
		t.Fatalf("missing community marker: %q", out)
	}
	if !strings.Contains(out, "GraphRAG") {
		t.Fatalf("missing summary text: %q", out)
	}
}
