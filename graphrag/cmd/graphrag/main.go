// Command graphrag demonstrates the GraphRAG indexing + global query pipeline in Go.
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"time"

	"promptledger/graphrag/internal/index"
	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
	"promptledger/graphrag/internal/query"
)

func main() {
	var (
		inPath   = flag.String("index-text", "", "Path to a UTF-8 text file to index (stub LLM)")
		question = flag.String("question", "What are the main themes in this corpus?", "Global question")
	)
	flag.Parse()

	ctx := context.Background()
	c := llm.StubCompleter{}

	if *inPath != "" {
		b, err := os.ReadFile(*inPath)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		ix := index.Indexer{Completer: c}
		art, err := ix.Build(ctx, []model.Document{{
			ID:        "doc1",
			Title:     *inPath,
			Text:      string(b),
			CreatedAt: time.Now(),
		}})
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		_ = enc.Encode(art)
		return
	}

	// Demo without file: tiny synthetic corpus.
	ix := index.Indexer{Completer: c}
	art, err := ix.Build(ctx, []model.Document{{
		ID: "doc1",
		Text: "GraphRAG indexes an entity graph from private documents. " +
			"Community summaries support global questions across the corpus.",
	}})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	e := query.Engine{Completer: c}
	ans, err := e.Global(ctx, *question, art)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(ans.Final)
}
