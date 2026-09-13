# Action: Branch

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038209](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19038209)  
> Confluence page id `19038209` (exported for Genius AI hiring take-home).

---

**Handler:** `Branch`

**Group:** Flow

Conditional routing. Evaluates a condition (If) or matches a value against cases (Switch) and outputs the selected edge label for downstream Argo when expressions.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| mode | string | yes | if or switch |
| op | string | if mode=if | eq, ne, gt, gte, lt, lte, truthy |
| left | any | if mode=if | Left-hand value |
| right | any | if mode=if | Right-hand value |
| value | any | if mode=switch | Value to match against cases |
| cases | array | if mode=switch | List of {label, match} objects |
| default | string | no | Fallback edge label |

## Output

| Field | Type | Description |
| --- | --- | --- |
| selected | string | Edge label to follow (true/false or case id) |

## Example config

```
{
  "mode": "if",
  "op": "eq",
  "left": 1,
  "right": 1
}
```

## Notes

Connect outbound edges with labels matching selected (e.g. true / false). BRANCH node kind on canvas.

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
