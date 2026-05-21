package contextfmt

import (
	"sort"
	"strings"
	"unicode"

	"promptledger/graphrag/internal/model"
)

// ForPrompt builds {retrieved_context} text compatible with PromptLedger render checks.
func ForPrompt(art *model.IndexArtifacts, question string) string {
	if art == nil {
		return ""
	}
	q := tokenize(question)
	type scored struct {
		c     model.Community
		score int
	}
	var list []scored
	for _, c := range art.Communities {
		list = append(list, scored{c, scoreCommunity(q, c, art)})
	}
	sort.Slice(list, func(i, j int) bool {
		if list[i].score != list[j].score {
			return list[i].score > list[j].score
		}
		return list[i].c.ID < list[j].c.ID
	})
	maxS := 0
	if len(list) > 0 {
		maxS = list[0].score
	}
	var picked []model.Community
	if maxS == 0 {
		picked = art.Communities
	} else {
		thresh := max(1, (maxS+1)/2)
		for _, sc := range list {
			if sc.score >= thresh && len(picked) < 10 {
				picked = append(picked, sc.c)
			}
		}
	}
	if len(picked) == 0 {
		picked = art.Communities
	}
	var parts []string
	for i, c := range picked {
		parts = append(parts, "["+c.ID+"] "+strings.TrimSpace(c.Summary))
		if i >= 9 {
			break
		}
	}
	return strings.Join(parts, "\n")
}

func scoreCommunity(q []string, c model.Community, art *model.IndexArtifacts) int {
	names := map[string]string{}
	for _, e := range art.Entities {
		names[e.ID] = e.Name
	}
	text := strings.ToLower(c.Summary)
	for _, id := range c.MemberIDs {
		text += " " + strings.ToLower(names[id])
	}
	set := map[string]struct{}{}
	for _, t := range tokenize(text) {
		set[t] = struct{}{}
	}
	sc := 0
	for _, t := range q {
		if _, ok := set[t]; ok {
			sc++
		}
	}
	if c.Level == 1 {
		sc++ // slight boost for meta communities
	}
	return sc
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
		if len(w) >= 3 {
			out = append(out, w)
		}
	}
	return out
}

func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
