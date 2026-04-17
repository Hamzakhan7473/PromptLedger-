package query

import (
	"context"
	"strconv"
	"strings"

	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
)

// GlobalAnswer runs the "map-reduce" style global sensemaking query:
// partial answers from community summaries, then a final consolidation (Edge et al.).
type GlobalAnswer struct {
	Question       string
	PartialAnswers []string
	Final          string
}

type Engine struct {
	Completer llm.Completer
}

func (e Engine) Global(ctx context.Context, q string, idx *model.IndexArtifacts) (*GlobalAnswer, error) {
	if e.Completer == nil {
		return nil, nil
	}
	var partials []string
	for _, c := range idx.Communities {
		if !relevant(q, c) {
			continue
		}
		sys := "Answer the user question using ONLY the community summary. If insufficient, say so."
		user := "Question: " + q + "\nCommunity summary:\n" + c.Summary
		p, err := e.Completer.Complete(ctx, sys, user)
		if err != nil {
			return nil, err
		}
		partials = append(partials, strings.TrimSpace(p))
	}
	if len(partials) == 0 {
		partials = []string{"No community matched this query in the stub heuristic; using all summaries."}
		for _, c := range idx.Communities {
			sys := "Produce a partial answer from this summary only."
			user := "Q: " + q + "\nSummary:\n" + c.Summary
			p, err := e.Completer.Complete(ctx, sys, user)
			if err != nil {
				return nil, err
			}
			partials = append(partials, strings.TrimSpace(p))
		}
	}

	var b strings.Builder
	for i, p := range partials {
		b.WriteString("[")
		b.WriteString(strconv.Itoa(i + 1))
		b.WriteString("] ")
		b.WriteString(p)
		b.WriteString("\n")
	}
	sys := "You consolidate partial answers into one coherent response with citations like [1], [2]."
	user := "Question: " + q + "\nPartial answers:\n" + b.String()
	final, err := e.Completer.Complete(ctx, sys, user)
	if err != nil {
		return nil, err
	}
	return &GlobalAnswer{
		Question:       q,
		PartialAnswers: partials,
		Final:          strings.TrimSpace(final),
	}, nil
}

func relevant(question string, _ model.Community) bool {
	q := strings.ToLower(question)
	// Heuristic for global questions; narrows partial generation. Broad matchers → multi-community.
	return strings.Contains(q, "all") ||
		strings.Contains(q, "theme") ||
		strings.Contains(q, "overview") ||
		strings.Contains(q, "main")
}
