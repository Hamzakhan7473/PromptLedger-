package graphx

import "testing"

func TestLabelPropagationSplitsCliques(t *testing.T) {
	g := NewWeightedGraph()
	// Two cliques connected by one weak bridge
	for _, pair := range [][2]string{{"a1", "a2"}, {"a2", "a3"}, {"b1", "b2"}, {"b2", "b3"}} {
		g.AddEdge(pair[0], pair[1], 3)
	}
	g.AddEdge("a3", "b1", 1)
	comps := LabelPropagation(g, 30)
	if len(comps) < 2 {
		t.Fatalf("expected at least 2 communities, got %d", len(comps))
	}
}
