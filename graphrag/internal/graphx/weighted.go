package graphx

import "sort"

// WeightedGraph is an undirected graph with integer edge weights.
type WeightedGraph struct {
	edges map[string]map[string]int
}

func NewWeightedGraph() *WeightedGraph {
	return &WeightedGraph{edges: make(map[string]map[string]int)}
}

func (g *WeightedGraph) AddNode(id string) {
	if g.edges[id] == nil {
		g.edges[id] = make(map[string]int)
	}
}

func (g *WeightedGraph) AddEdge(a, b string, w int) {
	if a == b || w <= 0 {
		return
	}
	g.AddNode(a)
	g.AddNode(b)
	g.edges[a][b] += w
	g.edges[b][a] += w
}

func (g *WeightedGraph) Neighbors(id string) map[string]int {
	return g.edges[id]
}

func (g *WeightedGraph) Nodes() []string {
	ids := make([]string, 0, len(g.edges))
	for id := range g.edges {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	return ids
}

// BuildEntityGraph links co-occurrence within chunks and explicit relationships.
func BuildEntityGraph(
	entityIDsByChunk map[string][]string,
	relationships [][2]string,
) *WeightedGraph {
	g := NewWeightedGraph()
	for _, ids := range entityIDsByChunk {
		uniq := uniqueSorted(ids)
		for i := 0; i < len(uniq); i++ {
			for j := i + 1; j < len(uniq); j++ {
				g.AddEdge(uniq[i], uniq[j], 1)
			}
		}
	}
	for _, pair := range relationships {
		g.AddEdge(pair[0], pair[1], 2)
	}
	return g
}
