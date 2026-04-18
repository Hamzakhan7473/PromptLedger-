package index

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"promptledger/graphrag/internal/graphx"
	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
)

// Indexer builds GraphRAG artifacts: chunks → entities/edges → communities → summaries.
type Indexer struct {
	Completer  llm.Completer
	ChunkRunes int // 0 means default (800)
}

func chunkDocument(doc model.Document, maxRunes int) []model.Chunk {
	if maxRunes <= 0 {
		maxRunes = 800
	}
	var out []model.Chunk
	runes := []rune(doc.Text)
	for i, start := 0, 0; start < len(runes); i++ {
		end := start + maxRunes
		if end > len(runes) {
			end = len(runes)
		}
		chunkText := strings.TrimSpace(string(runes[start:end]))
		if chunkText == "" {
			break
		}
		out = append(out, model.Chunk{
			ID:         fmt.Sprintf("%s#%d", doc.ID, i),
			DocumentID: doc.ID,
			Index:      i,
			Text:       chunkText,
		})
		if end == len(runes) {
			break
		}
		start = end
	}
	return out
}

type extractPayload struct {
	Entities []struct {
		Name string `json:"name"`
		Type string `json:"type"`
	} `json:"entities"`
	Relationships []struct {
		Source string `json:"source"`
		Target string `json:"target"`
		Kind   string `json:"kind"`
	} `json:"relationships"`
}

func (ix Indexer) extract(ctx context.Context, ch model.Chunk) (*extractPayload, error) {
	system := `Return only a JSON object with keys "entities" and "relationships".
entities: [{"name":string,"type":string},...]
relationships: [{"source":string,"target":string,"kind":string},...]
Use empty arrays if none. No markdown or commentary.`
	user := "Text:\n" + ch.Text
	raw, err := ix.Completer.Complete(ctx, system, user)
	if err != nil {
		return nil, err
	}
	raw = llm.TrimJSONFences(raw)
	var p extractPayload
	if err := json.Unmarshal([]byte(raw), &p); err != nil {
		return nil, fmt.Errorf("chunk %s: decode extract JSON: %w", ch.ID, err)
	}
	return &p, nil
}

// Build runs the full offline index pipeline.
func (ix Indexer) Build(ctx context.Context, docs []model.Document) (*model.IndexArtifacts, error) {
	if ix.Completer == nil {
		return nil, fmt.Errorf("completer is required")
	}
	cr := ix.ChunkRunes
	if cr <= 0 {
		cr = 800
	}
	var chunks []model.Chunk
	for _, d := range docs {
		chunks = append(chunks, chunkDocument(d, cr)...)
	}

	entityByName := map[string]string{}
	var entities []model.Entity
	var rels []model.Relationship
	entityIDsByChunk := map[string][]string{}

	mkEntityID := func(name, typ string) string {
		name = strings.TrimSpace(name)
		if id, ok := entityByName[name]; ok {
			return id
		}
		if strings.TrimSpace(typ) == "" {
			typ = "Concept"
		}
		id := fmt.Sprintf("e%d", len(entityByName)+1)
		entityByName[name] = id
		entities = append(entities, model.Entity{ID: id, Name: name, Type: typ})
		return id
	}

	for _, ch := range chunks {
		ext, err := ix.extract(ctx, ch)
		if err != nil {
			return nil, err
		}
		var ids []string
		for _, e := range ext.Entities {
			id := mkEntityID(e.Name, e.Type)
			ids = append(ids, id)
		}
		entityIDsByChunk[ch.ID] = uniqueStrings(ids)

		for _, r := range ext.Relationships {
			sid := mkEntityID(r.Source, "")
			tid := mkEntityID(r.Target, "")
			rels = append(rels, model.Relationship{
				ID:         fmt.Sprintf("r%d", len(rels)+1),
				SourceID:   sid,
				TargetID:   tid,
				Kind:       r.Kind,
				Evidence:   ch.ID,
				Confidence: 0.7,
			})
		}
	}

	g := graphx.CooccurrenceGraph(entityIDsByChunk)
	comps := g.ConnectedComponents()

	var communities []model.Community
	for i, comp := range comps {
		// Collect chunk text touching these entities
		set := map[string]struct{}{}
		for _, id := range comp {
			set[id] = struct{}{}
		}
		var buf strings.Builder
		for _, ch := range chunks {
			ids := entityIDsByChunk[ch.ID]
			if !intersects(set, ids) {
				continue
			}
			buf.WriteString(ch.Text)
			buf.WriteString("\n")
		}
		sys := "Summarize the following text for a community of related entities. Be concise."
		sum, err := ix.Completer.Complete(ctx, sys, buf.String())
		if err != nil {
			return nil, err
		}
		communities = append(communities, model.Community{
			ID:        fmt.Sprintf("c%d", i),
			Level:     0,
			MemberIDs: append([]string(nil), comp...),
			Summary:   strings.TrimSpace(sum),
		})
	}

	sort.Slice(entities, func(i, j int) bool { return entities[i].ID < entities[j].ID })
	return &model.IndexArtifacts{
		Chunks:        chunks,
		Entities:      entities,
		Relationships: rels,
		Communities:   communities,
	}, nil
}

func intersects(entitySet map[string]struct{}, chunkEntityIDs []string) bool {
	for _, id := range chunkEntityIDs {
		if _, ok := entitySet[id]; ok {
			return true
		}
	}
	return false
}

func uniqueStrings(in []string) []string {
	seen := map[string]struct{}{}
	var out []string
	for _, s := range in {
		s = strings.TrimSpace(s)
		if s == "" {
			continue
		}
		if _, ok := seen[s]; ok {
			continue
		}
		seen[s] = struct{}{}
		out = append(out, s)
	}
	sort.Strings(out)
	return out
}
