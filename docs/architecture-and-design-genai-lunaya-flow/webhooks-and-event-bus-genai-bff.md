# Webhooks and Event Bus — GenAI BFF

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18415660](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18415660)  
> Confluence page id `18415660` (exported for Genius AI hiring take-home).

---

Audience: engineers integrating with Genius AI BFF webhooks and the NATS event plane.

Status: as-built for staging (2026-08-30). Parent: Architecture and Design — GenAI / Lunaya Flow.

**Topics / pub-sub matrix:** see [Events and NATS Topics — GenAI](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397535/Events+and+NATS+Topics+GenAI) for every JetStream subject, publishers, subscribers, and Casbin vs NATS auth.

## Overview

Webhook ingress and EventRules are **independent** ways to start a product run. A webhook always starts its bound workflow and then emits `webhook.accepted`. EventRules only fire if you create a matching rule; that rule starts `trigger_workflow_id` (typically another workflow). They are not two stages of the same run — pointing a rule at the same workflow as the webhook route will start it twice.

| **Path** | **Entry** | **Outcome** |
| --- | --- | --- |
| **Webhook trigger** | `POST /hooks/v1/{path}` | Always starts the route’s published workflow; then emits `webhook.accepted` |
| **Event bus** | JetStream subjects `events.org.{orgId}.bus.{type}` | Durable org events; Publish/Subscribe/List via Connect |
| **EventRules** | JetStream consumer in the BFF | Optional: matching events start `trigger_workflow_id` (separate from the webhook route) |

Clients never connect to NATS. The BFF holds credentials and enforces org/RBAC.

```
External caller
  │  POST /hooks/v1/{path} + secret
  ▼
BFF webhook handler
  │  1) startProductRun(route.workflow_id)  ← always: the webhook-bound workflow
  │  2) publish BusEvent type=webhook.accepted (audit / fan-out signal)
  ▼
JetStream EVENTS
  │
  ├─► Connect EventBus (List / Subscribe / Publish)   ← observers only
  │
  └─► EventRules evaluator (optional, separate config)
        if when_expression matches (e.g. webhook.accepted)
        → startProductRun(rule.trigger_workflow_id)
        → usually a *different* workflow; not a second start of the webhook route
```

## Webhook triggers

### Publish-time setup

1. Canvas workflow includes a trigger node: `handler=webhook` with config `path`, `method` (POST), and `secret` (≥16 chars).
2. `PublishWorkflow` compiles steps to a runtime def, upserts `bff.workflow_webhook_routes` (path → org/workflow, **hashed** secret), and returns the workflow with secret redacted (`secretConfigured: true`).

### Invoke

```http
POST https://web.geniusai.io/hooks/v1/{path}
Content-Type: application/json
X-Webhook-Secret: <plaintext secret>
# or: Authorization: Bearer <plaintext secret>

{"any":"json body"}
```

| **Response** | **Meaning** |
| --- | --- |
| **202** | Accepted; body includes product `id`, `workflowId`, `runtimeRunId`, `status` |
| **404** | Unknown path **or** wrong secret (no existence leak) |
| **503** | Runtime unavailable |

Example product workflow: `examples/product-workflows/webhook-set-noop.json`.

### Notes

- Paths are normalized (no leading slash in route table; URL uses `/hooks/v1/...`).
- One enabled route per workflow; path is globally unique.
- Body is not currently mapped into workflow inputs (trigger = “fire run”).

## Event bus (NATS JetStream)

### Topology

- Stream `EVENTS`: subjects `events.>` (MaxAge 7d, dedupe window 2m).
- Stream `EVENTS_DLQ`: subjects `dlq.>` (outside `events.>` to avoid overlap).
- Platform subjects (runtime): e.g. `events.platform.actions.build.v1`, `events.platform.workflows.run.v1`. Full topic map: [Events and NATS Topics — GenAI](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397535/Events+and+NATS+Topics+GenAI).
- Org bus: `events.org.{orgId}.bus.{sanitizedType}`.

Type sanitization: lowercased; `/` → `.`; unsafe chars stripped (see runtime `pkg/bus.SanitizeType`).

### Domain events emitted by the BFF

| **Type** | **When** |
| --- | --- |
| `webhook.accepted` | Webhook started a run |
| `workflow.published` | Successful `PublishWorkflow` |
| `credential.created` / `credential.deleted` | Credential lifecycle |
| `rule.fired` | EventRules evaluator started a run |
| *(custom)* | `EventBus/PublishEvent` or rule `emit_type` |

Payloads are `genius.bus.v1.BusEvent` (protojson) with headers `Event-Id`, `Org-Id`, `Schema`, `Correlation-Id`.

### Connect API (`genius.bus.v1.EventBus`)

Requires JWT + permissions (`events.read` / `events.publish`).

- **PublishEvent** — writes to the caller’s org subject.
- **ListEvents** / **GetEvent** — recent org messages from JetStream (bounded fetch).
- **SubscribeEvents** — live stream; org ACL via subject filter; optional `type_prefix` / `correlation_id` filtered in-process.
- **GetEventChain** — nodes sharing a `correlation_id`.

### Build events

`RuntimeActions/SubscribeBuildEvents` bridges JetStream `events.platform.actions.build.v1` into the BFF Connect stream (`runtime.manage`).

## EventRules → Argo

Rules are org-scoped, stored in `bff.event_rules`, evaluated by a durable JetStream consumer `bff-event-rules` on `events.org.>`.

### Rule shape (v1)

| **Field** | **Meaning** |
| --- | --- |
| `when_kind` | Must be `EVENT_RULE_WHEN_KIND_EVENT` |
| `when_expression` | Exact event type after sanitize (e.g. `webhook.accepted`) |
| `trigger_workflow_id` | Published product workflow with `runtime_def_id` |
| `emit_type` | Optional extra bus event after fire |
| `enabled` | Toggles matching |
| `fired_count` | Incremented on success |

### Behaviour

1. Decode `BusEvent`; resolve org from `Org-Id` header or subject.
2. Skip type `rule.fired` (loop guard).
3. For each enabled matching rule: `StartProductRun(trigger_workflow_id)` → Argo. Does not re-run the webhook route’s workflow unless that id is the rule target.
4. Publish `rule.fired` (and `emit_type` if set) with attributes `rule_id`, `workflow_id`, `run_id`, `event_id`, …

Connect service: `genius.bus.v1.EventRules` (`event_rules.write` / `events.read`).

### Example chain

1. Publish workflow **A** with webhook path `demo/orders`.
2. Publish workflow **B** (target automation).
3. Create rule: `when_expression=webhook.accepted`, `trigger_workflow_id=B`.
4. `POST /hooks/v1/demo/orders` → one run of **A** + `webhook.accepted` → evaluator starts one run of **B** + `rule.fired`. Workflow A is not re-started by the rule.

## Permissions (RBAC)

| **Permission** | **Used for** |
| --- | --- |
| `events.read` | List/Get/Subscribe events; Get/List rules |
| `events.publish` | PublishEvent |
| `event_rules.write` | Create/Update/Delete/Enable rules |
| `workflows.publish` / `workflows.edit` | Publish workflows; StartRun |
| `runtime.manage` | SubscribeBuildEvents |

## Ops / staging

- BFF env: `GENIUS_NATS_URL`, `GENIUS_NATS_USERNAME`, `GENIUS_NATS_PASSWORD` (secret `genai-platform-nats-auth`).
- NATS Helm auth must use unquoted env vars: `user: << $NATS_USERNAME >>` (chart `<< >>` syntax).
- Logs: `event bus: nats (…)`, `event rules evaluator: consuming events.org.>`, `fired rule=…`.
- Inspect streams: `nats stream ls` / `stream info EVENTS` (via nats-box with app credentials).

## Related code

- BFF: `web/internal/server/hooks.go`, `web/internal/services/workflows.go`, `web/internal/events/`, `web/internal/services/bus.go`
- Runtime bus helpers: `runtime/pkg/bus`
- Example webhook workflow: `examples/product-workflows/webhook-set-noop.json`
