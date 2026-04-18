package llm

import (
	"os"
	"strings"
)

// Mode describes which completer is active.
type Mode string

const (
	ModeStub   Mode = "stub"
	ModeOpenAI Mode = "openai"
)

// CompleterFromEnv returns Stub when OPENAI_API_KEY is unset; otherwise OpenAIChat.
// If forceStub is true, always returns stub (for tests / offline).
func CompleterFromEnv(forceStub bool) (c Completer, mode Mode, err error) {
	if forceStub {
		return StubCompleter{}, ModeStub, nil
	}
	if strings.TrimSpace(os.Getenv("OPENAI_API_KEY")) == "" {
		return StubCompleter{}, ModeStub, nil
	}
	o, err := NewOpenAIChatFromEnv()
	if err != nil {
		return nil, "", err
	}
	return o, ModeOpenAI, nil
}
