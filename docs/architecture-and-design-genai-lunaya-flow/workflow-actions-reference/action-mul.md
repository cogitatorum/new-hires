# Action: Mul

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972741](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972741)  
> Confluence page id `18972741` (exported for Genius AI hiring take-home).

---

**Handler:** `Mul`

**Group:** Sample

Sample action: multiplies two numbers (catalog demo).

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| in1 | number | yes | First operand |
| in2 | number | yes | Second operand |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | number | Product |

## Example config

```
{
  "in1": 6,
  "in2": 7
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
