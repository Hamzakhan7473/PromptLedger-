package graphx

import "testing"

func TestConnectedComponents(t *testing.T) {
	g := CooccurrenceGraph(map[string][]string{
		"a": {"e1", "e2"},
		"b": {"e2", "e3"},
		"c": {"e9"},
	})
	comps := g.ConnectedComponents()
	if len(comps) != 2 {
		t.Fatalf("expected 2 components, got %d", len(comps))
	}
}
