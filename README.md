# ModuleX Python SDK

The official Python SDK for the [ModuleX](https://modulex.dev) AI workflow orchestration platform.

[![CI](https://github.com/ModuleXAI/modulex-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ModuleXAI/modulex-python/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/modulex-python)](https://pypi.org/project/modulex-python/)
[![Python](https://img.shields.io/pypi/pyversions/modulex-python)](https://pypi.org/project/modulex-python/)
[![License](https://img.shields.io/github/license/ModuleXAI/modulex-python)](LICENSE)

## Installation

```bash
pip install modulex-python
```

## Quick Start

```python
import asyncio
from modulex import Modulex

async def main():
    async with Modulex(
        api_key="mx_live_...",
        organization_id="your-org-id",
    ) as client:
        # Get current user
        me = await client.auth.me()
        print(f"Hello, {me['username']}!")

        # List workflows
        workflows = await client.workflows.list(status="active")
        for wf in workflows["workflows"]:
            print(f"  {wf['name']}")

asyncio.run(main())
```

## Authentication

Get your API key from the [ModuleX Dashboard](https://app.modulex.dev). Keys use the `mx_live_` prefix.

```python
from modulex import Modulex

# Pass API key directly
client = Modulex(api_key="mx_live_...")

# Or use environment variable
import os
client = Modulex(api_key=os.environ["MODULEX_API_KEY"])
```

### Organization Context

Most endpoints require an organization context. Set it at the client level or override per-request:

```python
# Set default org for all requests
client = Modulex(api_key="mx_live_...", organization_id="org-uuid")

# Override for a specific request
workflows = await client.workflows.list(organization_id="other-org-uuid")
```

## Configuration

```python
client = Modulex(
    api_key="mx_live_...",
    organization_id="org-uuid",           # Default organization
    base_url="https://api.modulex.dev",   # API base URL
    timeout=30.0,                         # Request timeout (seconds)
    max_retries=3,                        # Retry count for transient errors
)
```

## Resources

### Workflows

```python
# List workflows
workflows = await client.workflows.list(status="active", search="email")

# Auto-paginate all workflows
async for wf in client.workflows.list_all(status="active"):
    print(wf["name"])

# Create workflow
workflow = await client.workflows.create(
    workflow_schema={
        "metadata": {"name": "My Workflow", "version": "1.0"},
        "config": {},
        "state_schema": {"fields": {}},
        "nodes": [],
        "edges": [],
        "entry_point": "start",
    },
    name="My Workflow",
)

# Update & delete
await client.workflows.update("workflow-id", name="New Name", status="active")
await client.workflows.delete("workflow-id")
```

### Executions

```python
# Run a workflow
result = await client.executions.run(
    workflow_id="workflow-uuid",
    input={"messages": [{"role": "user", "content": "Hello!"}]},
)
print(result.run_id)  # typed attribute access (responses are Pydantic models)

# Safely retry a run without double-execution
result = await client.executions.run(
    workflow_id="workflow-uuid",
    input={"messages": [...]},
    idempotency_key="order-4823",  # stable key across retries
)

# Get execution state / resume after interrupt / cancel
state = await client.executions.get_state(thread_id="thread-uuid")
await client.executions.resume(thread_id="thread-uuid", run_id="run-uuid", resume_value="user input")
await client.executions.cancel(run_id="run-uuid", reason="No longer needed")

# Run history (workflow-runs)
runs = await client.executions.list_runs(workflow_id="workflow-uuid", limit=50)
async for run in client.executions.iter_runs(status="succeeded"):  # auto-paginates
    print(run.run_id, run.status)
detail = await client.executions.get_run(run_pk="run-row-id")
```

> Agentic ("direct LLM") chat moved off `/workflows/run` — use `client.assistant.chat(...)` instead.

### SSE Streaming

The backend carries the event type in the SSE `event:` field for `/chats/stream`, and in the JSON
`data["type"]` for workflow/composer/assistant streams. The SDK normalizes both, so `event.event`
always holds the logical type. Streams stop after a terminal event (`done`/`error`/`cancelled`/
`interrupted`) and heartbeats are filtered by default.

```python
# Listen to workflow execution events
async for event in client.executions.listen(run_id="run-uuid"):
    if event.event == "node_update":
        print(f"Node {event.data['node']}: {event.data.get('output')}")
    elif event.event == "interrupt":
        payload = event.data["data"]  # InterruptEventData is nested under data["data"]
        print(f"Needs input: {payload.get('message')}")
    elif event.is_terminal:
        print(f"Stream ended: {event.event}")

# Listen to chat list updates
async for event in client.chats.stream():
    if event.event == "chat_list_updated":
        print(f"Chat list changed: {event.data}")

# Listen to composer events
async for event in client.composer.listen("chat-id", "run-id"):
    print(f"{event.event}: {event.data}")
```

### Credentials

```python
# Add an API key credential
cred = await client.credentials.create(
    integration_name="openai",
    auth_data={"api_key": "sk-..."},
    display_name="Production OpenAI",
)

# Test a credential
result = await client.credentials.test(cred["credential_id"])
print(f"Valid: {result['is_valid']}")

# List credentials
creds = await client.credentials.list(integration_name="openai")

# Add MCP server
mcp = await client.credentials.create_mcp_server(
    server_url="https://mcp-server.example.com",
    headers={"Authorization": "Bearer ..."},
)
```

### Knowledge Bases

```python
# Create a knowledge base
kb = await client.knowledge.create(
    name="Docs",
    embedding_config={"provider": "openai", "model": "text-embedding-3-small"},
)

# Upload a document
doc = await client.knowledge.upload_document(
    knowledge_base_id=kb["id"],
    file_path="/path/to/doc.pdf",
    metadata={"department": "engineering"},
)

# Search
results = await client.knowledge.search(
    knowledge_base_id=kb["id"],
    query="How does deployment work?",
    top_k=5,
)

# Retrieve RAG context
context = await client.knowledge.retrieve_context(
    knowledge_base_id=kb["id"],
    query="deployment steps",
    max_tokens=2000,
)
```

### Schedules

```python
# Create a cron schedule
schedule = await client.schedules.create(
    workflow_id="workflow-uuid",
    name="Daily Report",
    schedule_type="cron",
    cron_expression="0 9 * * 1-5",
    timezone="America/New_York",
)

# Pause/resume
await client.schedules.pause(schedule["id"])
await client.schedules.resume(schedule["id"])

# View run history
runs = await client.schedules.list_runs(schedule["id"])
stats = await client.schedules.run_stats(schedule["id"], days=30)
```

### Deployments

```python
# Deploy a workflow
deployment = await client.deployments.create(
    workflow_id="workflow-uuid",
    deployment_note="v1.0 release",
)

# Activate a deployment
await client.deployments.activate("workflow-uuid", deployment["id"])

# Deactivate live deployment
await client.deployments.deactivate("workflow-uuid")
```

### Composer

`llm` is a provider config dict ({integration_name, provider_id, model_id, credential_id?}) — pass a
`ComposerLLMConfig` or an equivalent dict.

```python
from modulex.types import ComposerLLMConfig, YesNoResponse, user_input_request_from_event

result = await client.composer.chat(
    message="Add an LLM node that summarizes the input",
    workflow_id="workflow-uuid",
    llm=ComposerLLMConfig(integration_name="anthropic", provider_id="anthropic", model_id="claude-sonnet-4-20250514"),
)

# Listen, and answer a human-in-the-loop question (HITL) when the run pauses
async for event in client.composer.listen(result.composer_chat_id, result.run_id):
    if event.event == "user_input_request":
        question = user_input_request_from_event(event.data)  # typed UserInputRequest
        await client.composer.resume(
            result.composer_chat_id,
            request_id=question.request_id,
            response=YesNoResponse(answer=True),
            llm={"integration_name": "anthropic", "provider_id": "anthropic", "model_id": "claude-sonnet-4-20250514"},
        )  # returns a NEW run_id — re-subscribe with listen() on it
    elif event.is_terminal:
        break

chats = await client.composer.list(limit=20)        # cursor-paginated
await client.composer.save(result.composer_chat_id)  # or .revert(...)
```

### Assistant (agentic chat)

Shares the HITL contract with the composer. All endpoints are available to any org member.

```python
result = await client.assistant.chat("Summarize my latest runs", llm=ComposerLLMConfig(
    integration_name="openai", provider_id="openai", model_id="gpt-4o-mini",
))
async for event in client.assistant.listen(result.chat_id, result.run_id):
    if event.event == "response_chunk":
        print(event.data.get("data", {}).get("text", ""), end="")
    elif event.is_terminal:
        break
```

### Other Resources

```python
# Organizations
await client.organizations.create(name="My Org")
await client.organizations.invite("user@example.com", role="member")
llms = await client.organizations.llms()

# Dashboard
logs = await client.dashboard.logs(category="CREDENTIALS")
overview = await client.dashboard.analytics_overview()
users = await client.dashboard.users(search="john")

# Subscriptions
plans = await client.subscriptions.organization_plans()
billing = await client.subscriptions.organization_billing()

# Notifications
notifications = await client.notifications.list()

# Integrations
integrations = await client.integrations.browse(type="tool")
providers = await client.integrations.llm_providers()

# System
health = await client.system.health()
timezones = await client.system.timezones()

# API Keys
key = await client.api_keys.create(name="CI/CD Key")
await client.api_keys.revoke(key["id"])
```

## Error Handling

```python
from modulex import (
    Modulex,
    ModulexError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

try:
    workflow = await client.workflows.get("invalid-id")
except NotFoundError:
    print("Workflow not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s (limit={e.limit}, remaining={e.remaining})")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except ModulexError as e:
    print(f"API error ({e.status_code}): {e.message}")
```

Usage/billing denials (quota, credit, wallet) are surfaced structurally via `BillingError` and its
subclasses, which expose `code`, `layer`, `key`, `current`, `limit`, and `reason`:

```python
from modulex import BillingError, CreditExhaustedError

try:
    await client.executions.run(workflow_id="wf")
except CreditExhaustedError as e:           # 402, layer="credit"
    print(f"Out of credits: {e.current}/{e.limit}")
except BillingError as e:                   # any quota/credit/wallet denial
    print(f"Denied ({e.layer}/{e.code}): {e.reason}")
```

### Exception Hierarchy

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `ModulexError` | — | Base exception |
| `BadRequestError` | 400 | Malformed request |
| `AuthenticationError` | 401 | Invalid/missing auth |
| `PaymentRequiredError` | 402 | Payment required (billing) |
| `PermissionError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ConflictError` | 409 | Resource conflict |
| `ValidationError` | 422 | Validation error |
| `RateLimitError` | 429 | Rate limit exceeded |
| `InternalError` | 500 | Server error |
| `ExternalServiceError` | 502 | External service failure |
| `ServiceUnavailableError` | 503 | Service unavailable |
| `BillingError` | 402/403/429 | Usage denial (base) — `code`/`layer`/`reason` |
| `QuotaExceededError` | 403 | Quota exceeded (`layer="quota"`) |
| `CreditExhaustedError` | 402 | Credit plan exhausted (`layer="credit"`) |
| `WalletError` | 402 | Wallet overage denied (`layer="wallet"`) |
| `StreamError` | — | SSE stream error |
| `TimeoutError` | — | Request timeout |

## Type Hints

Responses are **Pydantic v2 models** — use typed attribute access (`result.id`) or, for
compatibility, dict-style access (`result["id"]`). Unknown fields the backend may add are preserved.
All models are importable:

```python
from modulex import SSEEvent
from modulex.types import (
    WorkflowDefinition,
    NodeDefinition,
    EdgeDefinition,
    LLMConfig,
    RunResponse,
    AsyncPage,        # typed auto-pagination (e.g. executions.iter_runs)
    ModulexModel,     # base class for all response models
)
```

## Documentation

For full API documentation, visit [docs.modulex.dev](https://docs.modulex.dev).

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up the development environment
- Running tests (unit and integration)
- Code style and commit conventions
- Pull request process

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
