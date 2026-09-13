# Action: Wait

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038345](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038345)  
> Confluence page id `19038345` (exported for Genius AI hiring take-home).

---

**Handler:** `Wait`

**Group:** Flow

Sleep for a number of seconds before continuing.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| seconds | number | no | Duration in seconds |

## Output

| Field | Type | Description |
| --- | --- | --- |
| slept | number | Seconds slept |

## Example config

```
{
  "seconds": 5
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
