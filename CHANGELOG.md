# Changelog

All notable changes to this project are documented here.

## [1.1.0] — 2026-08-13

### Added
- GitHub Actions CI across Python 3.10–3.12 (pytest + ruff + engine self-test)
- CONTRIBUTING.md, SECURITY.md, CODEOWNERS
- MANIFEST.in so sdist includes plugin.yaml, skill, and data files

### Fixed
- Default-branch confusion: production branch is `main` (legacy `master` retained as historical pointer)
- `.gitignore` no longer excludes package `__init__.py` files

## [1.0.0] — 2026-08-11

### Added
- Initial Harbor plugin: `harbor_recommend`, `harbor_status`, `harbor_self_test`
- Slash `/harbor` and CLI `hermes harbor`
- Bundled skill `collaboration-pattern-router`
- Oppositional unit suite (15 tests)
