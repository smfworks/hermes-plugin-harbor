# Architecture — harbor

```
repo root __init__.py          → re-exports register()
hermes_harbor/__init__.py      → tools, slash, CLI, skill
hermes_harbor/engine.py        → deterministic recommend()
hermes_harbor/data/thresholds.yaml
hermes_harbor/skill/SKILL.md
```

Decision table (complexity × seam) is the public contract. Cue lexicons are literal token-boundary matches. No hooks. Cache-safe.

Public tools: `harbor_recommend`, `harbor_status`, `harbor_self_test`.
