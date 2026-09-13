# Workforce OS Foundations — Durable Store, Tenancy & Organization

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21790723](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21790723)  
> Confluence page id `21790723` (exported for Genius AI hiring take-home).

---

Operator and engineer guide for the three foundation slices that landed on the GenAI BFF (staging: `web.geniusai.io`): durable product domain storage, tenant isolation (FND-06), and the organization / workforce model.

**Related:** [Goal — Genius Workforce OS](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397571/Goal+Genius+Workforce+OS) · Jira [GAB-83](https://geniusaidubai.atlassian.net/browse/GAB-83) · [GAB-84](https://geniusaidubai.atlassian.net/browse/GAB-84) · [GAB-91](https://geniusaidubai.atlassian.net/browse/GAB-91)

**Code:** `genius-ai-api` (`web/`) · schema `web/internal/store/postgres/schema.sql` · Connect services under `genius.*.v1`

---

## Prerequisites

- Staging BFF with **Postgres** (`GENIUS_POSTGRES_*`). Product and workforce RPCs are **fail-closed**: without a product store they return `FailedPrecondition`.
- JWT session from `genius.auth.v1.Auth/Login`. Claims carry `org_id` (`oid`); every List/Get/Mutate is scoped to that org.
- Casbin permissions on the session (owner/admin include `workforce.manage`, `settings.write`, `workitems.write`, `runtime.manage`, etc.).

Base URL (Connect JSON or gRPC/h2c):

```text
https://web.geniusai.io
```

Login example:

```bash
grpcurl -d '{"email":"you@example.com","password":"…"}' \
  web.geniusai.io:443 genius.auth.v1.Auth/Login
# use .accessToken as: -H "Authorization: Bearer <token>"
```

---

## 1. Durable product domain (GAB-83)

### What changed

Product domains that previously lived in process memory now persist in CNPG (`bff` schema), always with `org_id`:

| Domain | Tables | Connect service |
| --- | --- | --- |
| Work items | `bff.work_items` | `genius.workitems.v1.WorkItems` |
| Decisions | `bff.decisions` | `genius.decisions.v1.Decisions` |
| Agents | `bff.agents` | `genius.agents.v1.Agents` |
| Approvals / policies | `bff.approvals`, `bff.approval_policies` | `genius.approvals.v1.*` |
| Connectors | `bff.connectors` | `genius.connectors.v1.Connectors` |
| Settings | `bff.org_settings` | `genius.settings.v1.Settings` |
| Overview | computed from org-scoped stores | `genius.overview.v1.Overview` |

Schema is applied on BFF boot (`Open` → migrate embedded `schema.sql`). Restarting the web pod does **not** wipe these rows.

### How to work with it

**Work items**

```bash
# Create
grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"Invoice review","kind":"WORK_ITEM_KIND_HUMAN","owner":"alice"}' \
  web.geniusai.io:443 genius.workitems.v1.WorkItems/CreateWorkItem

# List / get / update / stats — same service; all org-filtered
```

**Settings** (engine + notifications per org)

```bash
grpcurl -H "Authorization: Bearer $TOKEN" -d '{}' \
  web.geniusai.io:443 genius.settings.v1.Settings/GetEngineSettings

grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"settings":{"autoExtractDecisions":true,"defaultModel":"default","minConfidenceAutoExecute":85}}' \
  web.geniusai.io:443 genius.settings.v1.Settings/UpdateEngineSettings
```

**Agents / approvals / connectors / decisions** — use existing List/Get/Update RPCs; empty lists are normal until you seed data (memory seed is no longer the production path).

### Acceptance checks

- Create a work item → `kubectl`/psql: row in `bff.work_items` with your `org_id`.
- Restart `deploy/genai-web` → `GetWorkItem` still returns the same id.
- Another org’s token cannot `Get` your id (`NotFound`).

---

## 2. Tenant isolation FND-06 (GAB-84)

### Model

**The BFF is the tenancy boundary.** lunaya-flow-runtime run/def IDs are not trusted alone. Runtime runs exposed through the BFF are recorded in `bff.runtime_run_bindings` with owning `org_id`.

| Path | Behavior |
| --- | --- |
| Product `StartProductRun` / webhooks / schedules | After runtime start, `BindRuntimeRun(org, runtimeRunId, workflowId, productRunId)` |
| Runtime proxy `StartWorkflowRun` | Binds returned run to JWT org |
| `GetWorkflowRun`, `ListReadySteps` | Lookup binding; missing or other-org → **NotFound** (no IDOR leak) |
| `DebugRun` | Requires product store; binds run ids from the stream |

**Intentionally global (platform):** actions catalog and runtime workflow **defs** (still gated by `runtime.manage`). Product workflows store per-org `runtime_def_id` pointers.

Full surface matrix: [Tenant Isolation Inventory — GenAI BFF](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21823491/Tenant+Isolation+Inventory+GenAI+BFF+FND-06).

### How to prove isolation

Seed two orgs (staging script):

```fish
# From genius-ai-api repo
./web/scripts/seed-fnd06-tenants.fish --sql-only \
  | kubectl -n genai exec -i genai-platform-postgres-1 -c postgres -- \
      env PGPASSWORD=$APP_PASS psql -h genai-platform-postgres-rw -U genai -d genai
# Then set usable password hashes (or copy from a known user) and restart genai-web for Casbin backfill.
```

As tenant A: create a work item / start a runtime run. As tenant B: `GetWorkItem` / `GetWorkflowRun` with A’s ids → **NotFound**. B’s `ListWorkItems` must not include A’s rows.

Unit tests in-repo: `go test ./internal/services/ -run Tenancy`.

### Staging deploy tip

Harbor `web:latest` may not refresh on nodes that already cached the tag. Prefer pinning the digest from the OCI workflow, or force a fresh pull. Argo `genai-web` syncing the Helm chart resets image to `tag: latest`.

---

## 3. Organization model / workforce (GAB-91)

### Vocabulary

| Concept | Meaning |
| --- | --- |
| **Department** | Org tree node (`key` unique per org) |
| **Position** | Stable seat (survives occupant change — PR-02) |
| **Actor** | `human` \| `digital` \| `external`; humans may link `user_id` → `bff.users` |
| **Assignment** | Effective-dated occupant; history preserved (never rewrite) |
| **Role contract** | Versioned mission/authority/responsibilities on a **position** (not Casbin `owner`/`admin`) |

### Permissions

| Permission | Roles |
| --- | --- |
| `workforce.read` | viewer and above |
| `workforce.manage` | owner, admin |

### ConnectRPC (`genius.workforce.v1`)

| Service | RPCs |
| --- | --- |
| `Departments` | List, Get, Create, Update |
| `Positions` | List, Get, Create, Update, **AssignPosition**, ListPositionAssignments |
| `Actors` | List, Get, Create, Update, PauseActor, ResumeActor |
| `RoleContracts` | List, Get, GetByPosition, **SaveRoleContractDraft**, **PublishRoleContract** |

### Typical flow (grpcurl)

```bash
# 1) Department
grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"key":"finance","name":"Finance"}' \
  web.geniusai.io:443 genius.workforce.v1.Departments/CreateDepartment

# 2) Position under department
grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"departmentId":"<dept-id>","key":"ar-clerk","title":"AR Clerk"}' \
  web.geniusai.io:443 genius.workforce.v1.Positions/CreatePosition

# 3) Actors (optional userId must exist in bff.users for this org)
grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"type":"human","displayName":"Alex","userId":"<user-uuid>"}' \
  web.geniusai.io:443 genius.workforce.v1.Actors/CreateActor

# 4) Assign (re-assign ends the open assignment and inserts a new row — PR-02)
grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"positionId":"<pos-id>","actorId":"<actor-id>"}' \
  web.geniusai.io:443 genius.workforce.v1.Positions/AssignPosition

grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"positionId":"<pos-id>"}' \
  web.geniusai.io:443 genius.workforce.v1.Positions/ListPositionAssignments

# 5) Role contract draft → publish (first publish marks draft version 1 in place)
grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"positionId":"<pos-id>","key":"ar-contract","displayName":"AR","mission":"Collect receivables","responsibilities":[{"key":"invoice","outcome":"Invoice posted","autonomyLevel":1}]}' \
  web.geniusai.io:443 genius.workforce.v1.RoleContracts/SaveRoleContractDraft

grpcurl -H "Authorization: Bearer $TOKEN" \
  -d '{"contractId":"<contract-id>"}' \
  web.geniusai.io:443 genius.workforce.v1.RoleContracts/PublishRoleContract
```

### Finance seed

```fish
set -x GENIUS_SEED_ORG_ID <your-org-uuid>
set -x GENIUS_POSTGRES_USERNAME …
set -x GENIUS_POSTGRES_PASSWORD …
./web/scripts/seed-finance-org.fish
```

Seeds Finance department, AR position, sample published contract, human actor + assignment.

### PR-03 helper (code)

`ValidateAccountablePosition` (Go) — active assignment must be a human actor or explicit document-triage style actor before work can be accountable to a position (used by later Work Office tickets).

---

## Quick troubleshooting

| Symptom | Likely cause |
| --- | --- |
| `FailedPrecondition` on product/workforce/runtime-run get | Postgres product store not wired |
| `AlreadyExists` on Publish (old builds) | Upgrade past `162264c` — first publish marks draft in place |
| Actor create FK error on `user_id` | User id not in `bff.users` for this org — omit `userId` or invite first |
| Cross-tenant get returns NotFound | Expected for FND-06 |
| New `:latest` image not live after CI | Pin Harbor digest or force image pull; check Argo sync |

---

## Repo doc mirrors

- `web/docs/runtime-tenancy.md`
- `web/docs/tenant-isolation-inventory.md`
