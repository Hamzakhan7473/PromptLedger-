# Next.js UI (target)

The production user path in the architecture diagram is:

```
Users → Next.js UI → API Gateway → Agent Orchestrator
```

**Current demo UI:** `web/frontend/` (static + FastAPI) — sufficient for recordings and Kubernetes demos.

**Planned Next.js app** (this directory):

- App Router + TypeScript
- Vertical picker (Legal, Tax, Fintech, Healthcare, Research)
- Agent run console with live trajectory steps
- Evaluation dashboard (success rate, reward, hallucination proxy)
- Links to PromptLedger evidence export and manifest diff

API base: `NEXT_PUBLIC_API_URL` → `/api/agent/*` and `/api/demo/*`

Scaffold when ready:

```bash
npx create-next-app@latest platform-ui --typescript --app --src-dir
```
