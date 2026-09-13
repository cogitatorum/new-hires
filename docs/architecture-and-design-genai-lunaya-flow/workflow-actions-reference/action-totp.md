# Action: Totp

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939992](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939992)  
> Confluence page id `18939992` (exported for Genius AI hiring take-home).

---

**Handler:** `Totp`

**Group:** Utility

Generate a time-based one-time password from a shared secret.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| secret | string | yes | Base32 secret |
| digits | integer | no | Code length (default 6) |
| period | integer | no | Step seconds (default 30) |

## Output

| Field | Type | Description |
| --- | --- | --- |
| code | string | Current TOTP code |

## Example config

```
{
  "secret": "JBSWY3DPEHPK3PXP"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
