# Architecture

Harbor is a **pure advisory plugin**. It classifies a task description and
recommends `solo`, `pair`, or `swarm`. It never launches agents.

```
task text
    │
    ▼
_safe_text / enum validation   (plugin handlers)
    │
    ▼
engine.recommend()             (deterministic cues + decision table)
    │
    ├── HarborRecommendation
    ├── format_human()
    └── JSON payload to tool / slash / CLI
```

## Surfaces

| Surface | Entry | Notes |
|---------|-------|--------|
| Tool | `harbor_recommend`, `harbor_status`, `harbor_self_test` | Fail closed; JSON |
| Slash | `/harbor …` | Help, status, self-test, or recommend |
| CLI | `hermes harbor {recommend,status,self-test}` | Human output on recommend |
| Skill | `collaboration-pattern-router` | Registered from packaged SKILL.md |

There are **no hooks**. That preserves Hermes prompt-cache invariants.

## Decision table

| Complexity | Seam | Pattern |
|------------|------|---------|
| simple | any | solo |
| medium | clear | pair |
| medium | weak/none | solo |
| complex | clear/weak | swarm |
| complex | none | pair |

`max_agents` can force solo when the budget is below the pattern’s need.

Cue lexicons live in `engine.py`. `data/thresholds.yaml` is **metadata**
for `harbor_status`; it is not the decision engine.

## Install paths

- Source / `hermes plugins install`: root `plugin.yaml` + root `__init__.py`
  re-exports `register`
- Wheel: entry point `hermes_agent.plugins` → `hermes_harbor`

Keep the two `plugin.yaml` files in sync.

## Failure modes

- Empty / invalid args → JSON `error` object, no exception
- Unexpected exception → logged, JSON `{"success": false, "error": "internal error"}`
- Invalid args → JSON `{"error": "..."}` (fail closed)
- Oversized task → truncated at 8000 characters
- Task text is never executed
