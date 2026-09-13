# Action: Sort

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038328](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038328)  
> Confluence page id `19038328` (exported for Genius AI hiring take-home).

---

**Handler:** `Sort`

**Group:** Transform

Sort items ascending or descending by a field.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | yes | Input array |
| field | string | no | Sort key |
| order | string | no | asc (default) or desc |

## Output

| Field | Type | Description |
| --- | --- | --- |
| items | array | Sorted array |

## Example config

```
{
  "items": [
    {
      "n": 3
    },
    {
      "n": 1
    }
  ],
  "field": "n",
  "order": "asc"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
