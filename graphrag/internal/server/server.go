package server

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"strings"
	"time"

	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
	"promptledger/graphrag/internal/persist"
	"promptledger/graphrag/internal/query"
	"promptledger/graphrag/pkg/contextfmt"
)

// Server exposes a minimal REST API for GraphRAG.
type Server struct {
	IndexPath string
	Artifacts *model.IndexArtifacts
	Completer llm.Completer
}

func New(indexPath string, c llm.Completer) (*Server, error) {
	art, err := persist.LoadJSON(indexPath)
	if err != nil {
		return nil, err
	}
	return &Server{IndexPath: indexPath, Artifacts: art, Completer: c}, nil
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", s.handleHealth)
	mux.HandleFunc("GET /v1/context", s.handleContext)
	mux.HandleFunc("POST /v1/query", s.handleQuery)
	mux.HandleFunc("GET /v1/index/meta", s.handleMeta)
	return mux
}

func (s *Server) handleHealth(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, map[string]string{"status": "ok"})
}

func (s *Server) handleMeta(w http.ResponseWriter, _ *http.Request) {
	writeJSON(w, s.Artifacts.Meta)
}

func (s *Server) handleContext(w http.ResponseWriter, r *http.Request) {
	q := r.URL.Query().Get("question")
	ctx := contextfmt.ForPrompt(s.Artifacts, q)
	writeJSON(w, map[string]string{"retrieved_context": ctx})
}

func (s *Server) handleQuery(w http.ResponseWriter, r *http.Request) {
	var body struct {
		Question string `json:"question"`
	}
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	body.Question = strings.TrimSpace(body.Question)
	if body.Question == "" {
		http.Error(w, "question required", http.StatusBadRequest)
		return
	}
	ctx, cancel := context.WithTimeout(r.Context(), 120*time.Second)
	defer cancel()
	e := query.Engine{Completer: s.Completer}
	ans, err := e.Global(ctx, body.Question, s.Artifacts)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	writeJSON(w, ans)
}

func writeJSON(w http.ResponseWriter, v any) {
	w.Header().Set("Content-Type", "application/json")
	enc := json.NewEncoder(w)
	enc.SetIndent("", "  ")
	_ = enc.Encode(v)
}

// ListenAndServe starts the HTTP server.
func (s *Server) ListenAndServe(addr string) error {
	return http.ListenAndServe(addr, s.Handler())
}

// ReloadIndex refreshes artifacts from disk.
func (s *Server) ReloadIndex() error {
	art, err := persist.LoadJSON(s.IndexPath)
	if err != nil {
		return err
	}
	s.Artifacts = art
	return nil
}

// DrainBody is a test helper.
func DrainBody(r io.Reader) ([]byte, error) {
	return io.ReadAll(r)
}
