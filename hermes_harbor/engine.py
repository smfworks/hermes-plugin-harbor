"""Harbor collaboration-pattern engine.

Deterministic, cache-safe advisory logic. No hooks, no mid-turn model swap.
Based on SMF Works coordination-cost experiment (2026-08-08):
solo wins simple; pair/swarm win only when seams are clear and complexity is high.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

__version__ = "1.0.0"
__author__ = "Aiona Edge / SMF Works"

# ── Cue lexicons (literal, bounded, token-boundary matched) ─────────────

_COMPLEX_CUES = (
    "multi-domain",
    "multi domain",
    "multi-file",
    "multi file",
    "multi-component",
    "multi component",
    "benchmark suite",
    "end-to-end",
    "e2e",
    "pipeline",
    "orchestration",
    "architecture",
    "refactor",
    "migrate",
    "integration",
    "full stack",
    "full-stack",
    "deploy",
    "release gate",
)

_MEDIUM_CUES = (
    "research",
    "compare",
    "comparison",
    "analysis",
    "analyze",
    "report",
    "investigate",
    "evaluate",
    "review",
    "summarize multiple",
    "competitive",
    "literature",
)

_SIMPLE_CUES = (
    "write a function",
    "fix a typo",
    "one file",
    "single file",
    "quick edit",
    "rename",
    "answer",
    "explain",
    "one paragraph",
    "short note",
    "status check",
)

_SEAM_CUES = (
    "you research i analyze",
    "research and analyze",
    "research and analysis",
    "code and tests",
    "frontend and backend",
    "api and runner",
    "write and review",
    "parallel",
    "split",
    "divide",
    "two parts",
    "two agents",
    "worker",
    "subtask",
    "module a",
    "module b",
)

_NO_SEAM_CUES = (
    "consistent voice",
    "same style",
    "single narrative",
    "one coherent",
    "continuous argument",
    "no clear split",
    "tightly coupled",
)

_DOMAIN_HINTS = (
    ("coding", ("code", "python", "typescript", "api", "function", "bug", "test suite", "implement")),
    ("research", ("research", "paper", "literature", "sources", "cite", "investigate")),
    ("writing", ("blog", "docs", "documentation", "essay", "prose", "copy")),
    ("ops", ("deploy", "cron", "infra", "server", "monitor", "incident")),
    ("creative", ("poem", "story", "creative", "design", "image")),
    ("data", ("benchmark", "dataset", "metrics", "evaluate", "score")),
)


@dataclass(frozen=True)
class HarborRecommendation:
    pattern: str  # solo | pair | swarm
    complexity: str  # simple | medium | complex
    confidence: float  # 0.0-1.0
    seam_clarity: str  # clear | weak | none
    domains: list[str]
    rationale: str
    do_now: list[str]
    anti_patterns: list[str]
    estimated_coordination_rounds: int
    evidence_basis: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tokenize_match(text: str, cue: str) -> bool:
    """Token-boundary-ish match; cues may contain spaces."""
    t = text.lower()
    c = cue.lower().strip()
    if not c or len(c) > 64:
        return False
    # Escape and allow flexible internal whitespace
    parts = [re.escape(p) for p in c.split() if p]
    if not parts:
        return False
    pattern = r"(?<!\w)" + r"[\s\-_/]+".join(parts) + r"(?!\w)"
    return re.search(pattern, t) is not None


def _count_cues(text: str, cues: tuple[str, ...]) -> int:
    return sum(1 for c in cues if _tokenize_match(text, c))


def _detect_domains(text: str) -> list[str]:
    found: list[str] = []
    for name, cues in _DOMAIN_HINTS:
        if any(_tokenize_match(text, c) for c in cues):
            found.append(name)
    return found or ["general"]


def _complexity(text: str, domains: list[str], explicit: str | None) -> tuple[str, float, str]:
    if explicit in {"simple", "medium", "complex"}:
        return explicit, 0.95, "explicit complexity provided by caller"

    complex_hits = _count_cues(text, _COMPLEX_CUES)
    medium_hits = _count_cues(text, _MEDIUM_CUES)
    simple_hits = _count_cues(text, _SIMPLE_CUES)
    domain_count = len([d for d in domains if d != "general"])

    # Length as weak signal. Medium cues alone must not promote to complex —
    # complex requires explicit complex markers and/or multi-domain breadth.
    words = len(text.split())
    score = 0
    score += complex_hits * 3
    score += medium_hits * 2
    score += domain_count * 2
    score += 2 if words > 80 else 0
    score += 1 if words > 40 else 0
    score -= simple_hits * 2

    is_complex = (
        complex_hits >= 2
        or domain_count >= 3
        or (complex_hits >= 1 and (domain_count >= 2 or words > 40 or medium_hits >= 1))
    )
    if is_complex:
        conf = min(0.9, 0.55 + 0.1 * complex_hits + 0.05 * domain_count)
        return "complex", conf, f"complex_hits={complex_hits} domains={domain_count} words={words}"
    if score >= 2 or medium_hits >= 1 or domain_count >= 2:
        conf = min(0.85, 0.5 + 0.1 * medium_hits + 0.05 * domain_count)
        return "medium", conf, f"medium_hits={medium_hits} domains={domain_count} words={words}"
    conf = min(0.85, 0.55 + 0.1 * max(simple_hits, 1))
    return "simple", conf, f"simple_hits={simple_hits} domains={domain_count} words={words}"


def _seam(text: str, explicit: str | None) -> tuple[str, str]:
    if explicit in {"clear", "weak", "none"}:
        return explicit, "explicit seam clarity provided by caller"
    clear = _count_cues(text, _SEAM_CUES)
    none = _count_cues(text, _NO_SEAM_CUES)
    if none and not clear:
        return "none", f"no_seam_cues={none}"
    if clear >= 2:
        return "clear", f"seam_cues={clear}"
    if clear == 1:
        return "weak", f"seam_cues={clear}"
    return "none", "no seam cues detected"


def recommend(
    task: str,
    *,
    complexity: str | None = None,
    seam_clarity: str | None = None,
    max_agents: int | None = None,
) -> HarborRecommendation:
    """Recommend solo | pair | swarm for a task description."""
    text = (task or "").strip()
    if not text:
        return HarborRecommendation(
            pattern="solo",
            complexity="simple",
            confidence=1.0,
            seam_clarity="none",
            domains=["general"],
            rationale="Empty task — default to solo; nothing to parallelize.",
            do_now=["Clarify the task before launching agents."],
            anti_patterns=["Do not spawn subagents without a task."],
            estimated_coordination_rounds=0,
            evidence_basis="default-empty",
        )
    if len(text) > 8000:
        text = text[:8000]

    domains = _detect_domains(text)
    cplx, conf, c_ev = _complexity(text, domains, complexity)
    seam, s_ev = _seam(text, seam_clarity)

    # Core decision table from coordination-cost experiment
    if cplx == "simple":
        pattern = "solo"
        rounds = 0
        rationale = (
            "Simple/single-domain work: coordination cost exceeds parallelism gain. "
            "Solo maintains full context and finishes faster."
        )
        do_now = [
            "Keep one agent with full context.",
            "Write the deliverable directly; skip delegate_task.",
        ]
        anti = [
            "Do not split a linear write across agents (produces redundant sections).",
            "Do not spawn workers for one-file edits.",
        ]
    elif cplx == "medium":
        if seam == "clear" and (max_agents is None or max_agents >= 2):
            pattern = "pair"
            rounds = 1
            rationale = (
                "Medium complexity with a clear seam: pair wins on depth "
                "(parallel research/analysis) but expect ~3-4× wall time vs solo."
            )
            do_now = [
                "Split along the natural seam (e.g., research vs analysis).",
                "Give each agent a self-contained brief.",
                "Merge once; do not open a second coordination round unless blocked.",
            ]
            anti = [
                "Do not force a split without a seam.",
                "Do not expect pair to beat solo on pure speed for medium tasks.",
            ]
        else:
            pattern = "solo"
            rounds = 0
            rationale = (
                "Medium complexity without a clear seam: stay solo for coherence. "
                "Pair only if you can name an independent split."
            )
            do_now = [
                "Stay solo unless you can name two independent subtasks.",
                "If depth is insufficient, add research tools — not agents.",
            ]
            anti = [
                "Do not invent artificial half-document splits.",
            ]
    else:  # complex
        if seam in {"clear", "weak"} and (max_agents is None or max_agents >= 3):
            pattern = "swarm"
            rounds = 2
            rationale = (
                "Complex multi-domain work: solo often cannot finish in time. "
                "Swarm (coordinator + workers) is justified when seams exist."
            )
            do_now = [
                "Appoint a coordinator who owns merge quality.",
                "Define 3+ independent subtasks with non-overlapping outputs.",
                "Wait for all workers before assembling; no placeholder merges.",
                "Standardize output format (paths, markdown sections, JSON schema).",
            ]
            anti = [
                "Do not launch swarm without a coordinator brief.",
                "Do not merge before all workers finish (placeholder docs rot).",
                "Do not ignore token tax: each worker needs full context (~2-5×).",
            ]
        elif max_agents is not None and max_agents < 2:
            pattern = "solo"
            rounds = 0
            rationale = "Complex task but max_agents < 2 — constrained to solo; timebox and chunk the work."
            do_now = ["Chunk the work into sequential milestones.", "Persist intermediate artifacts to disk."]
            anti = ["Do not silently ignore the agent cap."]
        else:
            pattern = "pair"
            rounds = 1
            rationale = (
                "Complex task with weak/no seam: use pair on the best available split "
                "rather than a loose swarm. Prefer two strong modules over many vague workers."
            )
            do_now = [
                "Force a clean bipartition (e.g., implementation vs evaluation).",
                "If still too large, sequence pairs rather than growing the swarm.",
            ]
            anti = [
                "Do not spawn many workers without independent work packages.",
            ]

    # Confidence dampen if cues conflict
    if cplx == "complex" and seam == "none":
        conf = min(conf, 0.7)
    if cplx == "simple" and _count_cues(text, _COMPLEX_CUES):
        conf = min(conf, 0.65)

    return HarborRecommendation(
        pattern=pattern,
        complexity=cplx,
        confidence=round(conf, 2),
        seam_clarity=seam,
        domains=domains,
        rationale=rationale,
        do_now=do_now,
        anti_patterns=anti,
        estimated_coordination_rounds=rounds,
        evidence_basis=f"{c_ev}; {s_ev}; experiment=smf-coordination-cost-2026-08-08",
    )


def format_human(rec: HarborRecommendation) -> str:
    lines = [
        f"**Harbor recommendation: `{rec.pattern}`** (confidence {rec.confidence:.2f})",
        f"- Complexity: {rec.complexity}",
        f"- Seam clarity: {rec.seam_clarity}",
        f"- Domains: {', '.join(rec.domains)}",
        f"- Coordination rounds: {rec.estimated_coordination_rounds}",
        f"- Rationale: {rec.rationale}",
        "- Do now:",
    ]
    for item in rec.do_now:
        lines.append(f"  - {item}")
    lines.append("- Anti-patterns:")
    for item in rec.anti_patterns:
        lines.append(f"  - {item}")
    lines.append(f"- Evidence: {rec.evidence_basis}")
    return "\n".join(lines)


def self_test() -> dict[str, Any]:
    """Oppositional self-test suite. Returns pass/fail with cases."""
    cases = [
        {
            "name": "empty",
            "task": "",
            "expect_pattern": "solo",
        },
        {
            "name": "simple_function",
            "task": "Write a function that reverses a string in one file.",
            "expect_pattern": "solo",
        },
        {
            "name": "medium_research_clear_seam",
            "task": (
                "Research Ollama vs LM Studio and analyze the findings in a competitive report. "
                "Split research and analysis between two agents."
            ),
            "expect_pattern": "pair",
        },
        {
            "name": "medium_no_seam",
            "task": "Write a coherent competitive analysis of three tools with a single narrative voice.",
            "expect_pattern": "solo",
        },
        {
            "name": "complex_benchmark_suite",
            "task": "Build a multi-model benchmark suite with API integration, scoring, and JSON reporting across coding reasoning creative categories. Split api and runner modules.",
            "expect_pattern": "swarm",
        },
        {
            "name": "complex_no_seam_pair",
            "task": "Implement a full-stack multi-component deployment pipeline refactor that is tightly coupled with continuous argument across modules.",
            "expect_pattern": "pair",
        },
        {
            "name": "explicit_override",
            "task": "anything",
            "complexity": "simple",
            "seam_clarity": "clear",
            "expect_pattern": "solo",
        },
        {
            "name": "max_agents_cap",
            "task": "Build a multi-domain multi-file end-to-end benchmark orchestration architecture with parallel workers.",
            "max_agents": 1,
            "expect_pattern": "solo",
        },
    ]
    results = []
    failures = 0
    for case in cases:
        rec = recommend(
            case["task"],
            complexity=case.get("complexity"),
            seam_clarity=case.get("seam_clarity"),
            max_agents=case.get("max_agents"),
        )
        ok = rec.pattern == case["expect_pattern"]
        if not ok:
            failures += 1
        results.append(
            {
                "name": case["name"],
                "ok": ok,
                "expected": case["expect_pattern"],
                "got": rec.pattern,
                "confidence": rec.confidence,
            }
        )
    return {
        "success": failures == 0,
        "version": __version__,
        "passed": len(results) - failures,
        "failed": failures,
        "total": len(results),
        "cases": results,
    }


def load_thresholds(path: Path | None = None) -> dict[str, Any]:
    """Optional thresholds file (YAML or JSON). Pure advisory metadata."""
    p = path or Path(__file__).parent / "data" / "thresholds.yaml"
    if not p.exists():
        return {"source": "builtin", "path": str(p)}
    text = p.read_text(encoding="utf-8")
    # Minimal YAML subset: key: value lines only (no PyYAML dependency required)
    data: dict[str, Any] = {"source": "file", "path": str(p)}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip().strip("\"'")
    return data


def dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)
