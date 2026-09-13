# Genius AI — frontend take-home briefing pack

This repository is the briefing pack for frontend take-home assignments: **real Genius AI product context** (Confluence docs + BFF ConnectRPC protos), not abstract toy challenges.

## What’s included

| Path | Purpose |
|------|---------|
| [`docs/`](docs/) | Confluence space **G** (Genius AI) as markdown |
| [`docs/bff-connect-client.md`](docs/bff-connect-client.md) | How to generate and use a **ConnectRPC** TypeScript client |
| [`proto/`](proto/) | Snapshot of Genius BFF `.proto` contracts (`genius.*.v1`) |
| [`buf.yaml`](buf.yaml) / [`buf.gen.yaml`](buf.gen.yaml) | Buf module + Connect-ES codegen config |

## How to use

1. Start at [`docs/index.md`](docs/index.md) (GenAI Home), then Architecture and Design, then the goal/design pages that match the assignment brief.
2. Read [`docs/bff-connect-client.md`](docs/bff-connect-client.md), then run `npx buf dep update && npx buf generate` from this repo root to emit typed clients under `src/gen/`.
3. Workflow **Action:** pages under `docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/` are API/reference detail — skim unless the brief points you there.
4. Treat links to `geniusaidubai.atlassian.net` as the canonical wiki source; this pack may lag slightly.

## Docs contents

- [GenAI Home](docs/index.md)
  - [Design Goal — AI Agents & Workflow Engine Integration](docs/architecture-and-design-genai-lunaya-flow/design-goal-ai-agents-workflow-engine-integration.md)
  - [Events and NATS Topics — GenAI](docs/architecture-and-design-genai-lunaya-flow/events-and-nats-topics-genai.md)
  - [Architecture and Design — GenAI / Lunaya Flow](docs/architecture-and-design-genai-lunaya-flow/index.md)
  - [Phase 1 — Agent-In-Pod checklist & runbook](docs/architecture-and-design-genai-lunaya-flow/phase-1-agent-in-pod-checklist-runbook.md)
  - [Product Workflows & Actions — BFF GUI Integration Guide](docs/architecture-and-design-genai-lunaya-flow/product-workflows-actions-bff-gui-integration-guide.md)
  - [Tenant Isolation Inventory — GenAI BFF (FND-06)](docs/architecture-and-design-genai-lunaya-flow/tenant-isolation-inventory-genai-bff-fnd-06.md)
  - [Webhooks and Event Bus — GenAI BFF](docs/architecture-and-design-genai-lunaya-flow/webhooks-and-event-bus-genai-bff.md)
  - [Workflow Actions — Reference TEST](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference-test.md)
    - [Action: Add](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-add.md)
    - [Action: Aggregate](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-aggregate.md)
    - [Action: Branch](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-branch.md)
    - [Action: Code](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-code.md)
    - [Action: CompareDatasets](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-comparedatasets.md)
    - [Action: Compression](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-compression.md)
    - [Action: Crypto](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-crypto.md)
    - [Action: DateTime](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-datetime.md)
    - [Action: DebugHelper](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-debughelper.md)
    - [Action: Echo](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-echo.md)
    - [Action: ExecuteWorkflow](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-executeworkflow.md)
    - [Action: FileStorage](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-filestorage.md)
    - [Action: Filter](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-filter.md)
    - [Action: HTML](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-html.md)
    - [Action: HttpRequest](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-httprequest.md)
    - [Action: ItemLists](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-itemlists.md)
    - [Action: JWT](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-jwt.md)
    - [Action: Limit](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-limit.md)
    - [Action: Markdown](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-markdown.md)
    - [Action: Merge](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-merge.md)
    - [Action: Mul](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-mul.md)
    - [Action: NoOp](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-noop.md)
    - [Action: RemoveDuplicates](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-removeduplicates.md)
    - [Action: RenameKeys](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-renamekeys.md)
    - [Action: Set](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-set.md)
    - [Action: SetEnv](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-setenv.md)
    - [Action: Sort](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-sort.md)
    - [Action: SplitInBatches](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-splitinbatches.md)
    - [Action: SplitOut](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-splitout.md)
    - [Action: StopAndError](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-stopanderror.md)
    - [Action: Summarize](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-summarize.md)
    - [Action: Totp](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-totp.md)
    - [Action: Wait](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-wait.md)
    - [Action: XML](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/action-xml.md)
    - [Workflow Actions — Reference](docs/architecture-and-design-genai-lunaya-flow/workflow-actions-reference/index.md)
  - [Workflow Debug — Execute to Node](docs/architecture-and-design-genai-lunaya-flow/workflow-debug-execute-to-node.md)
  - [Workforce OS Foundations — Durable Store, Tenancy & Organization](docs/architecture-and-design-genai-lunaya-flow/workforce-os-foundations-durable-store-tenancy-organization.md)
  - [Goal — Genius Workforce OS](docs/goal-genius-workforce-os/index.md)
  - [Workitems Dependency Graph](docs/goal-genius-workforce-os/workitems-dependency-graph.md)
  - [AI Operating System — Initial Design (Google Doc source)](docs/initial-design/ai-operating-system-initial-design-google-doc-source.md)
