# Changelog

All notable changes to the ModuleX Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-19

Major release realigning the SDK with the current platform API. **Breaking.**

### Added

- **`assistant` resource** — agentic standard chat (chat/get/list/listen/resume/cancel/status/delete) with HITL.
- **Composer HITL** — `composer.resume()`, `composer.set_focus()`, `composer.list()`; `composer.chat(llm=...)` now takes a provider-config dict (`ComposerLLMConfig`).
- **Execution history** — `executions.list_runs()`, `executions.iter_runs()` (typed `AsyncPage`), `executions.get_run()`; `executions.run(idempotency_key=...)` and `attribution_workflow_id`.
- **Credentials OAuth2** — `initiate_oauth2()`, `refresh_oauth2()`, and `create(oauth_config=...)`.
- **Organization settings** — `preview_invite()`, `get_settings()`, `set_llm_model_visibility()`, `set_composer_llm()`.
- **Structured billing errors** — `BillingError` + `PaymentRequiredError`/`QuotaExceededError`/`CreditExhaustedError`/`WalletError` (402/403/429) exposing `code`/`layer`/`key`/`current`/`limit`/`reason`; `RateLimitError` now carries `limit`/`remaining`/`reset`.
- **Typed responses** — every method returns a Pydantic v2 model (`ModulexModel`); dict-style access still works; unknown backend fields are preserved.
- Environment-variable config (`MODULEX_API_KEY`/`MODULEX_BASE_URL`/`MODULEX_ORGANIZATION_ID`), `User-Agent` header, `default_headers`, `Idempotency-Key` support.

### Changed

- **SSE event dispatch fixed** — `event.event` is normalized from `data["type"]`, so workflow/composer/assistant streams dispatch correctly; terminal events stop iteration; heartbeats filtered.
- `_paginate` now supports page / offset (`has_next`|`has_more`|`total`) / cursor styles and nested `data.<items>` envelopes.
- All response types migrated from `TypedDict` to Pydantic v2 models, aligned field-by-field with the backend.

### Removed

- **`templates` resource** (removed from the platform).
- `system.metrics()` (endpoint no longer exists), composer workflow-`history()` (deprecated), `ApiKeyResponse.is_revoked`, the unused sync `_compat.run_sync` shim, and the removed `/workflows/run` `llm`/`knowledge_config` parameters.

## [0.1.0] - 2026-03-09

### Added

- Initial release of the ModuleX Python SDK
- Full coverage of all 125 ModuleX API endpoints
- Async-first client with `httpx`
- SSE streaming support for workflow execution, chat, and composer events
- Automatic retry with exponential backoff for transient errors
- Auto-pagination iterators for list endpoints
- File upload support for knowledge base documents
- Complete type definitions for all request/response schemas
- Exception hierarchy mapping all HTTP error codes
- Organization ID resolution (per-request override or client default)
