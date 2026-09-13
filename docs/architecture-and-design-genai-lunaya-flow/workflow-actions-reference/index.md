# Workflow Actions — Reference

> Source: [https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/18939906)  
> Confluence page id `18939906` (exported for Genius AI hiring take-home).

---

Reference for executable workflow actions registered in the GenAI action catalog (staging). Each child page documents one handler: purpose, config, output, and an example.

**Status:** as-built 2026-09-07. Actions run as OCI images on Argo Workflows via the runtime.

## Using actions on the canvas

1. Add an **Action** node and pick a handler from the palette (Files, Flow, Transform, HTTP, …).
2. Fill literal config fields or add **bindings** to map upstream JSON paths into parameters.
3. Publish the workflow — the BFF compiles handlers into runtime `StepSpec` entries.
4. Start a run; each step executes its action container with resolved JSON input.

## Action index

### Flow

- **Branch (If / Switch)** (`Branch`)
- **Merge** (`Merge`)
- **Filter** (`Filter`)
- **Split In Batches** (`SplitInBatches`)
- **Stop and Error** (`StopAndError`)
- **No Op** (`NoOp`)
- **Wait** (`Wait`)
- **Compare Datasets** (`CompareDatasets`)

### Transform

- **Set / Edit Fields** (`Set`)
- **Set Environment Variable** (`SetEnv`) — [docs](https://geniusaidubai.atlassian.net/wiki/spaces/G/pages/21397505/Action+SetEnv)
- **Rename Keys** (`RenameKeys`)
- **Item Lists** (`ItemLists`)
- **Aggregate** (`Aggregate`)
- **Limit** (`Limit`)
- **Remove Duplicates** (`RemoveDuplicates`)
- **Sort** (`Sort`)
- **Split Out** (`SplitOut`)
- **Summarize** (`Summarize`)
- **Code** (`Code`)

### HTTP

- **HTTP Request** (`HttpRequest`)

### Utility

- **Crypto** (`Crypto`)
- **JWT** (`JWT`)
- **Date & Time** (`DateTime`)
- **TOTP** (`Totp`)

### Core

- **Execute Workflow** (`ExecuteWorkflow`)

### Files

- **HTML** (`HTML`)
- **XML** (`XML`)
- **Markdown** (`Markdown`)
- **Compression** (`Compression`)
- **File Storage** (`FileStorage`)

### Misc

- **Debug Helper** (`DebugHelper`)

### Sample

- **Add** (`Add`)
- **Mul** (`Mul`)
- **Echo** (`Echo`)
