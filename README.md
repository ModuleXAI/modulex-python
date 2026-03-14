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

# Direct LLM call
result = await client.executions.run(
    llm={
        "integration_name": "openai",
        "provider_id": "openai",
        "model_id": "gpt-4o-mini",
        "temperature": 0.4,
    },
    input={"messages": [{"role": "user", "content": "Hello!"}]},
)

# Get execution state
state = await client.executions.get_state(thread_id="thread-uuid")

# Resume after interrupt
await client.executions.resume(
    thread_id="thread-uuid",
    run_id="run-uuid",
    resume_value="user input",
)

# Cancel execution
await client.executions.cancel(run_id="run-uuid", reason="No longer needed")
```

### SSE Streaming

```python
# Listen to workflow execution events
async for event in client.executions.listen(run_id="run-uuid"):
    if event.event == "node_update":
        print(f"Node {event.data['node_id']}: {event.data['status']}")
    elif event.event == "done":
        print(f"Completed in {event.data['total_execution_time_ms']}ms")
    elif event.event == "error":
        print(f"Error: {event.data['error_message']}")

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

### Templates

```python
# Browse templates
templates = await client.templates.list()

# Use a template
result = await client.templates.use("template-id")
print(f"Created workflow: {result['workflow']['id']}")

# Like a template
await client.templates.like("template-id")
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

```python
# Start a composer session
result = await client.composer.chat(
    message="Add an LLM node that summarizes the input",
    workflow_id="workflow-uuid",
    llm={"integration_name": "anthropic", "model_id": "claude-sonnet-4-20250514"},
)

# Listen to composer events
async for event in client.composer.listen(result["composer_chat_id"], result["run_id"]):
    if event.event == "workflow_change":
        print(f"Workflow modified: {event.data}")
    elif event.event == "done":
        break

# Save or revert changes
await client.composer.save(result["composer_chat_id"])
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
    print(f"Rate limited. Retry after {e.retry_after}s")
except AuthenticationError:
    print("Invalid API key")
except ValidationError as e:
    print(f"Validation error: {e.message}")
except ModulexError as e:
    print(f"API error ({e.status_code}): {e.message}")
```

### Exception Hierarchy

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `ModulexError` | — | Base exception |
| `BadRequestError` | 400 | Malformed request |
| `AuthenticationError` | 401 | Invalid/missing auth |
| `PermissionError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Resource not found |
| `ConflictError` | 409 | Resource conflict |
| `ValidationError` | 422 | Validation error |
| `RateLimitError` | 429 | Rate limit exceeded |
| `InternalError` | 500 | Server error |
| `ExternalServiceError` | 502 | External service failure |
| `ServiceUnavailableError` | 503 | Service unavailable |
| `StreamError` | — | SSE stream error |
| `TimeoutError` | — | Request timeout |

## Type Hints

All types are available for import:

```python
from modulex.types import (
    WorkflowDefinition,
    NodeDefinition,
    EdgeDefinition,
    LLMConfig,
    RunResponse,
    SSEEvent,
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
