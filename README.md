# hermes-plugin-harbor

**Leave harbor only when the weather justifies the fleet.**

Advisory collaboration-pattern router for [Hermes Agent](https://github.com/NousResearch/hermes-agent). Recommends **solo**, **pair**, or **swarm** before multi-agent launches — based on real coordination-cost measurements from SMF Works.

> Cache-safe. No automatic hooks. No mid-conversation model swap. Tools + slash + CLI + bundled skill only.

## Why this exists

Hermes teams default to multi-agent too easily. Our 2026-08-08 experiment found:

| Pattern | Best for | Failure mode |
|---------|----------|--------------|
| **solo** | Simple / medium without seam | Complex builds time out |
| **pair** | Medium with clear seam; complex bipartition | Redundant halves; 3–4× time |
| **swarm** | Complex with clear multi-way seams | Placeholder merges; token tax |

Blog: [The Coordination Cost](https://www.smfclearinghouse.com/blog/2026-08-08-coordination-cost-framework)

Current version: **1.1.0**.

## Install

```bash
# Git / source install into active Hermes home
hermes plugins install smfworks/hermes-plugin-harbor --enable

# Or from a local checkout
hermes plugins install file:///absolute/path/to/hermes-plugin-harbor --enable

# pip surface
pip install .
```

Named profile:

```bash
hermes -p aiona plugins install smfworks/hermes-plugin-harbor --enable
```

## Usage

### Tool (agent)

```text
harbor_recommend(task="Build a multi-model benchmark suite with API and runner modules")
harbor_status()
harbor_self_test()
```

### Slash

```text
/harbor recommend Build a multi-model benchmark suite with API and runner modules
/harbor status
/harbor self-test
```

### CLI

```bash
hermes harbor recommend "Research three tools and write a competitive analysis; split research and analysis"
hermes harbor status
hermes harbor self-test
```

## Decision table (shipped)

| Complexity | Seam | Pattern |
|------------|------|---------|
| simple | any | solo |
| medium | clear | pair |
| medium | weak/none | solo |
| complex | clear/weak | swarm |
| complex | none | pair |

## Design principles

1. **Advisory only** — agent decides; Harbor recommends.
2. **No hooks** — preserves Hermes prompt-cache invariants.
3. **Fail closed on bad args** — invalid enums return JSON errors, never raise.
4. **Stdlib only** — zero runtime dependencies.
5. **Bundled skill** — `collaboration-pattern-router` registers with the plugin.

## Develop / test

```bash
cd hermes-plugin-harbor
python -m pytest -q
python -c "from hermes_harbor.engine import self_test; import json; print(json.dumps(self_test(), indent=2))"
```

## Lofoten note

Built during SMF Works' Lofoten sprint (Aug 2026). The name *Harbor* is deliberate: Arctic fishing fleets wait for weather windows; stockfish seasons reward discipline over constant departure. Multi-agent systems need the same restraint.

## License

MIT — SMF Works / Aiona Edge
