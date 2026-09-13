# Action: HTML

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19070994](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19070994)  
> Confluence page id `19070994` (exported for Genius AI hiring take-home).

---

**Handler:** `HTML`

**Group:** Files

Simple HTML string operations: wrap content in a tag or strip tags.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | wrap or stripTags |
| value | string | yes | Input HTML/text |
| tag | string | no | Tag for wrap (default div) |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | string | Transformed HTML |

## Example config

```
{
  "operation": "wrap",
  "value": "Hello",
  "tag": "p"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
