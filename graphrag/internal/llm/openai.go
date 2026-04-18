package llm

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
	"time"
)

// OpenAIChat uses the OpenAI-compatible Chat Completions HTTP API (OpenAI, Azure OpenAI base URL, etc.).
type OpenAIChat struct {
	APIKey     string
	BaseURL    string // e.g. https://api.openai.com/v1 (no trailing slash)
	Model      string
	HTTPClient *http.Client
}

// NewOpenAIChatFromEnv builds a client from environment variables:
//   - OPENAI_API_KEY (required)
//   - OPENAI_BASE_URL (optional, default https://api.openai.com/v1)
//   - OPENAI_MODEL (optional, default gpt-4o-mini)
func NewOpenAIChatFromEnv() (*OpenAIChat, error) {
	key := strings.TrimSpace(os.Getenv("OPENAI_API_KEY"))
	if key == "" {
		return nil, fmt.Errorf("OPENAI_API_KEY is not set")
	}
	base := strings.TrimSuffix(strings.TrimSpace(os.Getenv("OPENAI_BASE_URL")), "/")
	if base == "" {
		base = "https://api.openai.com/v1"
	}
	model := strings.TrimSpace(os.Getenv("OPENAI_MODEL"))
	if model == "" {
		model = "gpt-4o-mini"
	}
	return &OpenAIChat{
		APIKey:  key,
		BaseURL: base,
		Model:   model,
		HTTPClient: &http.Client{
			Timeout: 120 * time.Second,
		},
	}, nil
}

type chatRequest struct {
	Model          string              `json:"model"`
	Messages       []map[string]string `json:"messages"`
	Temperature    float64             `json:"temperature"`
	ResponseFormat *struct {
		Type string `json:"type"`
	} `json:"response_format,omitempty"`
}

type chatResponse struct {
	Error *struct {
		Message string `json:"message"`
		Type    string `json:"type"`
	} `json:"error"`
	Choices []struct {
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
	} `json:"choices"`
}

func (o *OpenAIChat) client() *http.Client {
	if o.HTTPClient != nil {
		return o.HTTPClient
	}
	return http.DefaultClient
}

// Complete implements Completer.
func (o *OpenAIChat) Complete(ctx context.Context, system, user string) (string, error) {
	if o.APIKey == "" {
		return "", fmt.Errorf("OpenAIChat: missing API key")
	}
	url := o.BaseURL + "/chat/completions"
	reqBody := chatRequest{
		Model: o.Model,
		Messages: []map[string]string{
			{"role": "system", "content": system},
			{"role": "user", "content": user},
		},
		Temperature: 0.2,
	}
	ls := strings.ToLower(system)
	if strings.Contains(ls, "entities") && strings.Contains(ls, "relationships") {
		reqBody.ResponseFormat = &struct {
			Type string `json:"type"`
		}{Type: "json_object"}
	}
	raw, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(raw))
	if err != nil {
		return "", err
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+o.APIKey)

	resp, err := o.client().Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return "", fmt.Errorf("openai http %d: %s", resp.StatusCode, shortenErr(body))
	}
	var out chatResponse
	if err := json.Unmarshal(body, &out); err != nil {
		return "", fmt.Errorf("decode response: %w", err)
	}
	if out.Error != nil && out.Error.Message != "" {
		return "", fmt.Errorf("openai api: %s", out.Error.Message)
	}
	if len(out.Choices) == 0 {
		return "", fmt.Errorf("openai: empty choices")
	}
	return strings.TrimSpace(out.Choices[0].Message.Content), nil
}

func shortenErr(b []byte) string {
	s := string(b)
	if len(s) > 500 {
		return s[:500] + "…"
	}
	return s
}
