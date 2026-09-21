# Changelog

## [1.1.0] - 2026-09-21
### Added
- Pinned `requirements-lock.txt` for reproducible dependency management.
- Ruff linter configuration via `pyproject.toml`.
- Router integration stub tests and structlog validation tests.

### Fixed
- Enforced strict linting in CI workflow by removing suppression (`|| true`).
- Upgraded logging infrastructure to utilize `structlog`.
