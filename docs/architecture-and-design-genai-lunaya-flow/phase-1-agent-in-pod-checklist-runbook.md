# Phase 1 — Agent-In-Pod checklist & runbook

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/23592968](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/23592968)  
> Confluence page id `23592968` (exported for Genius AI hiring take-home).

---

**Status:** Phase 1 Agent-In-Pod **complete** on staging; Phase 1.5 colleague memory + personality defaults **shipped and verified** (2026-09-13). **Design:** [Design Goal — AI Agents & Workflow Engine Integration](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/22806530/Design+Goal+AI+Agents+Workflow+Engine+Integration). **Epic:** [GAB-103](https://geniusaidubai.atlassian.net/browse/GAB-103).

## Where we are now

- **Phase 1 vertical slice:** Agent CRD → operator → per-agent namespace/StatefulSet → Telegram DM + HTTP invoke → workflow actuation via Genius BFF (Connect client). Staging `alice` is Ready.
- **Personality / models (Phase 1 scope clarified):** `spec.personality` + `spec.models` are Phase 1; TTS/STT and messenger groups remain Phase 2. Default Genius coworker voice is applied when personality is omitted.
- **Colleague memory (Phase 1.5):** Durable facts/events in the `agents` Postgres DB with **pgvector** semantic search. Cross-thread / cross-person work recall works; raw DM transcripts stay private to the thread.
- **Next (not started):** Phase 2 messenger groups, voice (TTS/STT), shell/HITL, standup summaries / `/forget`, retention TTLs.

## What shipped (Phase 1)

- `Agent` CRD (`agents.geniusai.io/v1alpha1`) + Kubebuilder operator (`genai-agents-manager`)
- Helm chart `genai-agents`; Argo Application wave 6; ImageUpdater tracks `agent-operator:latest` by digest
- CNPG Database `agents` on platform Postgres + checkpointer Secret
- Runtime `harbor.geniusai.io/genai/agent` — Deep Agents + LangGraph PostgresSaver + Buf Connect-ES BFF client + Telegram webhook
- Per-agent Telegram bot Secret + `setWebhook` to `https://web.geniusai.io/agents/<name>/telegram/webhook`
- Dedicated BFF agent user/role (no `runtime.manage`); sample CR `genai-agents/samples/alice.yaml`

## What shipped since Phase 1 acceptance (2026-09-12 → 2026-09-13)

- **Personality + models CRD:** `systemPrompt`, `agentsMdTemplate`, `skills`, `models.coordinator` / `specialists`, reasoning (`adaptive`/`medium`), actuation flags
- **Default voice:** calm Genius coworker tone (staging alice) is the operator default when personality is empty; sample `bob-minimal.yaml` shows omit-personality
- **Conversation reset:** Telegram `/reset` | `/new` | `/clear` and `POST /reset` clear checkpointer thread only
- **OpenRouter Auto:** alice coordinator `openrouter/auto` + adaptive reasoning effort + auto-router `cost_tier`
- **Colleague memory:** `CREATE EXTENSION vector`; tables `memory_facts`, `memory_events`, `memory_embeddings`; tools `search_memory` / `search_events` / `remember_fact`; post-turn extractor; per-turn semantic memory pack
- **CRD **`spec.memory`**:** enabled / extractAfterTurn / embed / embeddingModel (default `openai/text-embedding-3-small`)

## Staging alice checklist

- PASS Secrets (`alice-telegram`, `alice-openrouter`, `genai-agents-checkpointer`, `alice-bff`)
- PASS `Agent/alice` Ready + webhook configured
- PASS `GET /agents/alice/healthz` → 200
- PASS `POST /agents/alice/invoke` + Telegram DM (allowlist set)
- PASS BFF ProductWorkflows StartRun; ListActions correctly denied without `runtime.manage`
- PASS Personality tone (calm coworker) + `/reset`
- PASS Memory: facts for `user:108333189` + cross-actor recall via `search_memory`; embeddings in pgvector

## How memory works (ops note)

- `memory_facts` / `memory_events` = source of truth text; `memory_embeddings` = pgvector fingerprints (`ref_type` + `ref_id`)
- OpenRouter embeds text; Postgres pgvector ranks with `<=>` (cosine)
- Fact extraction uses the agent **coordinator** model (alice: `openrouter/auto`); embeddings use `openai/text-embedding-3-small`
- `/reset` clears LangGraph thread only — work facts survive
- Raw DMs stay in the checkpointer; only promoted work facts are shareable across conversations

## Runbook (ops)

1. Create Secrets in `genai` per `genai-agents/docs/secrets.md`.
2. Apply sample: `kubectl apply -f genai-agents/samples/alice.yaml` (or `bob-minimal.yaml` for default personality).
3. Wait for `kubectl -n genai get agent <name>` → `Ready` and `webhookConfigured=true`.
4. Smoke: `curl https://web.geniusai.io/agents/<name>/healthz` and `POST …/invoke`.
5. Set Telegram allowlist; DM the bot. Use `/reset` to clear chat thread. Ask it to remember a preference, then verify with another user or after reset.
6. On delete: operator clears Telegram webhook; PVC retains data by design.

## Image roll notes

- **Operator image:** push under `agent-operator/**` → Harbor → Argo ImageUpdater digests → rolls `genai-agents-manager`.
- **Agent runtime image:** push to `lunaya-dubai/agents` → Harbor `agent:latest`. ImageUpdater does **not** pin Agent CRs; pods pick up `:latest` on recreate (`imagePullPolicy: Always` / config-hash roll).

## Known notes

- Agent pods run as uid 1000 with `fsGroup: 1000` so PVC `/data` is writable.
- Operator skips Telegram `setWebhook` when URL/token already match; 429s requeue.
- CNPG TLS: runtime Pool uses `rejectUnauthorized: false` (private CA). `pgvector` 0.8.6 enabled on `agents` DB.
- BFF JWT lives in per-agent Secret (e.g. `alice-bff`); dedicated `agent` org role has no `runtime.manage`.
- Phase 2 still owns: groups, TTS/STT, shell actuation, HITL.

## Repos

- Operator: `lunaya-dubai/k8s-operator` → `agent-operator/`
- Runtime: `lunaya-dubai/agents`
- Helm: `lunaya-dubai/helm` → `genai-agents/`
