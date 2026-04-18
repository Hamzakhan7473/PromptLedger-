package persist

import (
	"encoding/json"
	"fmt"
	"os"

	"promptledger/graphrag/internal/model"
)

// SaveJSON writes index artifacts as pretty-printed JSON.
func SaveJSON(path string, art *model.IndexArtifacts) error {
	if art == nil {
		return fmt.Errorf("nil artifacts")
	}
	b, err := json.MarshalIndent(art, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, b, 0o644)
}

// LoadJSON reads index artifacts from JSON.
func LoadJSON(path string) (*model.IndexArtifacts, error) {
	b, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	var art model.IndexArtifacts
	if err := json.Unmarshal(b, &art); err != nil {
		return nil, err
	}
	return &art, nil
}
