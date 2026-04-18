// Package model holds core GraphRAG domain types (Edge et al., Microsoft GraphRAG).
package model

import "time"

// Document is a source unit (file, page range, etc.).
type Document struct {
	ID        string    `json:"id"`
	Title     string    `json:"title,omitempty"`
	Text      string    `json:"text"`
	CreatedAt time.Time `json:"created_at"`
}

// Chunk is a text slice used for local extraction and attribution.
type Chunk struct {
	ID         string `json:"id"`
	DocumentID string `json:"document_id"`
	Index      int    `json:"index"`
	Text       string `json:"text"`
}

// Entity is a node in the knowledge graph.
type Entity struct {
	ID   string `json:"id"`
	Name string `json:"name"`
	Type string `json:"type"`
}

// Relationship is a directed typed edge between entities.
type Relationship struct {
	ID         string  `json:"id"`
	SourceID   string  `json:"source_id"`
	TargetID   string  `json:"target_id"`
	Kind       string  `json:"kind"`
	Evidence   string  `json:"evidence,omitempty"`
	Confidence float64 `json:"confidence"`
}

// Community groups tightly related entities (cluster in the MS pipeline).
type Community struct {
	ID        string   `json:"id"`
	Level     int      `json:"level"` // 0 = base community; higher = hierarchical (optional extension)
	MemberIDs []string `json:"member_ids"`
	Summary   string   `json:"summary"` // pregenerated community summary
}

// IndexArtifacts is the serialized graph index used at query time.
type IndexArtifacts struct {
	Chunks        []Chunk        `json:"chunks"`
	Entities      []Entity       `json:"entities"`
	Relationships []Relationship `json:"relationships"`
	Communities   []Community    `json:"communities"`
}
