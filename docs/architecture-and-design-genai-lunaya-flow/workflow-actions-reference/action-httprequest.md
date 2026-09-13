# Action: HttpRequest

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972707](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18972707)  
> Confluence page id `18972707` (exported for Genius AI hiring take-home).

---

**Handler:** `HttpRequest`

**Group:** HTTP

Call any HTTP API. Supports method, URL, headers, query, body, and optional credentialId for auth injection.

## Configuration

Set fields on the node config panel or use `bindings` to wire values from upstream steps (`fromStep` + `path`).

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| method | string | yes | GET, POST, PUT, PATCH, DELETE, … |
| url | string | yes | Request URL |
| headers | object | no | Request headers |
| query | object | no | Query parameters |
| body | any | no | Request body |
| credentialId | string | no | Stored credential for auth |
| responseFormat | string | no | json or text |

## Output

| Field | Type | Description |
| --- | --- | --- |
| status | integer | HTTP status |
| body | any | Parsed or raw response |

## Example config

```
{
  "method": "GET",
  "url": "https://httpbin.org/get",
  "responseFormat": "json"
}
```

## Related

- Parent index: Workflow Actions — Reference
- Architecture: Genius AI BFF / Lunaya Flow
