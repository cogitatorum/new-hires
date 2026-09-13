# Action: ExecuteWorkflow

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005492](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/19005492)  
> Confluence page id `19005492` (exported for Genius AI hiring take-home).

---

**Handler:** `ExecuteWorkflow`

**Group:** Core

Start another published product workflow via the BFF StartRun API.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| workflowId | string | yes | Target workflow UUID |
| bffUrl | string | no | Override BFF URL |
| token | string | no | Bearer token override |

## Output

| Field | Type | Description |
| --- | --- | --- |
| status | integer | HTTP status |
| body | any | StartRun response |

## Example config

```
{
  "workflowId": "00000000-0000-0000-0000-000000000001"
}
```

## Notes

Use sparingly; prefer EventRules for decoupled orchestration.

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
