# Action: CompareDatasets

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005458](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005458)  
> Confluence page id `19005458` (exported for Genius AI hiring take-home).

---

**Handler:** `CompareDatasets`

**Group:** Flow

Diff two object arrays by a key field into onlyA, onlyB, and both buckets.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| a | array | yes | First dataset |
| b | array | yes | Second dataset |
| key | string | yes | Unique key field name |

## Output

| Field | Type | Description |
| --- | --- | --- |
| onlyA | array | In A not B |
| onlyB | array | In B not A |
| both | array | In both |

## Example config

```
{
  "a": [
    {
      "id": 1
    }
  ],
  "b": [
    {
      "id": 2
    }
  ],
  "key": "id"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
