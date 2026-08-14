"""Harbor — collaboration-pattern advisory plugin for Hermes Agent.

Provides tools, slash command, CLI, and bundled skill. No automatic hooks.
Advisory only — never swaps models or mutates conversation context.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from .engine import (
    __author__,
    __version__,
    dumps,
    format_human,
    load_thresholds,
    recommend,
    self_test,
)

logger = logging.getLogger(__name__)

# Metadata constants for wheel entry-point backfill when host leaves blanks
PLUGIN_NAME = "harbor"
PLUGIN_VERSION = __version__
PLUGIN_DESCRIPTION = (
    "Advisory collaboration-pattern router for multi-agent work "
    "(solo / pair / swarm) with oppositional self-test."
)
PLUGIN_AUTHOR = __author__


def _safe_text(value: Any, *, max_len: int = 8000) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    # Strip controls except newline/tab
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    if len(value) > max_len:
        value = value[:max_len]
    return value.strip()


def _parse_optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        return None
    if n < 1 or n > 32:
        return None
    return n


def _parse_enum(value: Any, allowed: set[str]) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    return v if v in allowed else None


def _recommend_handler(args: dict, **kwargs: Any) -> str:
    try:
        task = _safe_text(args.get("task") or args.get("text") or "")
        complexity = _parse_enum(args.get("complexity"), {"simple", "medium", "complex"})
        seam = _parse_enum(args.get("seam_clarity"), {"clear", "weak", "none"})
        max_agents = _parse_optional_int(args.get("max_agents"))
        if args.get("complexity") not in (None, "") and complexity is None:
            return json.dumps({"ok": False, "error": "complexity must be one of: simple, medium, complex"})
        if args.get("seam_clarity") not in (None, "") and seam is None:
            return json.dumps({"ok": False, "error": "seam_clarity must be one of: clear, weak, none"})
        if args.get("max_agents") not in (None, "") and max_agents is None:
            return json.dumps({"ok": False, "error": "max_agents must be an integer from 1 to 32"})
        if not task:
            return json.dumps({"ok": False, "error": "task is required and must be non-empty text"})

        rec = recommend(
            task,
            complexity=complexity,
            seam_clarity=seam,
            max_agents=max_agents,
        )
        payload = {
            "success": True,
            "recommendation": rec.to_dict(),
            "human": format_human(rec),
            "plugin_version": PLUGIN_VERSION,
        }
        return dumps(payload)
    except Exception:
        logger.exception("harbor_recommend failed")
        return json.dumps({"success": False, "error": "internal error"})


def _status_handler(args: dict, **kwargs: Any) -> str:
    try:
        thresholds = load_thresholds()
        return dumps(
            {
                "success": True,
                "name": PLUGIN_NAME,
                "version": PLUGIN_VERSION,
                "description": PLUGIN_DESCRIPTION,
                "author": PLUGIN_AUTHOR,
                "patterns": ["solo", "pair", "swarm"],
                "thresholds": thresholds,
                "hooks": "none (advisory only; cache-safe)",
            }
        )
    except Exception:
        logger.exception("harbor_status failed")
        return json.dumps({"success": False, "error": "internal error"})


def _self_test_handler(args: dict, **kwargs: Any) -> str:
    try:
        result = self_test()
        return dumps(result)
    except Exception:
        logger.exception("harbor_self_test failed")
        return json.dumps({"success": False, "error": "internal error"})


def _slash_handler(args: str = "", **kwargs: Any) -> str:
    text = _safe_text(args or "")
    if not text or text in {"help", "-h", "--help"}:
        return (
            "Harbor — collaboration pattern advisor\n"
            "Usage:\n"
            "  /harbor recommend <task description>\n"
            "  /harbor status\n"
            "  /harbor self-test\n"
            "Examples:\n"
            "  /harbor recommend Build a multi-model benchmark suite with API and runner modules\n"
        )
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""
    if cmd in {"status"}:
        return _status_handler({})
    if cmd in {"self-test", "selftest", "test"}:
        return _self_test_handler({})
    if cmd in {"recommend", "route", "r"}:
        return _recommend_handler({"task": rest})
    # bare text = recommend
    return _recommend_handler({"task": text})


def _cli_setup(subparser: Any) -> None:
    sub = subparser.add_subparsers(dest="harbor_cmd")
    rec = sub.add_parser("recommend", help="Recommend solo/pair/swarm for a task")
    rec.add_argument("task", nargs="+", help="Task description")
    rec.add_argument("--complexity", choices=["simple", "medium", "complex"])
    rec.add_argument("--seam", dest="seam_clarity", choices=["clear", "weak", "none"])
    rec.add_argument("--max-agents", type=int, default=None)
    sub.add_parser("status", help="Show harbor plugin status")
    sub.add_parser("self-test", help="Run oppositional self-test suite")


def _cli_handler(args: Any) -> int:
    cmd = getattr(args, "harbor_cmd", None)
    if cmd == "status":
        print(_status_handler({}))
        return 0
    if cmd == "self-test":
        out = json.loads(_self_test_handler({}))
        print(dumps(out))
        return 0 if out.get("success") else 1
    if cmd == "recommend":
        task = " ".join(getattr(args, "task", []) or [])
        payload = {
            "task": task,
            "complexity": getattr(args, "complexity", None),
            "seam_clarity": getattr(args, "seam_clarity", None),
            "max_agents": getattr(args, "max_agents", None),
        }
        raw = _recommend_handler(payload)
        data = json.loads(raw)
        if data.get("error"):
            print(raw)
            return 1
        print(data.get("human") or raw)
        return 0
    print("Usage: hermes harbor {recommend,status,self-test}")
    return 2


def register(ctx: Any) -> None:
    """Hermes plugin entry point."""
    # Backfill blank manifest fields only (wheel entry-point path)
    try:
        manifest = getattr(ctx, "manifest", None)
        if isinstance(manifest, dict):
            if not manifest.get("version"):
                manifest["version"] = PLUGIN_VERSION
            if not manifest.get("description"):
                manifest["description"] = PLUGIN_DESCRIPTION
            if not manifest.get("author"):
                manifest["author"] = PLUGIN_AUTHOR
    except Exception:  # noqa: BLE001
        pass

    ctx.register_tool(
        name="harbor_recommend",
        toolset="harbor",
        schema={
            "name": "harbor_recommend",
            "description": (
                "Recommend whether a task should use solo, pair, or swarm multi-agent "
                "collaboration. Use before launching delegate_task or multi-agent work. "
                "Returns pattern, complexity, seam clarity, rationale, and anti-patterns."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description to classify.",
                    },
                    "complexity": {
                        "type": "string",
                        "description": "Optional override: simple | medium | complex",
                    },
                    "seam_clarity": {
                        "type": "string",
                        "description": "Optional override: clear | weak | none",
                    },
                    "max_agents": {
                        "type": "integer",
                        "description": "Optional agent budget cap (1-32).",
                    },
                },
                "required": ["task"],
            },
        },
        handler=_recommend_handler,
        description="Recommend solo/pair/swarm collaboration pattern for a task.",
    )

    ctx.register_tool(
        name="harbor_status",
        toolset="harbor",
        schema={
            "name": "harbor_status",
            "description": "Show Harbor plugin status, version, and threshold metadata.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=_status_handler,
        description="Harbor plugin status.",
    )

    ctx.register_tool(
        name="harbor_self_test",
        toolset="harbor",
        schema={
            "name": "harbor_self_test",
            "description": "Run Harbor oppositional self-test suite and return pass/fail cases.",
            "parameters": {"type": "object", "properties": {}},
        },
        handler=_self_test_handler,
        description="Harbor self-test suite.",
    )

    ctx.register_command(
        name="harbor",
        handler=_slash_handler,
        description="Harbor: /harbor recommend <task> | status | self-test",
        args_hint="<recommend|status|self-test> [task...]",
    )

    ctx.register_cli_command(
        name="harbor",
        help="Collaboration pattern advisor (solo/pair/swarm)",
        setup_fn=_cli_setup,
        handler_fn=_cli_handler,
    )

    skill_path = Path(__file__).parent / "skill" / "SKILL.md"
    if skill_path.exists():
        ctx.register_skill(name="collaboration-pattern-router", path=skill_path)

    logger.info("harbor plugin registered v%s", PLUGIN_VERSION)
