package persist

import (
	"testing"
	"time"

	"promptledger/graphrag/internal/model"
)

func TestValidateOK(t *testing.T) {
	art := &model.IndexArtifacts{
		Meta:     model.IndexMeta{Version: "1", CreatedAt: time.Now()},
		Chunks:   []model.Chunk{{ID: "d#0", DocumentID: "d", Text: "x"}},
		Entities: []model.Entity{{ID: "e1", Name: "A", Type: "T"}},
		Communities: []model.Community{
			{ID: "c0", Summary: "theme", MemberIDs: []string{"e1"}},
		},
	}
	if issues := Validate(art); len(issues) != 0 {
		t.Fatal(issues)
	}
}
