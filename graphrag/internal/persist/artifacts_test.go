package persist

import (
	"path/filepath"
	"testing"

	"promptledger/graphrag/internal/model"
)

func TestRoundTrip(t *testing.T) {
	dir := t.TempDir()
	p := filepath.Join(dir, "idx.json")
	art := &model.IndexArtifacts{
		Entities: []model.Entity{{ID: "e1", Name: "Acme", Type: "Org"}},
		Communities: []model.Community{
			{ID: "c0", Summary: "Acme contracts", MemberIDs: []string{"e1"}},
		},
	}
	if err := SaveJSON(p, art); err != nil {
		t.Fatal(err)
	}
	got, err := LoadJSON(p)
	if err != nil {
		t.Fatal(err)
	}
	if len(got.Entities) != 1 || got.Entities[0].Name != "Acme" {
		t.Fatalf("%+v", got.Entities)
	}
}
