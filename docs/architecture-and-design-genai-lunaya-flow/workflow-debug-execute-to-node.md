# Workflow Debug — Execute to Node

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/20480011](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/20480011)  
> Confluence page id `20480011` (exported for Genius AI hiring take-home).

---

**Audience:** engineers integrating the workflow canvas or CLI against GeniusAI GenAI / Lunaya Flow.

**Status:** as-built for staging (BFF `ExecuteToNode` + runtime `DebugRun` stop-after / pins).

**Last reviewed:** 2026-09-06.

## What problem this solves

Publishing a product workflow creates a durable runtime definition, may sync webhooks/schedules, and is the path for production `StartRun` (Argo). For day-to-day authoring you need something closer to n8n **Test step / run to here**: execute a selected canvas node and its upstream ancestors, inspect streamed outputs, and optionally pin ancestor data — **without** flipping the workflow to `PUBLISHED`.

## Concepts

| Term | Meaning |
| --- | --- |
| Canvas node | Product graph node id (BFF `ProductWorkflow.nodes[].id`). Compile keeps this id as the runtime step id. |
| Run to here | Execute the **ancestor closure** of the target (DependsOn + `fromStep` bindings), inclusive, then stop. Downstream and sibling branches outside that closure are skipped. |
| Pin | Supply a JSON object as a step’s output without invoking its action container. Dependents resolve bindings against the pin. |
| Ephemeral def | Runtime workflow def created only for the debug session (`debug/{workflowId}/{ts}`). Product `runtime_def_id` / publish state are **not** updated. |
| JSON Pointer | Binding `path` format (RFC 6901), e.g. `/result`. Empty or `/` = whole prior output. |

## Architecture flow

| Step | Component | What happens |
| --- | --- | --- |
| 1 | Client | Calls product `ExecuteToNode(workflowId, nodeId, pinnedOutputs?)` with `workflows.edit`. |
| 2 | BFF | Loads canvas; validates; `compileProductToRuntimeSteps`; injects credentials (same as publish). |
| 3 | BFF → Runtime | Creates ephemeral `CreateWorkflowDef` (does not set product publish fields). |
| 4 | Runtime | `DebugRun` with `stopAfterStepId` + pins: skip non-ancestors, apply pins, invoke remaining ancestors then target in containers, stream events. |
| 5 | Client | Receives stream: run/step started/finished/failed + JSON outputs (+ `pinned=true` when applicable). |

Debug uses the **daemon container path** (same action images as catalog `image_ref`), not Argo. Actions must already be built (`BuildAction`) or invoke fails with missing image.

## Product RPCs (BFF)

Service: `genius.workflows.v1.ProductWorkflows`. Authz: `workflows.edit` (operators can self-test; **not** `runtime.manage`).

| RPC | Type | Purpose |
| --- | --- | --- |
| `PreviewCompile` | Unary | Validate + compile canvas → list of runtime steps / depends\_on. No def created, no publish. |
| `ExecuteToNode` | Server stream | Compile → ephemeral def → run-to-here; stream progress and outputs. |
| `ResolveNodeBindings` | Unary | Dry-resolve one node’s input JSON from an optional upstream output map (no containers). |

### ExecuteToNode request

```json
{
  "workflowId": "<product-workflow-id>",
  "nodeId": "set",
  "pinnedOutputs": {
    "wait": { "ok": true }
  }
}
```

- `nodeId` must be an **executable** canvas node (action / branch / AI). Triggers and end nodes are rejected.
- `pinnedOutputs` keys are canvas node ids (same as compiled step ids).
- Pin values must be JSON **objects** (Struct).

### Streamed event fields

| Field | Notes |
| --- | --- |
| `kind` | e.g. `DEBUG_RUN_EVENT_KIND_STEP_FINISHED` |
| `runId` / `runtimeDefId` | Ephemeral run and def ids |
| `nodeId` / `stepId` | Same id after compile |
| `output` | Step output object when finished |
| `pinned` | `true` if output came from `pinnedOutputs` |
| `error` | Set on step/run failure |

## Runtime RPCs (daemon / BFF proxy)

Daemon: `genai.workflow.v1.Workflows/DebugRun`. BFF proxy: `genius.runtime.v1.RuntimeWorkflows/DebugRun` (requires `runtime.manage`).

| Field | Behavior |
| --- | --- |
| `defId` / `defName` | Existing saved runtime def |
| `stopAfterStepId` | Empty = full DAG (legacy). Set = ancestor closure only, then finish. |
| `pinnedOutputs` | Map step id → Struct; finish without container invoke |

Also exposed on the BFF runtime adapter: `ListReadySteps(runId)` for inspecting unblocked pending steps on an existing run (advanced / future step-through).

### Publish / StartRun

- Sets `PUBLISHED` + `runtime_def_id`
- May sync webhook / schedule routes
- Execution via Argo
- Needs `workflows.publish` then `workflows.edit` to run

### ExecuteToNode

- Does **not** change publish state
- Does **not** sync webhook / schedule
- Ephemeral def + daemon containers
- Needs `workflows.edit` only

## How ancestor closure works

1. Start from `stopAfterStepId` / `nodeId`.
2. Walk predecessors via explicit `depends_on` and every binding `fromStep.stepId`.
3. All other steps in the def are marked **skipped** so they never become ready.
4. Apply pins first (so dependents unlock), then invoke remaining pending steps in ready order until the target finishes.
5. Run status becomes finished; siblings/downstream outside the closure never run.

**Diamond example:** `root → left`, `root → right`, both merge into `merge`. Stopping at `merge` runs all four. Stopping at `left` runs only `root` + `left`; `right` and `merge` are skipped.

## Feeding Code (and other) nodes from upstream

Data does **not** become process environment variables. Wire prior outputs with bindings:

```json
{
  "param": "input",
  "source": { "fromStep": { "stepId": "previous-node-id", "path": "/" } }
}
```

Inside the `Code` action, that value is the JS global `input`. Paths use **JSON Pointer**.

## CLI examples

From `web/examples/product-workflows/`:

```fish
./execute-to-node.fish wait-then-set.json set
./execute-to-node.fish wait-then-set.json set --pin wait '{"ok":true}'

# or via client.fish after CreateWorkflow:
./client.fish workflow preview   # prompts for workflow id
./client.fish workflow debug <workflow_id> <node_id>
```

## Limits and non-goals (current)

- No canvas UI buttons yet (API-first).
- No interactive pause / step-through / “run from here” without ancestors.
- No auto-build of missing action images.
- Ephemeral defs are not aggressively GC’d yet (name prefix `debug/`); product publish state remains untouched.
- Do not confuse palette action `DebugHelper` with this debug control plane.

## Related

- [Architecture and Design — GenAI / Lunaya Flow](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314/Architecture+and+Design+GenAI+Lunaya+Flow)
- [GenAI Publish and Run Sequence](https://geniusaidubai.atlassian.net/wiki/spaces/G/whiteboard/18415622) — production publish → Argo path
- [Workflow Actions — Reference](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906/Workflow+Actions+Reference)
- Repo: `web/README.md` (Debug without publish), `web/examples/product-workflows/execute-to-node.fish`
