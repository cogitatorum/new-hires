# Action: JWT

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005509](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005509)  
> Confluence page id `19005509` (exported for Genius AI hiring take-home).

---

**Handler:** `JWT`

**Group:** Utility

Sign or decode HS256 JSON Web Tokens.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | sign or decode |
| payload | object | sign | Claims for sign |
| token | string | decode | JWT string |
| secret | string | no | HMAC secret |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | any | Token string or decoded payload |

## Example config

```
{
  "operation": "sign",
  "payload": {
    "sub": "user-1"
  },
  "secret": "dev-secret"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
