// Command graphrag runs the GraphRAG indexing + global query pipeline in Go.
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"time"

	"promptledger/graphrag/internal/index"
	"promptledger/graphrag/internal/llm"
	"promptledger/graphrag/internal/model"
	"promptledger/graphrag/internal/persist"
	"promptledger/graphrag/internal/query"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "index":
		cmdIndex(os.Args[2:])
	case "query":
		cmdQuery(os.Args[2:])
	case "demo":
		cmdDemo(os.Args[2:])
	default:
		fmt.Fprintf(os.Stderr, "unknown subcommand %q\n\n", os.Args[1])
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintf(os.Stderr, `Usage:
  graphrag index  -text <file> -o <index.json> [-chunk-runes N]
  graphrag query  -index <index.json> -question "..." [-stub]
  graphrag demo   [-question "..."] (offline stub)

Environment (optional):
  OPENAI_API_KEY   If set, uses OpenAI-compatible chat completions for index/query.
  OPENAI_BASE_URL  Default https://api.openai.com/v1
  OPENAI_MODEL     Default gpt-4o-mini

`)
}

func cmdIndex(args []string) {
	fs := flag.NewFlagSet("index", flag.ExitOnError)
	textPath := fs.String("text", "", "path to UTF-8 text file to index")
	outPath := fs.String("o", "", "write index JSON to this path")
	chunk := fs.Int("chunk-runes", 800, "max runes per chunk")
	forceStub := fs.Bool("stub", false, "force offline stub LLM (ignore OPENAI_API_KEY)")
	_ = fs.Parse(args)

	if *textPath == "" || *outPath == "" {
		fmt.Fprintln(os.Stderr, "index: -text and -o are required")
		os.Exit(2)
	}
	b, err := os.ReadFile(*textPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	c, mode, err := llm.CompleterFromEnv(*forceStub)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "llm mode: %s\n", mode)

	ctx := context.Background()
	ix := index.Indexer{Completer: c, ChunkRunes: *chunk}

	art, err := ix.Build(ctx, []model.Document{{
		ID:        "doc1",
		Title:     *textPath,
		Text:      string(b),
		CreatedAt: time.Now(),
	}})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := persist.SaveJSON(*outPath, art); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "wrote %s (%d chunks, %d communities)\n", *outPath, len(art.Chunks), len(art.Communities))
}

func cmdQuery(args []string) {
	fs := flag.NewFlagSet("query", flag.ExitOnError)
	indexPath := fs.String("index", "", "path to index JSON from graphrag index")
	question := fs.String("question", "", "global question")
	forceStub := fs.Bool("stub", false, "force offline stub LLM")
	_ = fs.Parse(args)

	if *indexPath == "" || *question == "" {
		fmt.Fprintln(os.Stderr, "query: -index and -question are required")
		os.Exit(2)
	}

	art, err := persist.LoadJSON(*indexPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	c, mode, err := llm.CompleterFromEnv(*forceStub)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "llm mode: %s\n", mode)

	ctx := context.Background()
	e := query.Engine{Completer: c}
	ans, err := e.Global(ctx, *question, art)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(ans.Final)
}

func cmdDemo(args []string) {
	fs := flag.NewFlagSet("demo", flag.ExitOnError)
	question := fs.String("question", "What are the main themes in this corpus?", "global question")
	_ = fs.Parse(args)

	ctx := context.Background()
	c, mode, err := llm.CompleterFromEnv(true)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "llm mode: %s (demo always stub)\n", mode)

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
