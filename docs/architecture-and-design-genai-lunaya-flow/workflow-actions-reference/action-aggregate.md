# Action: Aggregate

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005441](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005441)  
> Confluence page id `19005441` (exported for Genius AI hiring take-home).

---

**Handler:** `Aggregate`

**Group:** Transform

Reduce an item array with sum, count, avg, min, max, or join.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | yes | Input items |
| op | string | yes | sum, count, avg, min, max, join |
| field | string | no | Numeric/string field to aggregate |
| separator | string | no | Separator for join |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | any | Aggregated value |

## Example config

```
{
  "items": [
    {
      "n": 1
    },
    {
      "n": 2
    }
  ],
  "field": "n",
  "op": "sum"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
