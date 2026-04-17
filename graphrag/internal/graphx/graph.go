package graphx

import "sort"

// Undirected adjacency for community detection (simple connected components).
type Graph struct {
	edges map[string]map[string]struct{}
}

func NewGraph() *Graph {
	return &Graph{edges: make(map[string]map[string]struct{})}
}

func (g *Graph) AddNode(id string) {
	if g.edges[id] == nil {
		g.edges[id] = make(map[string]struct{})
	}
}

func (g *Graph) AddEdge(a, b string) {
	if a == b {
		return
	}
	g.AddNode(a)
	g.AddNode(b)
	g.edges[a][b] = struct{}{}
	g.edges[b][a] = struct{}{}
}

// ConnectedComponents returns disjoint sets of node IDs.
func (g *Graph) ConnectedComponents() [][]string {
	seen := make(map[string]struct{})
	var out [][]string
	ids := make([]string, 0, len(g.edges))
	for id := range g.edges {
		ids = append(ids, id)
	}
	sort.Strings(ids)

	for _, start := range ids {
		if _, ok := seen[start]; ok {
			continue
		}
		var comp []string
		stack := []string{start}
		for len(stack) > 0 {
			n := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if _, ok := seen[n]; ok {
				continue
			}
			seen[n] = struct{}{}
			comp = append(comp, n)
			for m := range g.edges[n] {
				if _, ok := seen[m]; !ok {
					stack = append(stack, m)
				}
			}
		}
		sort.Strings(comp)
		out = append(out, comp)
	}
	sort.Slice(out, func(i, j int) bool { return out[i][0] < out[j][0] })
	return out
}

// CooccurrenceGraph builds an entity graph: entities co-mentioned in the same chunk are linked.
func CooccurrenceGraph(entityIDsByChunk map[string][]string) *Graph {
	g := NewGraph()
	all := map[string]struct{}{}
	for _, ids := range entityIDsByChunk {
		for _, id := range ids {
			all[id] = struct{}{}
		}
	}
	for id := range all {
		g.AddNode(id)
	}
	for _, ids := range entityIDsByChunk {
		uniq := uniqueSorted(ids)
		for i := 0; i < len(uniq); i++ {
			for j := i + 1; j < len(uniq); j++ {
				g.AddEdge(uniq[i], uniq[j])
			}
		}
	}
	return g
}

func uniqueSorted(ids []string) []string {
	m := make(map[string]struct{})
	for _, id := range ids {
		m[id] = struct{}{}
	}
	out := make([]string, 0, len(m))
	for id := range m {
		out = append(out, id)
	}
	sort.Strings(out)
	return out
}
