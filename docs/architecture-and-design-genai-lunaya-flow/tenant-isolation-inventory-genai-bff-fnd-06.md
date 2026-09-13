# Tenant Isolation Inventory — GenAI BFF (FND-06)

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21823491](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21823491)  
> Confluence page id `21823491` (exported for Genius AI hiring take-home).

---

Public data surfaces of the Genius AI BFF and how organization isolation is enforced (FND-06 / [GAB-84](https://geniusaidubai.atlassian.net/browse/GAB-84)).

Companion how-to: [Workforce OS Foundations — Durable Store, Tenancy & Organization](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21790723/Workforce+OS+Foundations+Durable+Store+Tenancy+Organization). Design note also in-repo: `web/docs/runtime-tenancy.md`.

Legend: **Fixed** = org-scoped; **Global** = intentionally platform-wide; **Gap** = residual risk.

## ConnectRPC (JWT + Casbin)

| Service | Isolation | Status |
| --- | --- | --- |
| `genius.auth.v1.Auth` | JWT carries `org_id` | Fixed |
| `genius.iam.v1.*` | Org-scoped users/roles; Casbin domain = org | Fixed |
| `genius.workflows.v1.ProductWorkflows` | Workflows/runs keyed by `org_id` | Fixed |
| `genius.workitems.v1.WorkItems` | Product store `org_id` | Fixed (GAB-83) |
| `genius.decisions.v1.Decisions` | Product store `org_id` | Fixed (GAB-83) |
| `genius.agents.v1.Agents` | Product store `org_id` | Fixed (GAB-83) |
| `genius.approvals.v1.*` | Product store `org_id` | Fixed (GAB-83) |
| `genius.connectors.v1.Connectors` | Product store `org_id` | Fixed (GAB-83) |
| `genius.settings.v1.Settings` | `bff.org_settings` | Fixed (GAB-83) |
| `genius.workforce.v1.*` | Org-model tables + `workforce.*` perms | Fixed (GAB-91) |
| `genius.credentials.v1.Credentials` | `credentials.org_id` | Fixed |
| `genius.bus.v1.EventBus` / `EventRules` | Org on publish/rules | Fixed |
| `genius.overview.v1.Overview` | Aggregates org-scoped stores | Fixed |
| `genius.runtime.v1.RuntimeActions` | Global actions catalog; `runtime.manage` | **Global** |
| `genius.runtime.v1.RuntimeWorkflows` (defs) | Runtime-global defs | **Global** |
| `genius.runtime.v1.RuntimeWorkflows` (runs) | `runtime_run_bindings` + NotFound on cross-org | **Fixed** (GAB-84) |

## HTTP / NATS

| Surface | Isolation | Status |
| --- | --- | --- |
| `POST /hooks/v1/{path}` | Path → `(org_id, workflow_id)` + secret | Fixed |
| Event publish / rules evaluator | Org in subject/metadata; rules by org | Fixed |
| Action build event subscribe | Platform stream; not product-tenant rows | Global stream |

## Runtime proxy detail

| Operation | Status |
| --- | --- |
| Actions Build/Get/List/Delete | Global + `runtime.manage` |
| Workflow defs CRUD/list | Global |
| StartWorkflowRun | Bind to caller org |
| GetWorkflowRun / ListReadySteps | `requireRuntimeRunOrg` |
| DebugRun | Bind stream run ids |
| Product StartRun / webhook / schedule | Bind + workflow store org scope |

## Residual global surfaces

1. Shared **actions catalog** for anyone with `runtime.manage`.
2. Runtime **workflow definitions** are not org-namespaced in the daemon; product workflows hold per-org `runtime_def_id`.
3. Without Postgres product store, binding-dependent runtime RPCs return `FailedPrecondition`.

## FND-06 evidence

Automated: `go test ./internal/services/ -run Tenancy` in `genius-ai-api`.

Staging: seed two orgs via `web/scripts/seed-fnd06-tenants.fish`, then attempt cross-tenant Get/List on work items, workforce, and runtime runs.
