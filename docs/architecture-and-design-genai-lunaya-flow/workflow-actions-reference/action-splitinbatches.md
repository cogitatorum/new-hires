# Action: SplitInBatches

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19071011](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19071011)  
> Confluence page id `19071011` (exported for Genius AI hiring take-home).

---

**Handler:** `SplitInBatches`

**Group:** Flow

Split an array into fixed-size batches for loop-style processing on the canvas.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | yes | Array to split |
| batchSize | integer | no | Batch size (default 10) |

## Output

| Field | Type | Description |
| --- | --- | --- |
| batches | array | Array of batch arrays |

## Example config

```
{
  "items": [
    1,
    2,
    3,
    4,
    5
  ],
  "batchSize": 2
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
