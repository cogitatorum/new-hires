# Architecture and Design — GenAI / Lunaya Flow

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314)  
> Confluence page id `18317314` (exported for Genius AI hiring take-home).

---

**Project Goal:** [Goal — Genius Workforce OS](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397571/Goal+Genius+Workforce+OS) is the current product scope and development baseline from Product.

**Audience:** engineers and partners working on GeniusAI GenAI / Lunaya Flow. **Status:** as-built for staging (shared CNPG, Argo Workflows execution, ConnectRPC BFF + runtime). **Last reviewed:** 2026-09-06.

## Related diagrams (whiteboards)

- [GenAI System Context](https://geniusaidubai.atlassian.net/wiki/spaces/G/whiteboard/18350083) — actors and external systems
- [GenAI Cluster Topology](https://geniusaidubai.atlassian.net/wiki/spaces/G/whiteboard/18415617) — namespaces and workloads
- [GenAI Publish and Run Sequence](https://geniusaidubai.atlassian.net/wiki/spaces/G/whiteboard/18415622) — canvas → publish → Argo
- [Webhooks and Event Bus — GenAI BFF](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18415660/Webhooks+and+Event+Bus+GenAI+BFF) — webhook ingress, JetStream subjects, EventRules → Argo
- [Workflow Actions — Reference](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906/Workflow+Actions+Reference) — per-action config, output, and examples for all catalog handlers
- [Workflow Debug — Execute to Node](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/20480011/Workflow+Debug+Execute+to+Node) — run-to-here without publish (PreviewCompile / ExecuteToNode / pins)

## 1. Purpose and scope

This document describes the **architecture and design** of the GenAI workflow platform built so far: a cluster-native system for **declarative product workflows** (canvas) that compile into **action DAGs** executed as **Argo Workflows**, with a product BFF for UI auth/IAM/canvas/credentials and a runtime control plane for defs, runs, and action OCI builds.

**In scope:** runtime daemon, web BFF, Kubernetes platform (Helm), ActionBuild operator, core actions, publish/run data path, durability boundaries.

**Out of scope / not yet built:** schedule triggers, OAuth2 credential helpers, SaaS app nodes, deep attribute/CEL EventRules. **Built:** webhook ingress, NATS JetStream event bus, EventRules → product run. (Workflow *execution* is live via Argo Workflows; unused `genusai.com` Workflow/Step CRDs are registered but not part of that path.)

## 2. System context

External actors and systems that interact with the platform:


| Endpoint / system | Role |
| --- | --- |
| `https://web.geniusai.io` | Public BFF (ConnectRPC over HTTPS via Gateway) |
| `https://harbor.geniusai.io` | OCI registry for app images, charts, and action images |
| `genai-runtime:8080` | Cluster-internal runtime API (not public) |
| CNPG cluster `genai-platform-postgres` | Shared database `genai` (runtime tables + `bff` schema) |
| Argo Workflows | Executes one DAG CR per workflow run |

## 3. High-level architecture


### 3.1 Design principles

- **Declarative graphs, not durable code:** workflows are data (defs + bindings); steps run as OCI action images.
- **Kubernetes as substrate:** placement, isolation, restarts, and secrets come from the cluster; Argo owns DAG orchestration.
- **Product vs runtime split:** BFF owns UI domains and org-scoped canvas; runtime owns executable defs/runs/actions.
- **Schema isolation on shared Postgres:** runtime tables in public schema; BFF in `bff` schema on the same CNPG database.
- **GitOps + digest pins:** charts and images flow through Harbor; ImageUpdater writes digests into Argo CD apps.

## 4. Component catalog

### 4.1 Web BFF (`genius-ai-api` / `genai-web`)

ConnectRPC control plane for the Genius UI. Listens on `:8090`. JWT auth interceptor; CORS outermost.

| Domain | Service | Persistence |
| --- | --- | --- |
| Auth | `genius.auth.v1` | Durable `bff.users` / refresh tokens (or memory fallback) |
| IAM | Orgs / Users / Roles | Same Postgres / memory |
| Product workflows | `genius.workflows.v1.ProductWorkflows` | `bff.product_workflows`, `bff.product_workflow_runs` |
| Credentials | `genius.credentials.v1` | `bff.credentials` (AES-GCM ciphertext) |
| Runtime proxy | `genius.runtime.v1` | Proxies to `GENIUS_RUNTIME_URL` |
| Decisions, work items, agents, approvals, connectors, event bus, settings | Various | **In-memory mock** only |

**Palette:** `ListNodeHandlers` exposes core handlers (manual/schedule/webhook triggers, Branch, Set, NoOp, Wait, HttpRequest, code stub, end).

**Publish validation:** HttpRequest requires `config.method` + `config.url`; edges require `fromNode`/`toNode` (not `from`/`to`).

### 4.2 Runtime daemon (`lunaya-flow-runtime` / `genai-runtime`)

| Service | Responsibility |
| --- | --- |
| `genai.workflow.v1.Workflows` | Create/Get/List defs & runs; StartWorkflowRun → async ArgoRun; DebugRun |
| `genai.actions.v1.Actions` | Action catalog; BuildAction → ActionBuild CR; JetStream build events |
| `genai.events.v1.Events` | NATS-backed events |
| `genai.common.v1.Health` | Health |

**Engine:** `WorkflowDef` (immutable recipe) → `WorkflowRun` (snapshot) → `ArgoRun` (one Argo Workflow CR, fail-fast DAG, optional step `when`).

**Durable tables:** `actions`, `workflow_defs` / `_steps` / `_edges`, `workflow_runs` / `_steps` / `_edges`.

### 4.3 ActionBuild operator (`genai-controller`)

- CRD group `genusai.com`: **ActionBuild** is active. Registered `Workflow`/`Step` CRDs are unused stubs — they are **not** the execution engine. Real runs are submitted as **Argo Workflow** CRs by `genai-runtime`.
- Reconciler creates a build Job: clone git → discover packages → `go build` → `oci.PackAndPush` → Harbor digest → upsert catalog via runtime.
- Builder image: `harbor.geniusai.io/genai/action-builder`.

### 4.4 Core actions (`actions/sample`)

| Action | Role |
| --- | --- |
| Set | Assign fields into an output object |
| Branch | If/Switch → `{selected}` for Argo `when` |
| HttpRequest | Generic HTTP call (credential injection from BFF at publish) |
| NoOp | Placeholder / pass-through |
| Wait | Sleep N seconds |
| Add / Mul | Sample arithmetic catalog actions |

**OCI packing:** scratch image with `/action` + CA trust bundle at `/etc/ssl/certs/ca-certificates.crt` and `SSL_CERT_FILE` (required for HTTPS from action pods).

### 4.5 Platform charts (Helm)

| Chart | Namespace | Provides |
| --- | --- | --- |
| `genai-operators` | `genai-system` | cert-manager, MetalLB, Harbor, Longhorn, CNPG operator, Envoy Gateway, Argo Workflows, … |
| `genai-platform` | `genai` | Postgres, NATS, SeaweedFS, Gateway routes |
| `genai-controller` | `genai-system` | Operator + CRDs |
| `genai-runtime` / `genai-web` | `genai` | App deployments |
| `genai-argocd` | `argocd` | GitOps apps + ImageUpdater digests |
| `genai-observability` | `genai-observability` | Prometheus / Grafana / Loki / Tempo / Velero |

## 5. End-to-end execution flow

For canvas debugging **without** Publish, see [Workflow Debug — Execute to Node](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/20480011/Workflow+Debug+Execute+to+Node) (run-to-here + pins).

Publish and run sequence — one row per phase, left-to-right

### 5.1 Compile rules (product → runtime)

- **Skipped:** TRIGGER, END (and non-executable handlers such as `code` today).
- **Executable:** ACTION + BRANCH nodes → runtime `StepSpec`s.
- **Branch:** dedicated `NODE_KIND_BRANCH` / handler `Branch`; labeled edges become Argo `when` expressions comparing `$.selected`.
- **Config → bindings:** Set/HttpRequest/Wait/Branch config fields become literal bindings; optional `config.bindings` for `fromStep` wiring.
- **Credentials:** HttpRequest `credentialId` resolved at publish; Authorization (or custom header) injected; secret never returned to clients.

Branch compile pattern — Manual → Set → Branch → labeled arms → End

## 6. Data model

Logical data model — BFF (green) and runtime (purple) with orthogonal links

## 7. Networking and GitOps

- **MetalLB** advertises the control-plane public IP; DNS A records for `web.geniusai.io` and `harbor.geniusai.io`.
- **Gateway API** + cert-manager terminate TLS for public hosts.
- **Argo CD** installs Helm charts from Harbor OCI (`genai/charts`).
- **ImageUpdater** watches `genai/{web,runtime,controller}:latest` and writes digests into application Helm parameters.

## 8. Security notes

- BFF JWT access + refresh; RBAC permissions include `workflows.*`, `credentials.*`, `runtime.manage`.
- Credentials encrypted at rest (AES-GCM); key from `GENIUS_CREDENTIALS_KEY` or derived from `GENIUS_JWT_SECRET`.
- At publish, secrets may be projected into runtime step bindings / Argo parameters for HttpRequest (short-lived run artifacts — tighten later with projected K8s secrets if needed).
- Action images must include a CA trust bundle for outbound HTTPS.
- Runtime API is cluster-internal only.

## 9. Durability and maturity matrix

| Capability | State |
| --- | --- |
| Runtime defs / runs / action catalog | DURABLE |
| BFF auth, IAM, product workflows, credentials | DURABLE |
| Argo DAG execution + Branch `when` | WORKING |
| Core actions Set / Branch / HttpRequest / NoOp / Wait | WORKING |
| BFF decisions / agents / approvals / connectors / bus | IN-MEMORY MOCK |
| Schedule / webhook triggers | PALETTE ONLY |
| BFF SubscribeBuildEvents → NATS | STUB |

## 10. Repository map


| Path | Contents |
| --- | --- |
| `runtime/` | Daemon, engine, Argo client, action OCI packer, protos |
| `web/` | BFF APIs, compile/publish, credentials store |
| `k8s/helm/` | Operators, platform, apps, Argo CD, observability |
| `k8s/operator/` | ActionBuild controller; unused Workflow/Step CRD stubs |
| `actions/sample/` | Core / sample action binaries |
| `examples/` | Runtime + product workflow JSON samples |

## 11. Related examples

- Product canvases: `examples/product-workflows/` (set-branch-noop, branch-switch, http-request-get, wait-then-set)
- Runtime defs: `examples/workflows/` (same flows + addmul)

**Canonical happy path today:** Manual → Set → Branch → labeled arms (NoOp/Set/HttpRequest) → Publish → StartRun → Argo Succeeded with correct `when` skip/run behavior.
