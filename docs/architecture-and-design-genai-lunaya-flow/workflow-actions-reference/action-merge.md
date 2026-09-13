# Action: Merge

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19103745](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19103745)  
> Confluence page id `19103745` (exported for Genius AI hiring take-home).

---

**Handler:** `Merge`

**Group:** Flow

Fan-in step: combines outputs from multiple upstream branches after dependencies complete.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| mode | string | no | combine (default), append, or chooseBranch |
| inputs | array | no | Objects to merge (often via bindings from prior steps) |

## Output

| Field | Type | Description |
| --- | --- | --- |
| data | object | Merged object |
| items | array | When mode produces a list |

## Example config

```
{
  "mode": "combine",
  "inputs": [
    {
      "a": 1
    },
    {
      "b": 2
    }
  ]
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
