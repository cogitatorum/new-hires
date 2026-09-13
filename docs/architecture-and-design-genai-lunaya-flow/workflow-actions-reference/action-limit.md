# Action: Limit

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038294](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038294)  
> Confluence page id `19038294` (exported for Genius AI hiring take-home).

---

**Handler:** `Limit`

**Group:** Transform

Return the first N items from an array.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| items | array | yes | Input array |
| max | integer | yes | Maximum items to keep |

## Output

| Field | Type | Description |
| --- | --- | --- |
| items | array | Truncated array |

## Example config

```
{
  "items": [
    {
      "n": 1
    },
    {
      "n": 2
    },
    {
      "n": 3
    }
  ],
  "max": 2
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
