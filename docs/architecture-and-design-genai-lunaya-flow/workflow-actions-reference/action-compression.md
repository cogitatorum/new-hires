# Action: Compression

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038226](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038226)  
> Confluence page id `19038226` (exported for Genius AI hiring take-home).

---

**Handler:** `Compression`

**Group:** Files

Gzip compress or decompress strings with base64 transport encoding.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | gzip or gunzip |
| value | string | yes | Plain text (gzip) or base64 gzip blob (gunzip) |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | string | Base64 gzip or plain text |

## Example config

```
{
  "operation": "gzip",
  "value": "hello world"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
