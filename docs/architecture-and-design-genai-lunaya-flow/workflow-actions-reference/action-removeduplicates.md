# Action: RemoveDuplicates

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005526](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005526)  
> Confluence page id `19005526` (exported for Genius AI hiring take-home).

---

**Handler:** `RemoveDuplicates`

**Group:** Transform

Deduplicate array items by a key field, or by full JSON if key omitted.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | yes | Input array |
| key | string | no | Dedupe key field |

## Output

| Field | Type | Description |
| --- | --- | --- |
| items | array | Deduped array |

## Example config

```
{
  "items": [
    {
      "id": 1
    },
    {
      "id": 1
    }
  ],
  "key": "id"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
