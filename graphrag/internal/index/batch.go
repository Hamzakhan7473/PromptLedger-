package index

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"promptledger/graphrag/internal/model"
)

// DocumentsFromDir loads .txt and .md files as documents (non-recursive).
func DocumentsFromDir(dir string) ([]model.Document, error) {
	entries, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}
	var docs []model.Document
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		name := e.Name()
		lower := strings.ToLower(name)
		if !strings.HasSuffix(lower, ".txt") && !strings.HasSuffix(lower, ".md") {
			continue
		}
		path := filepath.Join(dir, name)
		b, err := os.ReadFile(path)
		if err != nil {
			return nil, err
		}
		id := strings.TrimSuffix(name, filepath.Ext(name))
		docs = append(docs, model.Document{
			ID:        id,
			Title:     name,
			Text:      string(b),
			CreatedAt: time.Now().UTC(),
		})
	}
	if len(docs) == 0 {
		return nil, fmt.Errorf("no .txt or .md files in %s", dir)
	}
	return docs, nil
}
