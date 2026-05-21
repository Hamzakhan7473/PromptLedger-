package index

import (
	"context"
	"fmt"
	"strings"

	"promptledger/graphrag/internal/graphx"
	"promptledger/graphrag/internal/model"
)

const (
	AlgoComponents   = "components"
	AlgoLabelProp    = "labelprop"
	AlgoHierarchical = "hierarchical"
)

func detectCommunities(
	algo string,
	g *graphx.WeightedGraph,
	entityIDsByChunk map[string][]string,
) ([][]string, [][]string) {
	switch algo {
	case AlgoComponents:
		plain := graphx.CooccurrenceGraph(entityIDsByChunk)
		base := plain.ConnectedComponents()
		return base, nil
	case AlgoHierarchical:
		base := graphx.LabelPropagation(g, 25)
		meta := graphx.MetaCommunities(g, base)
		return base, meta
	default: // labelprop
		base := graphx.LabelPropagation(g, 25)
		return base, nil
	}
}

func summarizeCommunity(
	ctx context.Context,
	ix Indexer,
	chunks []model.Chunk,
	entityIDsByChunk map[string][]string,
	memberIDs []string,
	prefix string,
) (string, error) {
	set := map[string]struct{}{}
	for _, id := range memberIDs {
		set[id] = struct{}{}
	}
	var buf strings.Builder
	for _, ch := range chunks {
		if !intersects(set, entityIDsByChunk[ch.ID]) {
			continue
		}
		buf.WriteString(ch.Text)
		buf.WriteString("\n")
	}
	text := strings.TrimSpace(buf.String())
	if text == "" {
		return prefix + " (no local text)", nil
	}
	sys := "Summarize the following text for a community of related entities. Be concise."
	return ix.Completer.Complete(ctx, sys, text)
}

func buildCommunities(
	ctx context.Context,
	ix Indexer,
	chunks []model.Chunk,
	entityIDsByChunk map[string][]string,
	relPairs [][2]string,
) ([]model.Community, string, error) {
	algo := ix.CommunityAlgo
	if algo == "" {
		algo = AlgoLabelProp
	}
	g := graphx.BuildEntityGraph(entityIDsByChunk, relPairs)
	base, meta := detectCommunities(algo, g, entityIDsByChunk)

	var communities []model.Community
	for i, comp := range base {
		sum, err := summarizeCommunity(ctx, ix, chunks, entityIDsByChunk, comp, "")
		if err != nil {
			return nil, "", err
		}
		communities = append(communities, model.Community{
			ID:        fmt.Sprintf("c%d", i),
			Level:     0,
			MemberIDs: append([]string(nil), comp...),
			Summary:   strings.TrimSpace(sum),
		})
	}

	if len(meta) > 0 {
		// Summarize level-1 from level-0 summaries in each meta group.
		idToSummary := map[string]string{}
		for _, c := range communities {
			if c.Level == 0 {
				for _, mid := range c.MemberIDs {
					idToSummary[mid] = c.Summary
				}
			}
		}
		for i, comp := range meta {
			var buf strings.Builder
			for _, eid := range comp {
				if s, ok := idToSummary[eid]; ok {
					buf.WriteString(s)
					buf.WriteString("\n")
				}
			}
			sys := "Summarize these community summaries into one global theme. Be concise."
			sum, err := ix.Completer.Complete(ctx, sys, buf.String())
			if err != nil {
				return nil, "", err
			}
			communities = append(communities, model.Community{
				ID:        fmt.Sprintf("m%d", i),
				Level:     1,
				MemberIDs: append([]string(nil), comp...),
				Summary:   strings.TrimSpace(sum),
			})
		}
	}

	return communities, algo, nil
}
