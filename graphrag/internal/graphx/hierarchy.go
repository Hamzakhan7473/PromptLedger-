package graphx

import "sort"

// MetaCommunities merges level-0 communities that share cross-community edges.
func MetaCommunities(g *WeightedGraph, base [][]string) [][]string {
	if len(base) <= 1 {
		return base
	}
	nodeToComm := map[string]int{}
	for i, members := range base {
		for _, n := range members {
			nodeToComm[n] = i
		}
	}
	meta := NewWeightedGraph()
	for i := range base {
		meta.AddNode(itoa(i))
	}
	for a, nbrs := range g.edges {
		ca, okA := nodeToComm[a]
		if !okA {
			continue
		}
		for b, w := range nbrs {
			cb, okB := nodeToComm[b]
			if !okB || ca == cb {
				continue
			}
			meta.AddEdge(itoa(ca), itoa(cb), w)
		}
	}
	metaComps := meta.ConnectedComponentsFromWeighted()
	if len(metaComps) <= 1 {
		return [][]string{flatten(base)}
	}
	var out [][]string
	for _, group := range metaComps {
		seen := map[string]struct{}{}
		var merged []string
		for _, cid := range group {
			idx := atoi(cid)
			if idx < 0 || idx >= len(base) {
				continue
			}
			for _, n := range base[idx] {
				if _, ok := seen[n]; ok {
					continue
				}
				seen[n] = struct{}{}
				merged = append(merged, n)
			}
		}
		sort.Strings(merged)
		if len(merged) > 0 {
			out = append(out, merged)
		}
	}
	return out
}

func (g *WeightedGraph) ConnectedComponentsFromWeighted() [][]string {
	// Reuse unweighted view for meta graph (small).
	plain := NewGraph()
	for id := range g.edges {
		plain.AddNode(id)
		for nb, w := range g.edges[id] {
			if w > 0 {
				plain.AddEdge(id, nb)
			}
		}
	}
	return plain.ConnectedComponents()
}

func flatten(in [][]string) []string {
	var out []string
	for _, s := range in {
		out = append(out, s...)
	}
	sort.Strings(out)
	return out
}

func itoa(i int) string {
	if i == 0 {
		return "0"
	}
	var b [20]byte
	pos := len(b)
	n := i
	for n > 0 {
		pos--
		b[pos] = byte('0' + n%10)
		n /= 10
	}
	return string(b[pos:])
}

func atoi(s string) int {
	n := 0
	for _, c := range s {
		if c < '0' || c > '9' {
			return -1
		}
		n = n*10 + int(c-'0')
	}
	return n
}
