# Action: SetEnv

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397505](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397505)  
> Confluence page id `21397505` (exported for Genius AI hiring take-home).

---

**Handler:** `SetEnv`

**Group:** Transform

Expose a value (literal or binding) as a **real OS environment variable** on **descendant** steps (steps that depend on this node via edges / `fromStep`).

**As-built:** 2026-09-07. Runtime injects env for DebugRun processes and Argo action containers (`podSpecPatch`). Unlike `Set`, consumers do not need `fromStep` bindings to read the value — they use `os.Getenv` / process env (Code: `env.VAR`).

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`). Provide either singular `name`/`value` or `assignments`.

| **Field** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| name | string | one of name or assignments | ENV name. Must match `[A-Za-z_][A-Za-z0-9_]*`. For Argo injection the name must be a **literal** (not from\_step). |
| value | any | no | Value to export. Non-strings are JSON-encoded (booleans become `true`/`false`). May be bound from an upstream step. |
| assignments | array | one of name or assignments | List of `{name, value}` pairs (same rules as singular form). Names in the array must be literals for Argo. |
| bindings | array | no | Standard product bindings (e.g. bind `value` from `fromStep`). |

## Output

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| env | object (string map) | All exported names → string values |
| name | string | Echo of singular name when used |
| value | string | Stringified singular value when used |

## How later steps receive the env

1. Connect an edge from `SetEnv` to the consumer (or bind something from SetEnv so it becomes a dependency).
2. **DebugRun / local invoke:** after SetEnv finishes, the runtime merges its `env` map into the next action process environment.
3. **Argo / cluster:** each descendant DAG task gets a `podSpecPatch` that adds OS env entries whose values are Argo expressions reading `$.env.<NAME>` from the SetEnv task output.
4. Multiple ancestor SetEnv nodes accumulate; a later SetEnv for the same key overrides an earlier one.

## Example config

```
{
  "name": "API_TOKEN",
  "value": "secret-from-config"
}
```

Or multiple:

```
{
  "assignments": [
    { "name": "FOO", "value": "1" },
    { "name": "BAR", "value": "x" }
  ]
}
```

Bind value from an upstream `Set` output:

```
{
  "name": "API_TOKEN",
  "bindings": [
    {
      "param": "value",
      "fromStep": "set-credentials",
      "path": "/data/token"
    }
  ]
}
```

## Consuming in Code

Descendant `Code` steps see injected OS env as a map in JS:

```
{
  "source": "return { token: env.API_TOKEN }"
}
```

## Related

- Parent index: [Workflow Actions — Reference](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906/Workflow+Actions+Reference)
- [Action: Set](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939958/Action+Set) — JSON field bag (not OS env)
- [Action: Code](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19070977/Action+Code) — reads `env` in JS
- [Architecture and Design — GenAI / Lunaya Flow](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18317314/Architecture+and+Design+GenAI+Lunaya+Flow)
