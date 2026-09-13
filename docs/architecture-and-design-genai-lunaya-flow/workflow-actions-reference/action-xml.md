# Action: XML

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18940009](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18940009)  
> Confluence page id `18940009` (exported for Genius AI hiring take-home).

---

**Handler:** `XML`

**Group:** Files

Parse an XML string into a simplified JSON-like map (best-effort).

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| value | string | yes | XML document string |

## Output

| Field | Type | Description |
| --- | --- | --- |
| data | object | Parsed structure |

## Example config

```
{
  "value": "<root><item>1</item></root>"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
