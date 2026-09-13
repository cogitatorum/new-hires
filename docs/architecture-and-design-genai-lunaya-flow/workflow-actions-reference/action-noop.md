# Action: NoOp

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19103762](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19103762)  
> Confluence page id `19103762` (exported for Genius AI hiring take-home).

---

**Handler:** `NoOp`

**Group:** Flow

Pass-through placeholder step; succeeds without transforming data.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

No required config fields.

## Output

| Field | Type | Description |
| --- | --- | --- |
| ok | boolean | Always true on success |

## Example config

```
{}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
