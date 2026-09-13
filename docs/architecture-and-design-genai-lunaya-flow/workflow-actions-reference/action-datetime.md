# Action: DateTime

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005475](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005475)  
> Confluence page id `19005475` (exported for Genius AI hiring take-home).

---

**Handler:** `DateTime`

**Group:** Utility

Now, format, parse, or add duration to timestamps.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| operation | string | yes | now, format, parse, add |
| value | string | no | Input timestamp string |
| layout | string | no | Go time layout for format/parse |
| amount | integer | no | Amount to add |
| unit | string | no | seconds, minutes, hours, days |

## Output

| Field | Type | Description |
| --- | --- | --- |
| result | string | Formatted or computed time |

## Example config

```
{
  "operation": "now"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
