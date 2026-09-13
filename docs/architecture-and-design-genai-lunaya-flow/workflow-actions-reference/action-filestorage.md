# Action: FileStorage

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038277](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038277)  
> Confluence page id `19038277` (exported for Genius AI hiring take-home).

---

**Handler:** `FileStorage`

**Group:** Files

Read, write, list, delete, and check files on in-cluster S3 (SeaweedFS). Paths are keys inside the genai bucket.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | read, write, list, delete, exists |
| path | string | yes\* | Object key (e.g. workflows/demo/file.txt) |
| content | string | write | File content |
| encoding | string | no | utf8 (default) or base64 |
| recursive | boolean | list | Recursive listing |

## Output

| Field | Type | Description |
| --- | --- | --- |
| ok | boolean | Success flag |
| content | string | File content (read) |
| files | array | Entries for list |
| exists | boolean | For exists op |

## Example config

```
{
  "operation": "write",
  "path": "workflows/demo/hello.txt",
  "content": "hello",
  "encoding": "utf8"
}
```

## Notes

Requires runtime with GENAI\_S3\_\* injected into action pods. Use path prefixes per workflow for isolation.

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
