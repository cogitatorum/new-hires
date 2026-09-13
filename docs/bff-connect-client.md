# Genius BFF ConnectRPC — generate a client

The Genius AI browser/API surface is a **ConnectRPC** BFF. Service contracts live in this repo under [`proto/genius/`](../proto/genius/) (snapshot of the product protos). Candidates should generate typed clients with **Buf** — do **not** hand-roll `fetch` to `/genius.../Method` paths.

BFF Staging URL: `https://web.geniusai.io`  
Protocol for browsers: **Connect over HTTP/1.1 JSON** (`@connectrpc/connect-web`), not raw gRPC.

## What’s in `proto/`

| Package | Services (examples) |
|---------|---------------------|
| `genius.auth.v1` | `Auth` (login / refresh / logout) |
| `genius.iam.v1` | `Organizations`, `Users`, `Roles` |
| `genius.overview.v1` | `Overview` |
| `genius.workflows.v1` | `ProductWorkflows` |
| `genius.workitems.v1` | `WorkItems` |
| `genius.agents.v1` | `Agents` |
| `genius.approvals.v1` | `Approvals`, `Policies` |
| `genius.bus.v1` | `EventBus`, `EventRules` |
| `genius.connectors.v1` | `Connectors` |
| `genius.credentials.v1` | `Credentials` |
| `genius.decisions.v1` | `Decisions` |
| `genius.runtime.v1` | `RuntimeActions`, `RuntimeWorkflows` |
| `genius.settings.v1` | `Settings` |
| `genius.workforce.v1` | `Departments`, `Positions`, `Actors`, `RoleContracts` |
| `genius.common.v1` | Shared messages (no service) |

Skim the `.proto` files for RPCs and field names; Confluence docs under [`docs/`](./) explain product meaning.

## 1. Install toolchain (TypeScript / browser)

From your frontend app (Vite/Next/etc.):

```bash
npm install @bufbuild/protobuf @connectrpc/connect @connectrpc/connect-web
npm install --save-dev @bufbuild/buf @bufbuild/protoc-gen-es
```

Ensure `protoc-gen-es` is on `PATH` when Buf runs (npm’s `node_modules/.bin` is enough if you use `npx buf`).

## 2. Buf config in this take-home pack

This repo already includes:

- [`buf.yaml`](../buf.yaml) — module root = `proto/`
- [`buf.gen.yaml`](../buf.gen.yaml) — emits Connect-ES TypeScript into `src/gen`

From the **hire repo root**:

```bash
# once: fetch well-known types
npx buf dep update

# generate
mkdir -p src/gen
npx buf generate
```

That writes message types + service descriptors such as:

- `src/gen/genius/auth/v1/auth_pb.ts`
- `src/gen/genius/workflows/v1/workflows_pb.ts`
- …

If your app lives in a subdirectory, either run Buf from this pack and copy `src/gen`, or point `out:` in `buf.gen.yaml` at your app’s gen folder and run `buf generate` with this directory as the module (keep `buf.yaml` + `proto/` together).

### Alternate: generate against a path

```bash
# from another package that has its own buf.gen.yaml
npx buf generate /path/to/hire
# or
npx buf generate /path/to/hire/proto
```

(Exact path form depends on how your `buf.gen.yaml` is set up; prefer generating from this repo’s root with the bundled configs.)

## 3. Create a transport + clients

```ts
import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-web";
import { Auth } from "./gen/genius/auth/v1/auth_pb.js";
import { ProductWorkflows } from "./gen/genius/workflows/v1/workflows_pb.js";
import { Overview } from "./gen/genius/overview/v1/overview_pb.js";

const transport = createConnectTransport({
  baseUrl: import.meta.env.VITE_GENIUS_API_URL ?? "http://localhost:8090",
  interceptors: [
    (next) => async (req) => {
      const token = localStorage.getItem("accessToken");
      if (token) {
        req.header.set("Authorization", `Bearer ${token}`);
      }
      return next(req);
    },
  ],
});

export const authClient = createClient(Auth, transport);
export const workflowsClient = createClient(ProductWorkflows, transport);
export const overviewClient = createClient(Overview, transport);
```

Rules of thumb:

- Prefer **generated** `createClient(Service, transport)` over stringly-typed HTTP.
- Put `Authorization: Bearer <jwt>` in a Connect **interceptor**, not ad-hoc per call.
- Do **not** send a bearer token on `Auth.Login` / `Auth.RefreshToken` (call them before a token exists, or skip the header in the interceptor for those procedures).

## 4. Auth flow (UI)

1. `authClient.login({ email, password })` — registration is invite-only (`Auth.Register` is not a public self-serve path).
2. Persist `accessToken` and `refreshToken` from the response.
3. Other RPCs use the interceptor bearer header.
4. On `Unauthenticated` / code `unauthenticated`: `authClient.refreshToken({ refreshToken })`, update storage, retry once — or send the user to login.
5. `authClient.logout({ refreshToken })`, then clear tokens.

```ts
const tokens = await authClient.login({
  email: "you@example.com",
  password: "…",
});
localStorage.setItem("accessToken", tokens.accessToken);
localStorage.setItem("refreshToken", tokens.refreshToken);

const overview = await overviewClient.getOverview({});
```

## 5. Node / agents (optional)

Server-side TypeScript uses the same generated `_pb.ts` files with `@connectrpc/connect-node` instead of `connect-web`. Go services use `protoc-gen-go` + `protoc-gen-connect-go` (see the product `web/` repo’s Go `buf.gen.yaml`); for this take-home, **browser Connect-ES is enough**.

## 6. Common pitfalls

| Pitfall | Fix |
|--------|-----|
| Hand-built `fetch('/genius.workflows.v1.ProductWorkflows/StartRun')` | Use Buf + `createClient` |
| gRPC-web binary only | Use Connect JSON via `createConnectTransport` |
| CORS / wrong host | Point `baseUrl` at the BFF (8090 locally), not the Vite dev server |
| Missing `buf dep update` | Well-known types (`google.protobuf.*`) fail to resolve |
| Committing nothing after generate | Commit `src/gen` **or** document `buf generate` in your README/CI |

## Related product docs in this pack

- [Product Workflows & Actions — BFF GUI Integration Guide](./architecture-and-design-genai-lunaya-flow/product-workflows-actions-bff-gui-integration-guide.md)
- [Webhooks and Event Bus — GenAI BFF](./architecture-and-design-genai-lunaya-flow/webhooks-and-event-bus-genai-bff.md)
- [Architecture and Design](./architecture-and-design-genai-lunaya-flow/index.md)
