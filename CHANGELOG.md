# Changelog

## [1.2.0] - 2026-09-29
### Added
- Committed `requirements-lock.txt` for reproducible installs.
- Updated `requirements.txt` and `requirements-dev.txt` with pinned versions.
- New GitHub Actions workflow (`ci.yml`) running lint, type checks, tests, and security audit.
- Unit tests for `manage_infra.py` covering ROCm and Kubernetes checks.
- Unit tests for `chatbot_backend.py` covering conversation creation, sampling params, and tool registration validation.
- Extended router tests (`test_router.py`) with schema validation error cases.
- Expanded logging tests (`test_logging.py`) to validate structured output from `structlog`.

### Changed
- Refactored `manage_infra.py` to replace stdlib logging with `structlog`.
- Refactored `chatbot_backend.py` to add `structlog` logging and Pydantic schema validation.
- Refactored `lemonade_router.py` to enforce schema validation with Pydantic and structured logging.
- Updated README.md to reference lockfile installation and dev dependencies.

### Fixed
- CI workflow now installs from lockfile ensuring deterministic builds.
- Coverage gate raised to 70% in CI workflow.
- Improved error handling in infra and router modules with structured logs.
