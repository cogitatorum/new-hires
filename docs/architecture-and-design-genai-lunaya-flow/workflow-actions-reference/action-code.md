# Action: Code

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19070977](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19070977)  
> Confluence page id `19070977` (exported for Genius AI hiring take-home).

---

**Handler:** `Code`

**Group:** Transform

Run JavaScript (goja) against optional input JSON. Return value becomes result.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| **Field** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| source | string | yes | JavaScript source; use return {...} |
| input | any | no | JSON passed into the script scope |

## Output

| **Field** | **Type** | **Description** |
| --- | --- | --- |
| result | any | Returned value from script |

## Example config

```
{
  "source": "return { doubled: (input.n || 0) * 2 }",
  "input": {
    "n": 21
  }
}
```

## Notes

Sandboxed JS — no network or filesystem. Prefer builtins when possible.

OS environment variables injected by ancestor [SetEnv](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397505/Action+SetEnv) steps are available as the `env` map (e.g. `env.API_TOKEN`). Input JSON remains on `input`.

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
