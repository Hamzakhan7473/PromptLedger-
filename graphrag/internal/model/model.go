// Package model holds core GraphRAG domain types (Edge et al., Microsoft GraphRAG).
package model

import "time"

// Document is a source unit (file, page range, etc.).
type Document struct {
	ID        string
	Title     string
	Text      string
	CreatedAt time.Time
}

// Chunk is a text slice used for local extraction and attribution.
type Chunk struct {
	ID         string
	DocumentID string
	Index      int
	Text       string
}

// Entity is a node in the knowledge graph.
type Entity struct {
	ID   string
	Name string
	Type string
}

// Relationship is a directed typed edge between entities.
type Relationship struct {
	ID         string
	SourceID   string
	TargetID   string
	Kind       string
	Evidence   string // short provenance string (e.g. chunk id)
	Confidence float64
}

// Community groups tightly related entities (cluster in the MS pipeline).
type Community struct {
	ID        string
	Level     int // 0 = base community; higher = hierarchical (optional extension)
	MemberIDs []string
	Summary   string // pregenerated community summary
}

// IndexArtifacts is the serialized graph index used at query time.
type IndexArtifacts struct {
	Chunks        []Chunk
	Entities      []Entity
	Relationships []Relationship
	Communities   []Community
}
