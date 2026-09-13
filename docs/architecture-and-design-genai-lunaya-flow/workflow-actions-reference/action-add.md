# Action: Add

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972690](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972690)  
> Confluence page id `18972690` (exported for Genius AI hiring take-home).

---

**Handler:** `Add`

**Group:** Sample

Sample action: adds two numbers (catalog demo).

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| a | number | yes | First operand |
| b | number | yes | Second operand |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | number | a + b |

## Example config

```
{
  "a": 2,
  "b": 3
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
