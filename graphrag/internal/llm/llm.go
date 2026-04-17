package llm

import "context"

// Completer abstracts an LLM call used for extraction and summarization.
type Completer interface {
	Complete(ctx context.Context, system, user string) (string, error)
}
