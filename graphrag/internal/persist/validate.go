package persist

import (
	"fmt"

	"promptledger/graphrag/internal/model"
)

// Validate returns human-readable issues (empty if OK).
func Validate(art *model.IndexArtifacts) []string {
	var issues []string
	if art == nil {
		return []string{"nil artifacts"}
	}
	if len(art.Chunks) == 0 {
		issues = append(issues, "no chunks")
	}
	if len(art.Entities) == 0 {
		issues = append(issues, "no entities")
	}
	if len(art.Communities) == 0 {
		issues = append(issues, "no communities")
	}
	entitySet := map[string]struct{}{}
	for _, e := range art.Entities {
		entitySet[e.ID] = struct{}{}
	}
	for _, c := range art.Communities {
		if c.Summary == "" {
			issues = append(issues, fmt.Sprintf("community %s has empty summary", c.ID))
		}
		for _, mid := range c.MemberIDs {
			if _, ok := entitySet[mid]; !ok {
				issues = append(issues, fmt.Sprintf("community %s references unknown entity %s", c.ID, mid))
			}
		}
	}
	for _, r := range art.Relationships {
		if _, ok := entitySet[r.SourceID]; !ok {
			issues = append(issues, fmt.Sprintf("relationship %s unknown source %s", r.ID, r.SourceID))
		}
		if _, ok := entitySet[r.TargetID]; !ok {
			issues = append(issues, fmt.Sprintf("relationship %s unknown target %s", r.ID, r.TargetID))
		}
	}
	return issues
}
