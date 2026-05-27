# Architecture diagrams

## Kubernetes deployment (FigJam)

**File:** [kubernetes-deployment-architecture.jam](./kubernetes-deployment-architecture.jam)

Open in [Figma FigJam](https://www.figma.com/figjam/) (File → Import, or drag the `.jam` file into FigJam).

The diagram covers:

- Multi-stage Docker build (Go GraphRAG + Python API)
- Kustomize overlays (`dev` / `staging` / `production`)
- Ingress, Service, Deployment, HPA, PDB, NetworkPolicy
- Pod internals: FastAPI, demo UI, ConfigMap, `emptyDir` cache
- Local **kind** path (NodePort → host `8765`)
- Governance demo flow across Legal, Fintech, Healthcare, and Enterprise AI

Manifests and runbooks: [deploy/kubernetes/README.md](../../deploy/kubernetes/README.md).
