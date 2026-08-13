---
name: collaboration-pattern-router
description: Use when choosing solo vs pair vs swarm multi-agent collaboration before delegate_task.
version: 1.2.0
author: Aiona Edge / SMF Works
license: MIT
metadata:
  hermes:
    tags: [multi-agent, collaboration, coordination, delegate, harbor, routing]
    related_skills: [hermes-agent, hybrid-contextual-routing]
---

# Collaboration Pattern Router

## Overview

Decide **solo**, **pair**, or **swarm** *before* launching multi-agent work. Based on SMF Works' coordination-cost experiment: multi-agent is not free. Coordination cost (context transfer, merge, waiting, redundancy, token tax) often exceeds parallelism gain on simple and medium tasks.

Harbor metaphor: Lofoten fishing fleets do not leave harbor in every weather. Stockfish seasons reward waiting for the right window. Same rule for agents — leave harbor only when the sea (task complexity + seam clarity) justifies the fleet.

## When to Use

- Before `delegate_task` or spawning additional Hermes processes
- When a teammate proposes "let's swarm this"
- When a task might be multi-domain or multi-file
- When reviewing why a multi-agent run felt slow or redundant

**Don't use for:** model selection (use hybrid-contextual-routing / route_classify), ordinary single-file edits you already know are solo work.

## Decision Table

| Complexity | Seam clarity | Pattern | Why |
|------------|--------------|---------|-----|
| Simple (1 domain, linear) | any | **solo** | Coordination > parallelism |
| Medium (2 domains / research+synthesis) | clear | **pair** | Depth win, speed loss (~3-4×) |
| Medium | none/weak | **solo** | Coherence beats forced split |
| Complex (3+ domains, multi-file build) | clear/weak | **swarm** | Solo often cannot finish in time |
| Complex | none | **pair** | Forced bipartition beats vague swarm |

## Complexity Signals

**Simple:** one file, one function, quick answer, status check, single narrative paragraph.

**Medium:** research + report, compare N options, competitive analysis, investigate-and-recommend.

**Complex:** multi-model benchmark suite, multi-component build, architecture + implement + evaluate, multi-domain orchestration.

## Seam Clarity Signals

**Clear seams:** research vs analysis; API layer vs runner; code vs tests; frontend vs backend; independent modules with non-overlapping outputs.

**No seam:** consistent voice required; tightly coupled logic; continuous argument; "write the first half / second half" of one document.

## Procedure

1. **State the deliverable** in one sentence.
2. **Name domains** involved (coding, research, writing, ops, data…).
3. **Name the seam** — if you cannot, default toward solo (or pair only if complex).
4. **Call Harbor** if available:
   - Tool: `harbor_recommend` with the task text
   - CLI: `hermes harbor recommend "<task>"`
   - Slash: `/harbor recommend <task>`
5. **Act on the pattern:**
   - **solo** — do the work yourself; no `delegate_task`
   - **pair** — two self-contained briefs; one merge round
   - **swarm** — coordinator owns merge; ≥3 independent work packages; wait for all workers before assemble
6. **Done when** you have a chosen pattern, a written rationale, and either started work or launched agents with non-overlapping briefs.

## Cost Equation

```
Net Productivity = Parallelism Gain - Coordination Cost
```

Coordination cost includes:

1. Context transfer (every worker needs a full brief)
2. Merge effort (styles, overlaps, assumptions)
3. Waiting (slowest worker gates the parent)
4. Redundancy (overlapping sections without tight seams)
5. Token tax (often 2–5× input tokens per extra agent)

## Anti-Patterns

1. **Default swarm** — launching many agents because the task "sounds big."
2. **Half-document splits** — agent A writes intro, agent B writes body of one essay.
3. **Placeholder merge** — coordinator writes "TODO insert worker output" before workers finish.
4. **Ignoring token tax** — celebrating parallel wall time while burning 25× tokens.
5. **Confusing volume with quality** — 8× more bytes that are redundant is not a win.

## Verification Checklist

- [ ] Pattern chosen: solo | pair | swarm
- [ ] Complexity and seam named explicitly
- [ ] If pair/swarm: each agent has a self-contained brief and non-overlapping output path
- [ ] If swarm: coordinator will wait for all workers before merge
- [ ] Harbor self-test green when changing the plugin (`hermes harbor self-test`)

## Evidence Basis

SMF Clearinghouse: [The Coordination Cost: When Multi-Agent Collaboration Actually Helps](https://www.smfclearinghouse.com/blog/2026-08-08-coordination-cost-framework) (2026-08-08). Real `delegate_task` runs across solo/pair/swarm on documentation, competitive analysis, and benchmark-suite builds.
