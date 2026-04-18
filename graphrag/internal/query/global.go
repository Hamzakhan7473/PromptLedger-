package query

import (
	"context"
	"fmt"
	"sort"
	"strconv"
	"strings"
	"unicode"

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
		return nil, fmt.Errorf("query engine: completer is nil")
	}
	if idx == nil {
		return nil, fmt.Errorf("query engine: index is nil")
	}

	lookup := entityNames(idx)
	selected := selectCommunities(q, idx, lookup)

	var partials []string
	for _, c := range selected {
		sys := "Answer the user question using ONLY the community summary. If insufficient, say so."
		user := "Question: " + q + "\nCommunity summary:\n" + c.Summary
		p, err := e.Completer.Complete(ctx, sys, user)
		if err != nil {
			return nil, err
		}
		partials = append(partials, strings.TrimSpace(p))
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

func entityNames(idx *model.IndexArtifacts) map[string]string {
	m := make(map[string]string, len(idx.Entities))
	for _, e := range idx.Entities {
		m[e.ID] = e.Name
	}
	return m
}

type scoredCommunity struct {
	c model.Community
	s int
}

func selectCommunities(q string, idx *model.IndexArtifacts, names map[string]string) []model.Community {
	if len(idx.Communities) == 0 {
		return nil
	}
	var scored []scoredCommunity
	for _, c := range idx.Communities {
		scored = append(scored, scoredCommunity{c: c, s: relevanceScore(q, c, names)})
	}
	sort.Slice(scored, func(i, j int) bool {
		if scored[i].s != scored[j].s {
			return scored[i].s > scored[j].s
		}
		return scored[i].c.ID < scored[j].c.ID
	})

	maxS := scored[0].s
	if maxS == 0 {
		return idx.Communities
	}

	thresh := max(1, (maxS+1)/2)
	var out []model.Community
	for _, sc := range scored {
		if sc.s >= thresh {
			out = append(out, sc.c)
		}
		if len(out) >= 10 {
			break
		}
	}
	if len(out) == 0 {
		return idx.Communities
	}
	return out
}

func relevanceScore(q string, c model.Community, names map[string]string) int {
	qTerms := tokenize(q)
	if len(qTerms) == 0 {
		return 0
	}
	text := strings.ToLower(c.Summary)
	for _, id := range c.MemberIDs {
		text += " " + strings.ToLower(names[id])
	}
	set := map[string]struct{}{}
	for _, t := range tokenize(text) {
		set[t] = struct{}{}
	}
	score := 0
	for _, t := range qTerms {
		if _, ok := set[t]; ok {
			score++
		}
	}
	return score
}

var stopwords = map[string]struct{}{
	"the": {}, "and": {}, "for": {}, "are": {}, "but": {}, "not": {}, "you": {}, "all": {},
	"can": {}, "her": {}, "was": {}, "one": {}, "our": {}, "out": {}, "has": {}, "have": {},
	"this": {}, "that": {}, "with": {}, "from": {}, "they": {}, "will": {}, "what": {},
	"when": {}, "who": {}, "how": {}, "why": {}, "does": {}, "did": {}, "into": {},
}

func tokenize(s string) []string {
	s = strings.ToLower(s)
	var b strings.Builder
	for _, r := range s {
		if unicode.IsLetter(r) || unicode.IsNumber(r) {
			b.WriteRune(r)
		} else {
			b.WriteRune(' ')
		}
	}
	var out []string
	for _, w := range strings.Fields(b.String()) {
		if len(w) < 3 {
			continue
		}
		if _, ok := stopwords[w]; ok {
			continue
		}
		out = append(out, w)
	}
	return out
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
