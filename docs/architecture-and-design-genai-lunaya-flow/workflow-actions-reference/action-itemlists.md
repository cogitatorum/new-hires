# Action: ItemLists

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972724](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972724)  
> Confluence page id `18972724` (exported for Genius AI hiring take-home).

---

**Handler:** `ItemLists`

**Group:** Transform

Array helpers: split a field out, concatenate lists, or limit length.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | splitOut, concatenate, or limit |
| items | array | no | Input items |
| field | string | no | Field for splitOut |
| limit | integer | no | Max items for limit op |

## Output

| Field | Type | Description |
| --- | --- | --- |
| items | array | Result items |

## Example config

```
{
  "operation": "concatenate",
  "items": [
    [
      1,
      2
    ],
    [
      3
    ]
  ]
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
