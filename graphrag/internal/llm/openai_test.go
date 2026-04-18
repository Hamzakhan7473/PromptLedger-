package llm

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestOpenAIChatComplete(t *testing.T) {
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/chat/completions" {
			t.Fatalf("path %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprintf(w, `{"choices":[{"message":{"content":%q}}]}`,
			`{"entities":[],"relationships":[]}`)
	}))
	defer ts.Close()

	c := &OpenAIChat{
		APIKey:  "k",
		BaseURL: ts.URL + "/v1",
		Model:   "m",
	}
	s, err := c.Complete(context.Background(),
		`Return only JSON with keys "entities" and "relationships".`,
		"Text:\nhello",
	)
	if err != nil {
		t.Fatal(err)
	}
	if s == "" {
		t.Fatal("empty content")
	}
}
