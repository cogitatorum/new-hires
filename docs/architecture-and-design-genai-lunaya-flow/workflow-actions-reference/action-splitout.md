# Action: SplitOut

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939975](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939975)  
> Confluence page id `18939975` (exported for Genius AI hiring take-home).

---

**Handler:** `SplitOut`

**Group:** Transform

Take an array field on an object and emit each element as a top-level item.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| data | any | no | Source value |
| field | string | yes | Array field name |

## Output

| Field | Type | Description |
| --- | --- | --- |
| items | array | One item per array element |

## Example config

```
{
  "data": {
    "tags": [
      "a",
      "b"
    ]
  },
  "field": "tags"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
