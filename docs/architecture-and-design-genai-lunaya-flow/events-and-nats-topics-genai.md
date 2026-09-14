# Events and NATS Topics — GenAI

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397535](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397535)  
> Confluence page id `21397535` (exported for Genius AI hiring take-home).

---

**Audience:** engineers working on GenAI BFF, runtime, or integrations. **Status:** as-built for staging (2026-09-07); platform subjects only (no dual-publish). **Parent:** [Architecture and Design — GenAI / Lunaya Flow](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314/Architecture+and+Design+GenAI+Lunaya+Flow). Related: [Webhooks and Event Bus — GenAI BFF](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18415660/Webhooks+and+Event+Bus+GenAI+BFF) (webhook ingress + EventRules how-to).

This page is the **source of truth for NATS JetStream subjects**: what exists, who publishes, who may consume, and how authorization actually works (broker vs application).

## 1. Overview

The implemented event plane is **NATS JetStream** (not Kafka). Two in-cluster services hold the shared NATS credentials and talk to the broker:

- **genai-runtime** — publishes platform action-build and workflow-run events; exposes a low-level `Events.Subscribe` RPC.
- **genai-web (BFF)** — publishes org-scoped product `BusEvent`s; serves Connect EventBus / EventRules APIs; durable consumer for EventRules.

External clients and the UI **never connect to NATS**. They use Connect RPCs on the BFF (or runtime proxy routes the BFF exposes).

```
┌─────────────┐     Connect / hooks      ┌──────────────┐   NATS user genai    ┌────────────┐
│ UI / API /  │ ───────────────────────► │  genai-web   │ ◄──────────────────► │   NATS     │
│ webhooks    │                          │    (BFF)     │   JetStream EVENTS   │ JetStream  │
└─────────────┘                          └──────┬───────┘                      └─────▲──────┘
                                                │ proxy RPCs                         │
                                                ▼                                    │
                                         ┌──────────────┐                            │
                                         │ genai-runtime│ ───────────────────────────┘
                                         │   (daemon)   │   same NATS user
                                         └──────────────┘
```

## 2. Infrastructure

| **Item** | **Staging / cluster** |
| --- | --- |
| Broker | Helm chart dependency on NATS (JetStream file store). In-cluster URL `nats://nats:4222`. |
| Auth secret | `genai-platform-nats-auth` — keys `username` / `password`. Single shared user (typically `genai`). |
| Client env | BFF: `GENIUS_NATS_*`. Runtime: `GENAI_NATS_*` (or `nats.*` in `genai.yaml`). |
| Streams (created at startup) | `EVENTS` subjects `events.>` (7d retention, 2m dedupe). `EVENTS_DLQ` subjects `dlq.>` (30d). |

**Broker ACLs:** there are **no** NATS publish/subscribe permission lists per service or org. Both BFF and runtime use the same credential and can pub/sub the entire `events.>` tree. Tenant isolation is **application-level** (subject naming + JWT org + Casbin on BFF RPCs).

## 3. Subject taxonomy

### 3.1 Stream patterns

| **Pattern** | **Stream** | **Purpose** |
| --- | --- | --- |
| `events.>` | `EVENTS` | All primary events |
| `dlq.>` | `EVENTS_DLQ` | Dead-letter (helper exists; not wired from rule consumers today) |
| `events.org.{orgId}.>` | under `EVENTS` | Org-scoped product bus tree |
| `events.org.{orgId}.bus.{type}` | under `EVENTS` | Canonical product bus subject for one event type |

`{type}` is sanitized: lowercase, `/`→`.`, strip unsafe chars, max 128 (`SanitizeType` in `runtime/pkg/bus`).

### 3.2 Platform subjects (cluster / runtime)

| **Subject** | **Publisher** | **Schema / payload** | **Intended subscribers** | **Notes** |
| --- | --- | --- | --- | --- |
| `events.platform.actions.build.v1` | Runtime `ActionsHandler` (ActionBuild progress) | `genai.actions.v1.ActionBuildEvent` (protojson). Header `Schema`=same. | BFF `RuntimeActions.SubscribeBuildEvents`; any runtime `Events.Subscribe` client | Build progress subject |
| `events.platform.workflows.run.v1` | Runtime `WorkflowsHandler` (Argo run lifecycle) | `genai.workflows.v1.WorkflowRunEvent` (protojson) | No dedicated BFF consumer in-repo; consume via runtime `Events.Subscribe` or a custom durable | Kinds: RUN\_STARTED, STEP\_\*, RUN\_FINISHED, RUN\_FAILED |
| `events.platform.workflows.run.logs.v1` | Fluent Bit (via runtime HTTP ingest) | `genai.workflows.v1.WorkflowRunLogChunk` (protojson). Header `Schema`=same. | BFF `RuntimeWorkflows.SubscribeRunLogs` gated by topic ACL | Constant `SubjectWorkflowsRunLogs` |

### 3.3 Product org bus subjects

Shape: `events.org.{orgId}.bus.{sanitizedType}`

Payload: `genius.bus.v1.BusEvent` (protojson). Header `Schema`=`genius.bus.v1.BusEvent`.

| **Event type (suffix)** | **Publisher** | **When** | **Typical attrs** |
| --- | --- | --- | --- |
| *any* client type | BFF `EventBus.PublishEvent` | API caller with `events.publish` | Caller-defined; source defaults `INTERNAL` |
| `workflow.published` | BFF on `PublishWorkflow` | After successful publish | `workflow_id`, `runtime_def_id` |
| `webhook.accepted` | BFF webhook ingress | After starting the route’s published workflow | `workflow_id`, `run_id`, `runtime_run_id`, `path` |
| `credential.created` / `credential.deleted` | BFF credentials CRUD | Create / delete credential | Credential identifiers |
| `rule.fired` | BFF EventRules evaluator | After a matching rule starts a workflow | Rule / workflow ids (rules cannot match this type — loop guard) |
| Custom `EventRule.emit_type` | BFF EventRules evaluator | Optional extra emit after rule fire | Configured by the rule |

### 3.4 DLQ

Helper `PublishToDLQ` publishes to `dlq.{originalSubject}` with header `Original-Subject`. **No in-repo consumer currently calls this** after MaxDeliver / Nak on rule failures.

### 3.5 Message headers

| **Header** | **Meaning** |
| --- | --- |
| `Event-Id` | Stable id; also used as NATS `Nats-Msg-Id` for dedupe |
| `Schema` | Payload schema name |
| `Org-Id` | Org UUID when applicable |
| `Correlation-Id` | Chain / correlation |
| `Produced-At` | Producer timestamp |
| `Content-Type` | `application/protobuf+json` |

## 4. Who may publish / subscribe

### 4.1 At the broker (NATS)

| **Identity** | **Publish** | **Subscribe** |
| --- | --- | --- |
| NATS user `genai` (BFF + runtime pods) | All `events.>` and `dlq.>` (no ACL restriction) | All of the above |
| UI / external apps | None (no NATS credentials) | None |

### 4.2 At the BFF (Casbin + JWT org)

Product EventBus / EventRules go through Connect. JWT carries `OrgID`; subjects are always under that org for the org bus.

#### Capability roots (coarse)

| **Permission** | **RPC / surface** | **Roles** |
| --- | --- | --- |
| `events.publish` | Org-bus publish (concrete `events.org.{orgId}.bus.{type}`) | owner, admin, operator |
| `events.read` | Org-bus list/get/subscribe (`events.org.{orgId}.>`) | owner, admin, operator, **viewer** |
| `event_rules.write` | Create / Update / Delete / SetEnabled EventRule | owner, admin only |
| `runtime.manage` | Still allows `SubscribeBuildEvents` (admin path) | owner, admin |

`events.read` / `events.publish` do **not** grant platform subjects (`events.platform.…`).

#### Topic Role paths (NATS-mirror)

Role permissions may also use a **separate** grammar (never mixed into resource path compilation):

```text
topic.<nats.subject.or.filter>.<read|publish>
```

- Prefix `topic.` is required (Casbin object uses `topic:` + subject).
- NATS wildcards in the subject: `*` (one token), `>` (rest; must be final subject token).
- Subscribe requests may pass a **wildcard filter**; authz allows only if the grant **covers** the filter (filter ⊆ grant).

Examples: `topic.events.platform.workflows.run.>.read`, `topic.events.platform.workflows.run.logs.v1.read`, `topic.events.org.*.bus.>.read`.

| **Surface** | **Authz** |
| --- | --- |
| `EventBus` publish/list/subscribe/get | Capability org-bus **or** matching `topic.…` grant |
| `SubscribeBuildEvents` | `topic.events.platform.actions.build.v1.read` **or** `runtime.manage` |
| Agent seed | `topic.events.platform.workflows.run.>.read` (run + future logs) |

`GetResourceTree` returns `topic_permission_hints` with example strings for IAM UI.

**Approver** has neither `events.read` nor `events.publish` nor platform topic grants.

Domain publishers inside the BFF (publish workflow, webhook, credentials, rules) use the BFF’s NATS client directly — they are not gated by `events.publish` on each emit; callers are gated by the RPC that triggers them (e.g. publish workflow authz).

### 4.3 Durable / service consumers

| **Consumer** | **Filter** | **Who** | **Auth model** |
| --- | --- | --- | --- |
| `bff-event-rules` | `events.org.>` (all orgs) | BFF EventRules evaluator | Same shared NATS user; rule rows are org-scoped in Postgres |
| Ephemeral EventBus subscribe/list | `events.org.{jwtOrgId}.>` | BFF on behalf of user | `events.read` **or** covering `topic.…` grant + JWT org |
| SubscribeBuildEvents | `events.platform.actions.build.v1` | BFF on behalf of user | Topic grant **or** `runtime.manage` |
| SubscribeRunLogs | `events.platform.workflows.run.logs.v1` | BFF on behalf of user | Topic grant **or** `runtime.manage` (agent seed covers `topic.events.platform.workflows.run.>.read`) |

### 4.4 Runtime `genai.events.v1.Events/Subscribe`

The runtime daemon Subscribe RPC takes an arbitrary JetStream filter subject and **does not apply product Casbin**. Anyone who can reach the runtime Connect port can consume matching subjects. Prefer the BFF-facing APIs for user traffic; treat daemon Subscribe as an internal/ops surface.

## 5. Connect APIs (product)

| **Service** | **RPC** | **Behavior** |
| --- | --- | --- |
| `genius.runtime.v1.RuntimeActions` | `SubscribeBuildEvents` | Stream ActionBuildEvent from platform build subject |
| `genius.runtime.v1.RuntimeWorkflows` | `SubscribeRunLogs` | Stream WorkflowRunLogChunk from platform run logs subject (optional `run_id` filter) |
| `genius.bus.v1.EventBus` | `PublishEvent` | Publish to org bus subject |
|  | `GetEvent` / `ListEvents` | Ephemeral scan of recent org messages (not a durable event store; limited pull) |
|  | `SubscribeEvents` | Stream org wildcard; optional type / correlation filters in-process |
|  | `GetEventChain` | Recent events sharing a correlation id |
| `genius.bus.v1.EventRules` | CRUD + enable | Only `EVENT_RULE_WHEN_KIND_EVENT` accepted today. Match exact type → start product run → optional emit + always `rule.fired` |

## 6. Code map

- Subjects / streams / publish: `runtime/pkg/bus/bus.go`
- NATS client: `runtime/pkg/common/nats/`
- Runtime Events RPC + build/run publishers: `runtime/daemon/services/{events,actions,workflows}.go`
- BFF bus + rules: `web/internal/events/`, handlers `web/internal/services/bus.go`
- RBAC seed: `web/internal/rbac/rbac.go`
- Helm: `k8s/helm/genai-platform` (NATS + auth secret), `genai-web` / `genai-runtime` (Fluent Bit DaemonSet + ingest)
- Runtime log ingest: `runtime/daemon/services/runlogs_ingest.go`
- BFF SubscribeRunLogs: `web/internal/services/{runtime,bus,deps}.go`

## 7. Known gaps (as-built)

- No multi-tenant NATS ACLs — shared `genai` user.
- List/GetEvent are not a durable Postgres event store (contrast older `aios.md` intent).
- DLQ helper unused; schedule-started runs do not emit bus events (webhooks do).
- Workflow run logs: Fluent Bit DaemonSet (genai-runtime chart) → runtime `/internal/v1/workflow-run-logs` → JetStream; not persisted beyond stream retention.

## Related

- [Webhooks and Event Bus — GenAI BFF](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18415660/Webhooks+and+Event+Bus+GenAI+BFF)
- [Architecture and Design — GenAI / Lunaya Flow](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314/Architecture+and+Design+GenAI+Lunaya+Flow)
