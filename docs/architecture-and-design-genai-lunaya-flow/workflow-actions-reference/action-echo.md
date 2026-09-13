# Action: Echo

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038260](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038260)  
> Confluence page id `19038260` (exported for Genius AI hiring take-home).

---

**Handler:** `Echo`

**Group:** Sample

Sample action: echoes a message string.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| msg | string | yes | Message to echo |

## Output

| Field | Type | Description |
| --- | --- | --- |
| echo | string | Same message |

## Example config

```
{
  "msg": "ping"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
