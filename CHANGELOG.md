# Changelog

## 1.1.0 — 2026-08-13

Production-hardening release.

- Add GitHub Actions CI (pytest + ruff on Python 3.10–3.12, package-data check)
- Stop claiming “outcome logging” that was never implemented
- Return generic `internal error` on unexpected exceptions; log the traceback
- Expand tests: CLI, `register()`, thresholds loader, package data
- Add SECURITY.md, CONTRIBUTING.md, ARCHITECTURE.md, Dependabot
- Mark Development Status as Production/Stable

## 1.0.0 — 2026-08-12

Initial Lofoten sprint release: advisory solo/pair/swarm router with tools,
slash command, CLI, and bundled skill.
