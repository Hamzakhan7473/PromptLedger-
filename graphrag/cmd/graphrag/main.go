// Command graphrag runs the GraphRAG indexing + global query pipeline in Go.
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
	"promptledger/graphrag/internal/persist"
	"promptledger/graphrag/internal/query"
	"promptledger/graphrag/internal/server"
	"promptledger/graphrag/pkg/contextfmt"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "index":
		cmdIndex(os.Args[2:])
	case "batch":
		cmdBatch(os.Args[2:])
	case "query":
		cmdQuery(os.Args[2:])
	case "context":
		cmdContext(os.Args[2:])
	case "validate":
		cmdValidate(os.Args[2:])
	case "serve":
		cmdServe(os.Args[2:])
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
  graphrag index    -text <file> -o <index.json> [-chunk-runes N] [-algo labelprop|hierarchical|components] [-stub]
  graphrag batch    -dir <folder> -o <index.json> [-algo ...] [-stub]
  graphrag query    -index <index.json> -question "..." [-stub]
  graphrag context  -index <index.json> [-question "..."]  # PromptLedger {retrieved_context}
  graphrag validate -index <index.json>
  graphrag serve    -index <index.json> -addr :8080 [-stub]
  graphrag demo     [-question "..."]

Environment:
  OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

`)
}

func completer(stub bool) (llm.Completer, llm.Mode, error) {
	c, mode, err := llm.CompleterFromEnv(stub)
	if err != nil {
		return nil, "", err
	}
	fmt.Fprintf(os.Stderr, "llm mode: %s\n", mode)
	return c, mode, nil
}

func cmdIndex(args []string) {
	fs := flag.NewFlagSet("index", flag.ExitOnError)
	textPath := fs.String("text", "", "path to UTF-8 text file")
	outPath := fs.String("o", "", "write index JSON")
	chunk := fs.Int("chunk-runes", 800, "max runes per chunk")
	algo := fs.String("algo", index.AlgoLabelProp, "community detection: labelprop|hierarchical|components")
	forceStub := fs.Bool("stub", false, "force offline stub LLM")
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
	c, _, err := completer(*forceStub)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	ctx := context.Background()
	ix := index.Indexer{Completer: c, ChunkRunes: *chunk, CommunityAlgo: *algo}
	art, err := ix.Build(ctx, []model.Document{{
		ID: "doc1", Title: *textPath, Text: string(b), CreatedAt: time.Now().UTC(),
	}})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	writeIndex(*outPath, art)
}

func cmdBatch(args []string) {
	fs := flag.NewFlagSet("batch", flag.ExitOnError)
	dir := fs.String("dir", "", "directory of .txt/.md files")
	outPath := fs.String("o", "", "write index JSON")
	chunk := fs.Int("chunk-runes", 800, "max runes per chunk")
	algo := fs.String("algo", index.AlgoHierarchical, "community detection algorithm")
	forceStub := fs.Bool("stub", false, "force stub LLM")
	_ = fs.Parse(args)
	if *dir == "" || *outPath == "" {
		fmt.Fprintln(os.Stderr, "batch: -dir and -o are required")
		os.Exit(2)
	}
	docs, err := index.DocumentsFromDir(*dir)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	c, _, err := completer(*forceStub)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	ctx := context.Background()
	ix := index.Indexer{Completer: c, ChunkRunes: *chunk, CommunityAlgo: *algo}
	art, err := ix.Build(ctx, docs)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	writeIndex(*outPath, art)
}

func cmdQuery(args []string) {
	fs := flag.NewFlagSet("query", flag.ExitOnError)
	indexPath := fs.String("index", "", "index JSON path")
	question := fs.String("question", "", "global question")
	jsonOut := fs.Bool("json", false, "emit full GlobalAnswer JSON")
	forceStub := fs.Bool("stub", false, "force stub LLM")
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
	c, _, err := completer(*forceStub)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	ctx := context.Background()
	ans, err := query.Engine{Completer: c}.Global(ctx, *question, art)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if *jsonOut {
		enc := json.NewEncoder(os.Stdout)
		enc.SetIndent("", "  ")
		_ = enc.Encode(ans)
		return
	}
	fmt.Println(ans.Final)
}

func cmdContext(args []string) {
	fs := flag.NewFlagSet("context", flag.ExitOnError)
	indexPath := fs.String("index", "", "index JSON path")
	question := fs.String("question", "", "optional question to rank communities")
	_ = fs.Parse(args)
	if *indexPath == "" {
		fmt.Fprintln(os.Stderr, "context: -index is required")
		os.Exit(2)
	}
	art, err := persist.LoadJSON(*indexPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(contextfmt.ForPrompt(art, *question))
}

func cmdValidate(args []string) {
	fs := flag.NewFlagSet("validate", flag.ExitOnError)
	indexPath := fs.String("index", "", "index JSON path")
	jsonOut := fs.Bool("json", false, "JSON output")
	_ = fs.Parse(args)
	if *indexPath == "" {
		fmt.Fprintln(os.Stderr, "validate: -index is required")
		os.Exit(2)
	}
	art, err := persist.LoadJSON(*indexPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	issues := persist.Validate(art)
	if *jsonOut {
		_ = json.NewEncoder(os.Stdout).Encode(map[string]any{
			"passed": len(issues) == 0,
			"issues": issues,
			"meta":   art.Meta,
		})
	} else {
		for _, i := range issues {
			fmt.Println(i)
		}
	}
	if len(issues) > 0 {
		os.Exit(1)
	}
}

func cmdServe(args []string) {
	fs := flag.NewFlagSet("serve", flag.ExitOnError)
	indexPath := fs.String("index", "", "index JSON path")
	addr := fs.String("addr", ":8080", "listen address")
	forceStub := fs.Bool("stub", false, "force stub LLM for query endpoint")
	_ = fs.Parse(args)
	if *indexPath == "" {
		fmt.Fprintln(os.Stderr, "serve: -index is required")
		os.Exit(2)
	}
	c, _, err := completer(*forceStub)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	srv, err := server.New(*indexPath, c)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "listening on %s (index %s)\n", *addr, *indexPath)
	if err := srv.ListenAndServe(*addr); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func cmdDemo(args []string) {
	fs := flag.NewFlagSet("demo", flag.ExitOnError)
	question := fs.String("question", "What are the main themes in this corpus?", "global question")
	_ = fs.Parse(args)
	ctx := context.Background()
	c, _, err := completer(true)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	ix := index.Indexer{Completer: c, CommunityAlgo: index.AlgoLabelProp}
	art, err := ix.Build(ctx, []model.Document{{
		ID: "doc1",
		Text: "GraphRAG indexes an entity graph from private documents. " +
			"Community summaries support global questions across the corpus.",
		CreatedAt: time.Now().UTC(),
	}})
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	ans, err := query.Engine{Completer: c}.Global(ctx, *question, art)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(ans.Final)
}

func writeIndex(path string, art *model.IndexArtifacts) {
	if err := persist.SaveJSON(path, art); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "wrote %s (%d chunks, %d entities, %d communities, algo=%s)\n",
		path, len(art.Chunks), len(art.Entities), len(art.Communities), art.Meta.CommunityAlgorithm)
}
