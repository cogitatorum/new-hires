# Action: Set

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939958](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939958)  
> Confluence page id `18939958` (exported for Genius AI hiring take-home).

---

**Handler:** `Set`

**Group:** Transform

Build an output object by assigning named fields to literal or bound values.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| assignments | array | no | List of {name, value} pairs |

## Output

| Field | Type | Description |
| --- | --- | --- |
| data | object | Result object |

## Example config

```
{
  "assignments": [
    {
      "name": "greeting",
      "value": "hello"
    },
    {
      "name": "n",
      "value": 42
    }
  ]
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
