# Action: StopAndError

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19071028](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19071028)  
> Confluence page id `19071028` (exported for Genius AI hiring take-home).

---

**Handler:** `StopAndError`

**Group:** Flow

Fail the workflow run with a custom error message.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| message | string | yes | Error text surfaced in run status |

## Output

Step fails the run; no success output.

## Example config

```
{
  "message": "Validation failed: missing customer id"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
