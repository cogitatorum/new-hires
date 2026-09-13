# Action: RenameKeys

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972758](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972758)  
> Confluence page id `18972758` (exported for Genius AI hiring take-home).

---

**Handler:** `RenameKeys`

**Group:** Transform

Rename keys on an input object using a mapping table.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| data | object | no | Source object |
| mapping | object | yes | oldKey → newKey map |

## Output

| Field | Type | Description |
| --- | --- | --- |
| data | object | Object with renamed keys |

## Example config

```
{
  "data": {
    "foo": 1
  },
  "mapping": {
    "foo": "bar"
  }
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
