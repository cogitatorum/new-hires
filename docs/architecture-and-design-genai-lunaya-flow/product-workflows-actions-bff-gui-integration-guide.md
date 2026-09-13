# Product Workflows & Actions — BFF GUI Integration Guide

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/20054190](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/20054190)  
> Confluence page id `20054190` (exported for Genius AI hiring take-home).

---

**Audience:** GUI / frontend engineers integrating with the Genius AI BFF (`genius-ai-api` / `genai-web`) for product workflows and runtime actions.  

**Status:** as-built for staging (ConnectRPC product canvas + Lunaya Flow runtime compile).  

**Parent:** [Architecture and Design — GenAI / Lunaya Flow](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314/Architecture+and+Design+GenAI+Lunaya+Flow)  

**Related:** [Workflow Actions — Reference](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906/Workflow+Actions+Reference), [Webhooks and Event Bus — GenAI BFF](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18415660/Webhooks+and+Event+Bus+GenAI+BFF)

---

## 1. Mental model

Two layers matter for a GUI:

| Layer | Service | What the UI owns |
| --- | --- | --- |
| **Product canvas** | `genius.workflows.v1.ProductWorkflows` | Graph editor: nodes, edges, titles, handler config, publish/run UX |
| **Runtime catalog** | `genius.runtime.v1.RuntimeActions` (+ optional `RuntimeWorkflows`) | Action packages (schemas, images, builds). Prefer product RPCs for day-to-day workflow ops |

**Important:** edges define **control / dependency** topology. They do **not** automatically copy one node’s output into another. Data wiring is explicit via `config.bindings` (literal values or `fromStep` + `path`).

Publish compiles the canvas into a runtime workflow definition (`StepSpec` + `Binding`), stores `runtimeDefId` on the product workflow, and sets state to `PUBLISHED`. There is no version-history RPC; each publish mints a new runtime def id and overwrites `runtimeDefId`.

Do **not** confuse runtime actions with `genius.workitems.v1` (UI “Actions” / work items).

---

## 2. Transport, auth, and permissions

### 2.1 Connect client

- Base URL: BFF HTTP endpoint (staging cluster / local `:8090`).
- Browser: Connect over HTTP/1.1 JSON (`@connectrpc/connect-web`).
- Tools: gRPC/h2c via `grpcurl` also works.
- Content-Type for JSON Connect: `application/json`.
- Procedure paths look like `/genius.workflows.v1.ProductWorkflows/CreateWorkflow`.

### 2.2 Auth flow

1. `Auth.Login` with `{ "email", "password" }` → `accessToken`, `refreshToken` (no bearer required).
2. Persist both tokens.
3. Every other RPC: `Authorization: Bearer <accessToken>`.
4. On `Unauthenticated`: `Auth.RefreshToken` with `{ "refreshToken" }`, retry once, or send user to login.
5. `Auth.Logout` then drop tokens.

Public (no JWT): `Auth.Login`, `Auth.RefreshToken` only. `Auth.Register`** is disabled** (invite-only via authenticated `InviteUser`).

Org scope comes from JWT claims (`org_id`); stores are org-scoped.

### 2.3 Permissions (workflows / actions)

| Operation | Permission |
| --- | --- |
| Create, list (type-level), list runs, get run, list node handlers | `workflows.edit` / `workflows.read` as coded |
| Get / update / rename / duplicate / delete / bind / start run | `workflows.read` or `workflows.edit` (resource `workflow/{id}` also allowed) |
| Publish | `workflows.publish` |
| Runtime action build/list/get/delete | `runtime.manage` |

Typical roles: owner/admin → publish + runtime; operator → edit without publish; viewer → read-only.

---

## 3. Product workflow schema (create / update)

### 3.1 Core messages (Connect JSON = protojson camelCase)

```json
{
  "id": "optional-on-create",
  "name": "http-request-get",
  "triggerSummary": "Manual GET demo",
  "nodes": [ /* WorkflowNode */ ],
  "edges": [ /* WorkflowEdge */ ],
  "runtimeDefId": "set-by-publish-or-bind",
  "state": "WORKFLOW_PUBLISH_STATE_DRAFT",
  "stats": {},
  "updatedAt": "RFC3339"
}
```

#### `WorkflowNode`

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable canvas id; becomes runtime step id. Must be unique in the graph. |
| `kind` | enum | `NODE_KIND_TRIGGER`, `CONDITION`, `AI`, `HUMAN`, `APPROVAL`, `ACTION`, `END`, `BRANCH` |
| `title` | string | Display name |
| `handler` | string | Palette / action name (`HttpRequest`, `Set`, `Branch`, `Add`, …) |
| `config` | object (`Struct`) | Handler-specific fields + optional `bindings` array |

#### `WorkflowEdge`

| Field | Type | Notes |
| --- | --- | --- |
| `fromNode` | string | Source node id (**not** `from`) |
| `toNode` | string | Target node id (**not** `to`) |
| `label` | string | Branch arm: `"true"` / `"false"` for If, or Switch case id. Empty = unconditional |

#### Publish state

- `WORKFLOW_PUBLISH_STATE_DRAFT`
- `WORKFLOW_PUBLISH_STATE_PUBLISHED`

### 3.2 Create vs update payloads

`CreateWorkflow` request fields:

- `name` (required in practice for UX)
- `triggerSummary`
- `nodes`, `edges`

Starts as `DRAFT` with empty `runtimeDefId`.

`UpdateWorkflow` request fields:

- `id` (required)
- `triggerSummary` — applied when non-empty
- `nodes`, `edges` — **replaced only when the arrays are non-empty**

Rename uses `RenameWorkflow` (`id`, `name`), not Update.

### 3.3 Minimal valid canvas example

```json
{
  "name": "http-request-get",
  "triggerSummary": "Manual GET httpbin",
  "nodes": [
    {
      "id": "trigger",
      "kind": "NODE_KIND_TRIGGER",
      "handler": "manual",
      "title": "Manual Trigger"
    },
    {
      "id": "http",
      "kind": "NODE_KIND_ACTION",
      "handler": "HttpRequest",
      "title": "GET httpbin",
      "config": {
        "method": "GET",
        "url": "https://httpbin.org/get",
        "headers": { "Accept": "application/json" },
        "query": { "source": "genai-demo" },
        "responseFormat": "json"
      }
    },
    {
      "id": "done",
      "kind": "NODE_KIND_ACTION",
      "handler": "NoOp",
      "title": "Done"
    },
    {
      "id": "end",
      "kind": "NODE_KIND_END",
      "handler": "end",
      "title": "End"
    }
  ],
  "edges": [
    { "fromNode": "trigger", "toNode": "http" },
    { "fromNode": "http", "toNode": "done" },
    { "fromNode": "done", "toNode": "end" }
  ]
}
```

Repo example: `web/examples/product-workflows/http-request-get.json`.

### 3.4 What publish compiles

Executable nodes (`ACTION` / `BRANCH` / `AI` with a known handler) become runtime steps:

| Product | Runtime |
| --- | --- |
| `node.id` | `StepSpec.id` |
| `node.title` | `StepSpec.name` |
| `node.handler` | `StepSpec.action` (apps like Slack expand to `HttpRequest`) |
| `config` + `config.bindings` | `StepSpec.bindings` |
| Incoming edges from exec nodes | `StepSpec.depends_on` |
| Edge `label` from `BRANCH` | `StepSpec.when` (Argo expression) |

Triggers and End are skipped. At least one executable node is required to publish.

---

## 4. Wiring node outputs into later inputs

### 4.1 Runtime binding model

Canonical types (Lunaya Flow runtime):

```text
Binding { param, source }
Source oneof:
  literal | from_step { step_id, path } | file | secret | context
```

**GUI phase-1 support:** use **literal** and **fromStep** only. File / secret / context sources are rejected by the engine today.

### 4.2 Where the GUI stores bindings

Put them on the **downstream** node under `config.bindings` (JSON array). Almost every palette `configSchemaJson` includes a `bindings` array property.

Preferred product shorthand (used in examples):

```json
{
  "param": "items",
  "fromStep": "filter",
  "path": "items"
}
```

```json
{
  "param": "a",
  "literal": 2
}
```

Nested proto-shaped form also accepted:

```json
{
  "param": "in1",
  "source": {
    "fromStep": { "stepId": "add", "path": "result" }
  }
}
```

Rules:

- `param` is required (must match the action **input** schema property).
- Exactly one of `source` | `literal` | `fromStep`.
- `fromStep` = upstream **node id** (same as `WorkflowNode.id`).
- `path` = JSON Pointer into that step’s **output document** (leading `/` optional). Examples: `"result"`, `"result/items"`, `""` / `"/"` = whole output.
- For many builtins, non-`bindings` config keys (`url`, `method`, `assignments`, …) compile to **literal** bindings. Explicit `bindings` win on duplicate `param`.

### 4.3 Chaining example (Add → Mul)

```json
{
  "id": "add",
  "kind": "NODE_KIND_ACTION",
  "handler": "Add",
  "config": {
    "bindings": [
      { "param": "a", "literal": 2.0 },
      { "param": "b", "literal": 3.0 }
    ]
  }
},
{
  "id": "mul",
  "kind": "NODE_KIND_ACTION",
  "handler": "Mul",
  "config": {
    "bindings": [
      { "param": "in1", "fromStep": "add", "path": "result" },
      { "param": "in2", "literal": 4.0 }
    ]
  }
}
```

Edge `{ "fromNode": "add", "toNode": "mul" }` only ensures Mul waits on Add. Without the `fromStep` binding, Mul would not see Add’s `result`.

### 4.4 Transform chain example

```json
{
  "id": "blend",
  "handler": "Code",
  "config": {
    "source": "(function(){ return { items: input.items }; })()",
    "bindings": [
      { "param": "input", "fromStep": "seed", "path": "data" }
    ]
  }
},
{
  "id": "filter",
  "handler": "Filter",
  "config": {
    "field": "status",
    "op": "eq",
    "value": "active",
    "bindings": [
      { "param": "items", "fromStep": "blend", "path": "result/items" }
    ]
  }
}
```

Full stress sample: `web/examples/product-workflows/platform-stress-test.json`.

### 4.5 Branch control vs data bindings

For `NODE_KIND_BRANCH` / handler `Branch`:

- Config (`mode` ∈ `if|switch`, plus `op`/`left`/`right` or `value`/`cases`/`default`) becomes literal bindings on the Branch action.
- **Every** edge leaving a branch **must** set `label` (`"true"` / `"false"` or case id).
- Compiler emits a `when` expression on successors, e.g. comparing `tasks['branch'].outputs...selected` to the label.
- Branch labels are **control flow**, not data copy. If a branch arm needs upstream data, still add `config.bindings` on the target node.

### 4.6 GUI authoring rules of thumb

1. When the user draws a wire for **data**, write/update a `bindings[]` entry on the target node (`param` from target input schema, `fromStep`/`path` from source output schema).
2. When the user draws a wire for **order / branch**, write an `edges[]` entry (and `label` if from Branch).
3. Validate `param` against `RuntimeAction.inputSchema` / palette `configSchemaJson`; validate `path` against upstream `outputSchema`.
4. Keep node ids stable across edits so published bindings keep resolving.
5. Credentials: put `credentialId` in config when needed; Publish resolves secrets and strips `credentialId` before runtime.

---

## 5. ProductWorkflows RPC map (GUI checklist)

Connect service: `genius.workflows.v1.ProductWorkflows`

| RPC | Request highlights | Response / notes |
| --- | --- | --- |
| `ListNodeHandlers` | empty | Palette: handler id, title, group, `configSchemaJson` |
| `CreateWorkflow` | name, triggerSummary, nodes, edges | New `ProductWorkflow` (DRAFT) |
| `GetWorkflow` | id | Full graph |
| `ListWorkflows` | page | Page of workflows |
| `UpdateWorkflow` | id + partial fields | Graph replace rules above |
| `RenameWorkflow` | id, name |  |
| `DuplicateWorkflow` | id, optional name | New id, DRAFT, clears `runtimeDefId` |
| `DeleteWorkflow` | id |  |
| `PublishWorkflow` | id | Compiles → runtime CreateWorkflowDef; sets `runtimeDefId`, PUBLISHED |
| `BindRuntimeDef` | id, runtimeDefId | Manual link without republish |
| `StartRun` | workflowId | Needs `runtimeDefId`; returns `ProductWorkflowRun` |
| `GetRun` / `ListRuns` | run id / workflowId + page | Refreshes status from runtime |
| `GetWorkflowStats` | id | Aggregate stats |

Suggested UI loop:

1. Login → store tokens
2. `ListNodeHandlers` → render palette / forms
3. Optionally `ListActions` / `BuildAction` for custom catalog actions (`runtime.manage`)
4. `CreateWorkflow` / `UpdateWorkflow` while editing
5. `PublishWorkflow` (requires runtime URL + publish perm)
6. `StartRun` → poll `GetRun` / `ListRuns`
7. Show publish errors (invalid bindings, missing branch labels, empty executable graph) inline on the offending nodes

Webhook-triggered runs (no JWT): `POST /hooks/v1/{path}` with webhook secret — see Webhooks doc. Canvas still publishes with a Webhook trigger node first.

---

## 6. Runtime actions (catalog) for the GUI

Service: `genius.runtime.v1.RuntimeActions` (needs `runtime.manage`)

| RPC | Purpose |
| --- | --- |
| `ListActions` | Catalog rows for picker |
| `GetAction` | `name` → schemas, image, build status |
| `BuildAction` | `gitUrl`, `branch` → register/rebuild |
| `DeleteAction` | by name |
| `SubscribeBuildEvents` | stream build progress |

`RuntimeAction` fields include: `name`, `gitUrl`, `branch`, `description`, `imageRef`, `buildStatus`, `inputSchema`, `outputSchema`, `packagePath`.

### How actions relate to nodes

1. **Builtins** from `ListNodeHandlers` (`HttpRequest`, `Set`, `Filter`, `Branch`, …): node `handler` becomes runtime `StepSpec.action` (or expands for apps).
2. **Catalog packages** (e.g. sample `Add` / `Mul`): same — `handler` must equal action **name**; bindings map to **input** schema; `fromStep.path` must address upstream **output** schema.
3. Product workflow RPCs do not build images; use RuntimeActions for that ops surface.

---

## 7. Validation constraints the GUI should preflight

Before publish (and preferably on blur / save):

- Edge endpoints use `fromNode` / `toNode` and reference existing node ids.
- At least one executable node (`ACTION` / `BRANCH` / `AI` with known handler).
- `BRANCH` handler is `Branch`; `mode` is `if` or `switch`; every outgoing edge has non-empty `label`.
- Handler-specific config: e.g. HttpRequest needs `method`+`url`; Code needs `source`; StopAndError needs `message`; ExecuteWorkflow needs `workflowId`.
- Each binding has `param` and exactly one of `literal` / `fromStep` (+ `path`).
- No duplicate `param` on the same node after merge.
- `fromStep` targets an upstream executable node that will exist after compile.
- Stub handlers (`stickyNote`, etc.) are non-executable decoration only.

Publish will still enforce schema against registered actions on the runtime side.

---

## 8. Example client snippets

### Login + create (Connect JSON)

```http
POST /genius.auth.v1.Auth/Login
Content-Type: application/json

{"email":"owner@example.com","password":"..."}
```

```http
POST /genius.workflows.v1.ProductWorkflows/CreateWorkflow
Authorization: Bearer <accessToken>
Content-Type: application/json

{ "name": "...", "triggerSummary": "...", "nodes": [...], "edges": [...] }
```

```http
POST /genius.workflows.v1.ProductWorkflows/PublishWorkflow
Authorization: Bearer <accessToken>
Content-Type: application/json

{ "id": "<workflowId>" }
```

```http
POST /genius.workflows.v1.ProductWorkflows/StartRun
Authorization: Bearer <accessToken>
Content-Type: application/json

{ "workflowId": "<workflowId>" }
```

### Local helper

`web/examples/product-workflows/client.fish` exercises login, create from JSON, list, publish, start run, and action list/build via grpcurl.

---

## 9. Proto / code map (for implementers)

| Concern | Location |
| --- | --- |
| Product workflow RPCs | `web/proto/genius/workflows/v1/workflows.proto` |
| Product handlers / compile | `web/internal/services/workflows.go`, `workflow_compile.go` |
| Palette descriptors | `web/internal/services/palette_*.go` |
| Runtime proxy RPCs | `web/proto/genius/runtime/v1/runtime.proto` |
| Runtime Binding / StepSpec | `runtime/proto/genai/workflows/v1/workflow.proto` |
| Examples | `web/examples/product-workflows/*.json` |
| Auth / CORS notes | `web/README.md` |

---

## 10. FAQ

**Q: If I connect node A → node B on the canvas, does B receive A’s output?**  

A: No. That edge only orders / depends. Add `config.bindings` on B with `fromStep: "A"` and the output `path`.

**Q: Why did publish fail with no executable nodes?**  

A: Only Trigger/End/sticky stubs are present, or handlers are unknown stubs.

**Q: Why do branch arms fail compile?**  

A: Missing `label` on edges leaving the Branch node.

**Q: Where do versions live?**  

A: Each publish creates a new runtime def name (`pwf-…`) and overwrites `runtimeDefId`. There is no product ListVersions API yet; use `BindRuntimeDef` only for deliberate manual linking.

**Q: Can the GUI talk to RuntimeWorkflows directly?**  

A: Yes for ops/debug, but day-to-day canvas create/update/publish/run should stay on `ProductWorkflows` so org ACL, compile, credentials, and stats stay consistent.
