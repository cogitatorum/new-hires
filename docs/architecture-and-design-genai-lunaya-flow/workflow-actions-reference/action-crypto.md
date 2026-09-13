# Action: Crypto

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038243](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038243)  
> Confluence page id `19038243` (exported for Genius AI hiring take-home).

---

**Handler:** `Crypto`

**Group:** Utility

Hash, HMAC, and base64 encode/decode helpers.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | hash, hmac, base64Encode, base64Decode |
| value | string | yes | Input string |
| algorithm | string | no | sha256 (default), sha1, md5 |
| secret | string | no | Required for hmac |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | string | Hex or base64 result |

## Example config

```
{
  "operation": "hash",
  "algorithm": "sha256",
  "value": "hello"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
