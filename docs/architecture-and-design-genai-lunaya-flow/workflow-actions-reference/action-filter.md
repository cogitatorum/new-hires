# Action: Filter

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939941](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939941)  
> Confluence page id `18939941` (exported for Genius AI hiring take-home).

---

**Handler:** `Filter`

**Group:** Flow

Keep array items where a field satisfies an operator against a value.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | no | Input items |
| field | string | no | Field name on each item |
| op | string | no | eq, ne, gt, gte, lt, lte, contains, truthy |
| value | any | no | Comparison value |

## Output

| Field | Type | Description |
| --- | --- | --- |
| items | array | Filtered items |

## Example config

```
{
  "items": [
    {
      "status": "open"
    },
    {
      "status": "closed"
    }
  ],
  "field": "status",
  "op": "eq",
  "value": "open"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
