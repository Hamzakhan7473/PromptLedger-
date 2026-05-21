// Package graphrag is the public API for indexing and global query over private corpora.
package graphrag

import (
	"context"

	"promptledger/graphrag/internal/index"
	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
	"promptledger/graphrag/internal/persist"
	"promptledger/graphrag/internal/query"
	"promptledger/graphrag/pkg/contextfmt"
)

// Service orchestrates GraphRAG indexing and querying.
type Service struct {
	Indexer index.Indexer
	Query   query.Engine
}

// NewService builds a service from environment (OPENAI_API_KEY) or stub when forceStub is true.
func NewService(forceStub bool) (*Service, error) {
	c, _, err := llm.CompleterFromEnv(forceStub)
	if err != nil {
		return nil, err
	}
	return &Service{
		Indexer: index.Indexer{Completer: c, CommunityAlgo: index.AlgoLabelProp},
		Query:   query.Engine{Completer: c},
	}, nil
}

// BuildIndex runs the full pipeline on documents.
func (s *Service) BuildIndex(ctx context.Context, docs []model.Document) (*model.IndexArtifacts, error) {
	return s.Indexer.Build(ctx, docs)
}

// QueryGlobal answers a global sensemaking question over a built index.
func (s *Service) QueryGlobal(ctx context.Context, art *model.IndexArtifacts, question string) (*query.GlobalAnswer, error) {
	return s.Query.Global(ctx, question, art)
}

// ContextForPrompt formats retrieved context for PromptLedger {retrieved_context} substitution.
func ContextForPrompt(art *model.IndexArtifacts, question string) string {
	return contextfmt.ForPrompt(art, question)
}

// SaveIndex writes artifacts to JSON.
func SaveIndex(path string, art *model.IndexArtifacts) error {
	return persist.SaveJSON(path, art)
}

// LoadIndex reads artifacts from JSON.
func LoadIndex(path string) (*model.IndexArtifacts, error) {
	return persist.LoadJSON(path)
}

// ValidateIndex checks artifact shape.
func ValidateIndex(art *model.IndexArtifacts) []string {
	return persist.Validate(art)
}
