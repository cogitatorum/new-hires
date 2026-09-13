# Action: Markdown

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038311](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038311)  
> Confluence page id `19038311` (exported for Genius AI hiring take-home).

---

**Handler:** `Markdown`

**Group:** Files

Pass-through markdown text with normalized output field (rendering is client-side).

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| value | string | yes | Markdown source |

## Output

| Field | Type | Description |
| --- | --- | --- |
| markdown | string | Same markdown in output |

## Example config

```
{
  "value": "# Title\n\nBody text"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
