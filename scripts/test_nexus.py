#!/usr/bin/env python3
"""NEXUS smoke test and optional live execution utility."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings  # noqa: E402
from nexus_agents.registry import validate_agent_registry  # noqa: E402
from nexus_agents.specialists import AGENT_REGISTRY  # noqa: E402
from observability.logging import configure_logging  # noqa: E402
from orchestrator.model_router import validate_configured_models  # noqa: E402
from orchestrator.nexus_agent import run_nexus  # noqa: E402
from orchestrator.runtime import RunGate, sdk_runtime  # noqa: E402
from tools.registry import implemented_tools, validate_tool_registry  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate NEXUS installation")
    parser.add_argument("--dry-run", action="store_true", help="Do not call OpenAI")
    parser.add_argument(
        "--message",
        default="Analyze the NEXUS production architecture and identify operational risks.",
    )
    parser.add_argument("--session-id", default="smoke-test")
    parser.add_argument("--validate-models", action="store_true")
    return parser.parse_args()


async def main() -> int:
    args = parse_args()
    registry_errors = validate_agent_registry() + validate_tool_registry()
    if registry_errors:
        print(json.dumps({"status": "failed", "registry_errors": registry_errors}, indent=2))
        return 1

    settings = get_settings()
    configure_logging(
        settings.nexus_log_level,
        json_logs=settings.is_production,
        stream=sys.stderr,
    )
    gate = RunGate(settings.nexus_max_concurrent_runs)
    model_status: dict[str, object] = {"checked": False}
    try:
        if args.validate_models:
            model_status = await validate_configured_models(settings)
            if model_status.get("missing") and settings.nexus_model_validation_mode == "strict":
                print(json.dumps({"status": "failed", "models": model_status}, indent=2))
                return 1

        async with asyncio.timeout(settings.nexus_request_timeout_seconds):
            result = await run_nexus(
                args.message,
                session_id=args.session_id,
                dry_run=args.dry_run,
                settings=settings,
                run_gate=gate,
            )
        payload = {
            "status": "ok",
            "dry_run": args.dry_run,
            "agents": len(AGENT_REGISTRY),
            "implemented_tools": len(implemented_tools()),
            "models": model_status,
            "result": result.model_dump(mode="json"),
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0
    finally:
        await sdk_runtime.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
