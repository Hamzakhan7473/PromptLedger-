package graphx

import "sort"

// LabelPropagation runs weighted label propagation community detection.
func LabelPropagation(g *WeightedGraph, maxIter int) [][]string {
	if maxIter <= 0 {
		maxIter = 20
	}
	nodes := g.Nodes()
	if len(nodes) == 0 {
		return nil
	}
	label := make(map[string]string, len(nodes))
	for _, n := range nodes {
		label[n] = n
	}
	for iter := 0; iter < maxIter; iter++ {
		changed := false
		for _, n := range nodes {
			votes := map[string]int{}
			for nb, w := range g.Neighbors(n) {
				votes[label[nb]] += w
			}
			votes[label[n]] += 1 // self bias
			best := label[n]
			bestScore := -1
			for cand, score := range votes {
				if score > bestScore || (score == bestScore && cand < best) {
					best = cand
					bestScore = score
				}
			}
			if best != label[n] {
				label[n] = best
				changed = true
			}
		}
		if !changed {
			break
		}
	}
	groups := map[string][]string{}
	for _, n := range nodes {
		l := label[n]
		groups[l] = append(groups[l], n)
	}
	out := make([][]string, 0, len(groups))
	for _, members := range groups {
		sort.Strings(members)
		out = append(out, members)
	}
	sort.Slice(out, func(i, j int) bool { return out[i][0] < out[j][0] })
	return out
}
