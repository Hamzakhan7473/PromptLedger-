package llm

import (
	"context"
	"encoding/json"
	"strings"
)

// StubCompleter is deterministic and offline-friendly for CI/tests.
// It extracts capitalized tokens as "entities" and emits a trivial community summary.
type StubCompleter struct{}

func (StubCompleter) Complete(_ context.Context, system, user string) (string, error) {
	ls := strings.ToLower(system)
	// Entity extraction contract: return JSON for index pipeline (matches indexer prompt).
	if strings.Contains(ls, "entities") && strings.Contains(ls, "relationships") {
		words := strings.Fields(user)
		var names []string
		seen := map[string]struct{}{}
		for _, w := range words {
			w = strings.Trim(w, ".,;:\"'()[]{}")
			if len(w) < 3 {
				continue
			}
			if w[0] < 'A' || w[0] > 'Z' {
				continue
			}
			if _, ok := seen[w]; ok {
				continue
			}
			seen[w] = struct{}{}
			names = append(names, w)
			if len(names) >= 12 {
				break
			}
		}
		type ent struct {
			Name string `json:"name"`
			Type string `json:"type"`
		}
		type rel struct {
			Source string `json:"source"`
			Target string `json:"target"`
			Kind   string `json:"kind"`
		}
		var entities []ent
		for _, n := range names {
			entities = append(entities, ent{Name: n, Type: "Concept"})
		}
		var rels []rel
		for i := 0; i < len(names)-1; i++ {
			rels = append(rels, rel{Source: names[i], Target: names[i+1], Kind: "related_to"})
		}
		payload := map[string]any{
			"entities":      entities,
			"relationships": rels,
		}
		b, err := json.Marshal(payload)
		return string(b), err
	}

	// Summaries / partial answers / final answers: echo mode.
	if strings.Contains(ls, "summarize") {
		return "Community summary: key entities include " + shorten(user, 200), nil
	}
	if strings.Contains(ls, "partial") || strings.Contains(ls, "only the community") || strings.Contains(ls, "answer the user question") {
		return "Partial answer: " + shorten(user, 240), nil
	}
	return "Final answer: " + shorten(user, 800), nil
}

func shorten(s string, n int) string {
	s = strings.Join(strings.Fields(s), " ")
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}
