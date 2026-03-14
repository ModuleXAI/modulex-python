# Changelog

All notable changes to the ModuleX Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
