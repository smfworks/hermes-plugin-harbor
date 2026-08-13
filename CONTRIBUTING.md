# Contributing

## Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m ruff check .
```

Python 3.10+ is required. Runtime dependencies: none.

## Changing the decision table

The solo / pair / swarm table is a published contract (skill + blog +
self-test). If you change cue lists or routing, you must:

1. Update `self_test()` cases in `hermes_harbor/engine.py`
2. Update `tests/test_harbor.py`
3. Update `hermes_harbor/skill/SKILL.md` and the README table
4. Note the behavioral change in `CHANGELOG.md`

Do not add Hermes hooks. Cache-safety is a hard constraint.

## Keep manifests aligned

Version and provided tools live in three places:

- `pyproject.toml`
- `plugin.yaml` (repo root — Hermes source install)
- `hermes_harbor/plugin.yaml` (packaged)

`hermes_harbor/engine.py` `__version__` must match.

## PR expectations

- Tests green locally
- No new runtime dependencies without a written rationale
- Conventional commit subject (`fix:`, `feat:`, `docs:`, `ci:`, `test:`)
