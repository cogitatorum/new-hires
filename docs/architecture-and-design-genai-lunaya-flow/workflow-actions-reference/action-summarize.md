# Action: Summarize

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19071045](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19071045)  
> Confluence page id `19071045` (exported for Genius AI hiring take-home).

---

**Handler:** `Summarize`

**Group:** Transform

Group items by a field and compute sum, count, or avg per group.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | yes | Input rows |
| groupBy | string | yes | Grouping field |
| op | string | yes | sum, count, or avg |
| field | string | no | Numeric field for sum/avg |

## Output

| Field | Type | Description |
| --- | --- | --- |
| rows | array | Summary rows per group |

## Example config

```
{
  "items": [
    {
      "dept": "a",
      "n": 1
    }
  ],
  "groupBy": "dept",
  "op": "count"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
