# Design Goal — AI Agents & Workflow Engine Integration

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/22806530](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/22806530)  
> Confluence page id `22806530` (exported for Genius AI hiring take-home).

---

**Status:** Design goal — **approved** for AI integration with Genius / GenAI (including former open decisions below).

**Audience:** product, platform, backend, AI, and ops.

**Related:** [Goal — Genius Workforce OS](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397571/Goal+Genius+Workforce+OS),
[Architecture and Design](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314/Architecture+and+Design+GenAI+Lunaya+Flow),
[Workflow Actions — Reference](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906/Workflow+Actions+Reference),
[Events and NATS Topics](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397535/Events+and+NATS+Topics+GenAI).

**Decision locked:** Agents converse freely with humans over a **messenger** channel abstraction; **all real-world actuation goes through the product workflow engine** (compose catalog actions → publish/run). The agent is planner + narrator + workflow author—not a general-purpose shell operator.

**First messenger:** Telegram is only the first messenger adapter we will implement; the architecture must not treat any single app as a core subsystem.

## 1. Summary

Build autonomous AI agents that live in Kubernetes as **persistent digital employees**, not disposable sandboxes.
Each agent has identity, personality, voice, workspace, memory, tools policy, and an event history—and interacts with humans the way a colleague would:
via a **messenger** (chat) and shared work artifacts.

When it is time to **do** something that affects systems, data, or people outside the conversation,
the agent does **not** get unrestricted shell/git/kubectl as its primary hands.
It must **compose and run product workflows** from the provided **action catalog**, using the Genius workflow engine
(canvas → compile → Argo / runtime) to reach the goal. Chat is free; actuation is constrained.

Operations are **CRD-driven**: a namespaced `Agent` custom resource plus a Kubebuilder operator reconciles Namespace (per agent), identity, storage, runtime, networking, config, and messenger gateway registration.

Human chat is delivered through a pluggable **messenger** layer (DMs and groups). **Telegram is the first messenger we will support**; further messengers are not planned yet.

## 2. Goals

- Run agents inside the cluster as first-class citizens (like human coworkers).
- Give each agent a durable office: desk (pod), files (PVC), badge (identity/RBAC), journal (events/memory).
- Support long-running autonomous work with isolation and least privilege.
- Keep conversation (LLM orchestration, messenger/HTTP) in the agent environment; keep side effects in the workflow engine.
- Expose a **messenger** channel abstraction (DMs + groups); voice is an agent capability, messengers only deliver it.
- Ship **Telegram as the first messenger adapter**—not as a platform primitive other components depend on by name.
- Declare every agent via a namespaced Kubernetes `Agent` CRD; Kubebuilder operator creates and reconciles required resources.
- **Actuation policy:** `workflowEngineOnly` — goals that mutate the world are achieved by composing catalog actions into workflows, not by ad-hoc shell.

## 3. Non-goals (this phase)

- Multi-tenant SaaS sandbox providers as the agent’s home (E2B, Modal, etc.).
- Ephemeral one-shot Jobs per message (no durable identity).
- Shared pods used by many agent identities.
- Unrestricted cluster-admin access for agents.
- Hand-maintained per-agent YAML sprawl without CRD/operator.
- **Fulfilling user goals via direct shell / arbitrary kubectl / ad-hoc scripts** as a parallel actuation path.
- Treating LangGraph tool-calls as a substitute for Argo-backed product runs for production side effects.
- Hard-wiring product logic, CRD schemas, or event models to a single chat vendor.
- A second messenger adapter (not planned yet).
- Mandatory HITL classes until the action catalog is more complete (none required for now).

## 4. Design metaphor

| Human office | Agent equivalent |
| --- | --- |
| Desk + laptop | Kubernetes Pod (agent runtime, conversation, planning) |
| Filing cabinet | PVC (`workspace`, `memory`, `events`) |
| Job description / personality | System prompt + `AGENTS.md` + skills |
| Voice | Stable TTS persona (+ STT); TTS via ElevenLabs |
| Badge / identity | Stable agent ID, ServiceAccount, workforce Actor, display name |
| Working memory | LangGraph checkpointer (in-cluster Postgres) |
| Institutional memory | Memory files on PVC + optional store |
| Calendar / audit | Event log + workflow run history (Argo / NATS) |
| **Hands / tools that change the world** | **Genius product workflows + action catalog** (not free shell) |
| Talking to coworkers | Messenger (DM / groups; invite-only) / HTTP / CLI |

Humans do **not** SSH into the pod. They message the agent; the agent plans, composes workflows, and reports back.

## 5. Core principle — free talk, workflow-only hands

### 5.1 What the agent may do freely

- Converse (text / voice), clarify goals, explain status, refuse unsafe asks.
- Read its own memory, event log, and allowed product APIs (list workflows, runs, catalog, ACL-scoped resources).
- Draft, debug (`PreviewCompile`, `ExecuteToNode`), and start product workflow runs; whether to auto-publish is decided **per objective**, not a global default.
- Watch NATS / run events and narrate progress back to the human on the active messenger thread.
- Propose or trigger `BuildAction` when the catalog cannot express a needed capability (extends hands; still ends in a workflow step). Org-wide use of new images requires a dedicated approve permission (any role that includes it).

### 5.2 What counts as actuation (must use the engine)

- Calling external APIs, sending mail, writing object storage, mutating tickets/work items.
- Scheduled / webhook-driven automation that continues without the chat turn.
- Anything that needs org credentials, retries, Argo audit, or path ACL enforcement.
- High-risk operations stay in workflows; **no mandatory HITL classes for now** (catalog still incomplete)—revisit when the catalog matures.

### 5.3 Split of responsibility

| Put in the agent pod | Put in the workflow engine |
| --- | --- |
| Ambiguous planning, persona, conversation, voice | Retries, DAGs, cron, webhooks, secret injection, Argo audit |
| Intent → graph composition; narrating runs | High-volume / long-wait / multi-step integrations |
| Judgment in chat; asking for missing actions | Deterministic catalog steps (HTTP, Branch, Wait, Gmail, FileStorage, …) |
| Debug exploration of a draft canvas | Published / policy-approved runs with real side effects (publish policy per objective) |

### 5.4 Failure modes to design for

1. **Missing actions** — Agent must ask the human or open a BuildAction loop; never invent a shell escape.
2. **Slow compose loop** — Fast draft/compile/debug; avoid publishing junk defs for every chat turn.
3. **Exploration vs production** — Private/debug runs OK; production side effects follow the per-objective publish policy.
4. **Long work** — Multi-hour waits live in Wait/schedule/webhook resume; agent wakes on run events.
5. **Attribution** — Runs record `started_by=agent:<id>` (and workforce Actor) for audit.

## 6. Architecture

### 6.1 Interaction plane

```
Human (Messenger DM / group / HTTP / CLI)
        │
        ▼
Messenger gateway  (pluggable adapters; first: Telegram; invite-only)
        │  route by agent id + chat/thread context
        ▼
Agent Pod  (standard container; namespace-per-agent)
  │ Deep Agents + LangGraph (plan, converse, compose)
  │ OpenRouter (LLM)
  │ Workflow client (ProductWorkflows / Runtime / EventRules)
  │ Memory / skills / event writer
  └── PVC (workspace + secrets allowed on PVC), in-cluster Postgres checkpointer
        │
        ├── compose / publish (per objective) / StartRun / ExecuteToNode
        ▼
Genius workflow engine (BFF + runtime + Argo + action catalog)
        │
        ├── credentials, path ACL, NATS run events
        └── side effects in the world
```

### 6.2 Control plane

```
Agent CR (namespaced) ──► Agent Operator (Kubebuilder)
               ├─ Namespace per agent
               ├─ SA / RBAC
               ├─ PVC + StatefulSet/Pod (standard containers)
               ├─ NetworkPolicy / quotas
               ├─ Config (persona, models, actuation: workflowEngineOnly)
               ├─ Secret refs (also allowed on PVC per policy)
               └─ Messenger gateway registration ──► invoke / thread routing
```

### 6.3 Pattern choice: Agent-In-Pod

| Pattern | Where the agent lives | Fit |
| --- | --- | --- |
| **Agent-In-Pod (chosen)** | Long-lived pod is the office | Strong for “digital employee” |
| Sandbox-as-backend | Brain outside; tools hit remote box | Weaker |
| Cloud sandbox SaaS | Ephemeral vendor VM | Not a cluster citizen |

Isolation is Kubernetes (namespace-per-agent, NetworkPolicy, SecurityContext) with **standard containers** for now (gVisor/Kata not required day one).
**Actuation isolation** is additionally enforced by routing side effects through the workflow engine and org RBAC/path ACL.

## 7. Agent CRD (conceptual)

Namespaced `Agent` (not cluster-scoped). Illustrative shape:

```
apiVersion: agents.geniusai.io/v1alpha1
kind: Agent
metadata:
  name: alice
  namespace: agent-alice   # or CR lives in a control ns; office ns still per-agent
spec:
  displayName: Alice
  personality:
    systemPrompt: |
      You are Alice...
    agentsMdTemplate: |
      # AGENTS.md
      ...
    skills: []

  actuation:
    mode: workflowEngineOnly
    allowActionBuild: true
    allowDebugRuns: true
    # publish: decided per objective — not a single global default

  identity:
    git: { userName: Alice Bot, userEmail: alice@example.com }
    workforce:
      actorRef: ""
    serviceAccount:
      rules: []

  models:
    coordinator: openrouter:...
    specialists:
      researcher: openrouter:...

  voice:
    enabled: true
    tts:
      provider: elevenlabs
      voiceId: alice-primary
      secretRef: {...}
    stt:
      provider: ""          # not decided yet
      secretRef: {...}
    defaults:
      replyModality: auto   # mirror human (text↔voice)

  workspace:
    storageClassName: longhorn
    size: 50Gi
    mountPath: /home/agent
    # Secrets may live on the PVC (approved policy)

  channels:
    messenger:
      enabled: true
      provider: telegram      # first adapter; no second planned yet
      credentialsSecretRef: { name: alice-messenger, key: token }
      allowFrom: { users: [], groups: [] }   # invite-only
      groupPolicy: { respondOn: mention-or-reply }
      media: { sendVoiceNotes: true, acceptVoiceNotes: true }

  tools:
    workflowClient: true
    catalogRead: true
    webSearch: true
    shell:
      enabled: false
    hitl:
      # No mandatory HITL classes while catalog is incomplete
      execute: false

  isolation:
    runtimeClassName: null    # standard containers
    networkPolicy: default-deny-plus-egress
    resources:
      requests: { cpu: "250m", memory: 512Mi }
      limits: { cpu: "2", memory: 4Gi }

  persistence:
    checkpointer: { postgresSecretRef: { name: agents-postgres } }  # in-cluster
    retainWorkspaceOnDelete: true

status:
  phase: Ready
  endpoint: http://agent-alice.agent-alice.svc:8080
  messenger:
    provider: telegram
    handle: "@alice_agent_bot"
    webhookConfigured: true
```

## 8. How agents use the Genius workflow engine

### 8.1 Capabilities the agent relies on

- **Product canvas** (`genius.workflows.v1`): draft/update/publish, StartRun, ListRuns, ListNodeHandlers, PreviewCompile, ExecuteToNode.
- **Action catalog** (`RuntimeActions` / palette): HttpRequest, Branch, Wait, Set, Gmail\*, FileStorage, Code, transforms, ExecuteWorkflow, sample math, plus OCI-built custom actions.
- **Triggers**: manual, webhook, schedule/interval; EventRules (`WHEN_KIND_EVENT` → start published workflow).
- **Credentials**: org secrets; agent may also keep secrets on its PVC per approved policy; prefer `credentialId` for workflow steps.
- **Events**: NATS run progress and org bus events for narration and wakeups.
- **IAM / path ACL**: workforce-bound roles; **BuildAction org approval** requires a dedicated permission—any role that includes it may approve.

### 8.2 Canonical loops

1. **Chat → compose → run → narrate** — Human (invite-only messenger) asks → agent drafts from catalog → debug if needed → publish only when that objective’s policy says so → StartRun → narrate.
2. **Event → workflow → agent wakeup** — Run/rule completes → agent summarizes on the messenger thread.
3. **Missing capability** — Catalog gap → explain → optional BuildAction → approval via dedicated permission → resume composition.
4. **Skill promotion** — Recurring compositions become published reusable workflows; skills become thin StartRun + narrate wrappers.

### 8.3 What we explicitly do not wire as primary hands

- Deep Agents `LocalShellBackend` fulfilling user goals.
- Scoped kubectl mutate / direct git push to production as the happy path.
- Parallel “agent tools” that duplicate HttpRequest/Gmail/FileStorage outside Argo.

Optional later: shell restricted to scaffolding action source for BuildAction—still not for goal fulfillment.

## 9. Per-agent cluster layout

```
Agent CR: alice (namespaced)
└── (reconciled by Kubebuilder operator)
    ├── Namespace: agent-alice          # approved: namespace per agent
    ├── ServiceAccount + RBAC
    ├── PersistentVolumeClaim           # retain on delete
    ├── ConfigMap (persona / actuation)
    ├── Secret refs / secrets on PVC
    ├── NetworkPolicy (+ optional ResourceQuota)
    ├── StatefulSet / Pod               # standard containers
    ├── Service
    └── Messenger gateway registration  # Telegram first; invite-only
```

Shared platform: Agent Operator + CRD, **in-cluster Postgres** checkpointer, messenger gateway, OpenRouter, optional LangSmith, existing Genius BFF + runtime + NATS + action builder.

## 10. Communication channels

### 10.1 Messenger (first-class abstraction)

The product primitive is a **messenger**: DMs and optional groups. Provider adapters sit behind it.

| Mode | Behavior |
| --- | --- |
| DM (1:1) | Private thread: `messenger:dm:<agent_id>:<provider>:<user_id>` |
| Groups | Respond on **mention or reply**; thread `messenger:group:<agent_id>:<provider>:<chat_id>` |

**Allowlisting:** invite-only (which users/groups may talk to which agent).

Gateway: provider session, invoke mapping, replies, allowlists, event log, optional voice encode/decode.

### 10.2 First messenger: Telegram

**Telegram is the first (and currently only planned) messenger adapter** (Phase 1 DMs; Phase 2 groups). Not a core dependency of agent runtime or workflow engine. No second messenger planned yet.

### 10.3 Also supported

- HTTP / CLI for ops and debugging

### 10.4 Voice

Persona-level `spec.voice`: TTS via **ElevenLabs**; STT vendor **not decided yet**. Default reply modality **auto** (mirror human). Messengers only transport/encode audio.

## 11. Capability mapping

| Aspect | Mechanism |
| --- | --- |
| Identity | Stable AGENT\_ID, SA, git author, workforce Actor, display name |
| Personality | System prompt, durable AGENTS.md, skills |
| Voice | ElevenLabs TTS; STT TBD; modality auto |
| Workspace | PVC (notes, drafts, action repos, **secrets allowed on PVC**) |
| Memory | In-cluster Postgres checkpointer; institutional files |
| Actuation | ProductWorkflows + catalog + credentials + ACL |
| History | PVC event JSONL + workflow run IDs (+ optional LangSmith) |

## 12. Security & isolation

- **Namespace per agent**; default-deny NetworkPolicy; required egress only.
- Non-root, drop caps, no privilege escalation; never cluster-admin.
- **Standard containers** (no gVisor/Kata day one).
- Secrets may live on the agent PVC (approved); still use Secret refs / credential IDs for workflow steps where applicable.
- ResourceQuota / limits.
- Path ACL + per-objective publish policy; BuildAction org approval via dedicated permission.
- **No mandatory HITL classes for now**—revisit when catalog is complete.
- Threat note: prompt injection can still misuse allowed workflow APIs—RBAC and catalog limits remain necessary.

## 13. Human interaction model

1. Invited human messages agent via messenger (DM/group) or HTTP/CLI.
2. Gateway invokes agent with stable `thread_id`; groups only when mentioned or replied to.
3. Agent plans; if actuation is required, composes catalog actions, debugs, publishes per that objective’s policy, starts run.
4. Agent appends events and replies (modality auto).
5. Human disconnects; pod + PVC remain (**retain on delete**); long work continues in Argo until events wake narration.

## 14. Tech stack

| Layer | Choice |
| --- | --- |
| Agent API | Namespaced Kubernetes CRD (`Agent`) |
| Control plane | Agent Operator (**Kubebuilder**) |
| Orchestration | Deep Agents + LangGraph |
| Models | OpenRouter |
| Agent service | Deno / TypeScript (initial) |
| Office | StatefulSet + PVC + SA/RBAC/NetworkPolicy; namespace per agent; standard containers |
| Checkpointer | **In-cluster Postgres** |
| Actuation | Genius BFF ProductWorkflows + runtime + Argo + action OCI catalog |
| Events | NATS (run progress + org bus / EventRules) |
| Human chat | Messenger gateway; **Telegram first**; invite-only; no second messenger planned |
| Voice | ElevenLabs TTS; STT TBD; modality auto |

## 15. Phased delivery

### Phase 0 — Design goal (this document)

Approved: Agent-In-Pod + `workflowEngineOnly` + messenger abstraction + decisions in §16.

### Phase 1 — Vertical slice

- Namespaced `Agent` CRD + Kubebuilder operator (per-agent namespace, StatefulSet, PVC retain, SA/RBAC, NetworkPolicy, Service, ConfigMap)
- Deep Agents in-pod with workflow client (no shell goal fulfillment); secrets allowed on PVC
- Memory + event log; **in-cluster Postgres** checkpointer
- Messenger gateway: Telegram adapter, **invite-only**, DMs; HTTP invoke
- Compose → StartRun → narrate; publish decided per objective
- CR status Ready / errors; reply modality auto; text/voice when voice enabled

### Phase 2 — Employee realism

- Messenger groups with **mention-or-reply** policy
- Workforce Actor binding + path ACL
- EventRules wakeups; run attribution `started_by=agent:…`
- BuildAction loop + **dedicated approve permission** for org-wide images
- Voice: ElevenLabs TTS; pick STT vendor; PVC retention already default

### Phase 3 — Fleet

- Multi-agent GitOps; messenger gateway at scale; quotas/hibernation
- Skill → published workflow promotion
- Eval/trace standard; revisit HITL classes when catalog is mature
- Additional messengers only if newly planned (none today)

## 16. Approved decisions

Formerly “open decisions”—now locked:

| # | Topic | Decision |
| --- | --- | --- |
| 1 | Namespace | **Namespace per agent** |
| 2 | Runtime isolation | **Standard containers** (not gVisor/Kata day one) |
| 3 | Messenger group triggers | **Mention + reply** |
| 4 | Messenger allowlisting | **Invite-only** |
| 5 | Checkpointer Postgres | **In-cluster Postgres** |
| 6 | Secrets placement | **Allowed on the agent PVC** |
| 7 | HITL classes | **None for now** (catalog incomplete); revisit later |
| 8 | CRD | `Agent`**, namespaced** |
| 9 | Delete semantics | **Retain** PVC / event history by default |
| 10 | Operator toolchain | **Kubebuilder** |
| 11 | Voice | **ElevenLabs** for TTS; STT / voice service topology **not decided yet** |
| 12 | Default reply modality | **Auto** (mirror human) |
| 13 | Publish policy | **Per objective**—no single global auto-publish default |
| 14 | Catalog / BuildAction governance | **Dedicated approve permission**; any role that includes it may approve |
| 15 | Second messenger | **Not planned yet** |

## 17. Recommendation

This design is the approved direction:

- Namespaced `Agent` CRD + **Kubebuilder** operator; **namespace per agent**; retain PVC on delete
- Deep Agents + LangGraph + OpenRouter; in-cluster Postgres checkpointer; secrets allowed on PVC
- Standard containers; messenger with Telegram first, invite-only, mention+reply in groups; modality auto; ElevenLabs TTS
- **Workflow engine as the only hands**; publish per objective; BuildAction org approval via dedicated permission; no mandatory HITL yet

Phase 1 scaffolding can proceed against these decisions.
