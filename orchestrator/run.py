"""Command-line interface for Cognexus (NEXUS-compatible)."""

from __future__ import annotations

import argparse
import asyncio
import sys

from config.settings import APP_VERSION, get_settings
from observability.logging import configure_logging
from orchestrator.execution_modes import EXECUTION_MODES
from orchestrator.nexus_agent import run_nexus
from orchestrator.runtime import RunGate, sdk_runtime


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Run Cognexus from the command line")
    parser.add_argument("--version", action="version", version=f"cognexus {APP_VERSION}")
    parser.add_argument("message", nargs="+", help="Task for NEXUS")
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--mode",
        choices=EXECUTION_MODES,
        default="focus",
        dest="execution_mode",
        help="Execution mode controlling reasoning, output structure, and delegation.",
    )
    parser.add_argument(
        "--tier-override",
        type=int,
        choices=range(1, 9),
        default=None,
        help="Expert override for the primary routing tier (1-8).",
    )
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


async def _main() -> None:
    args = parse_args()
    settings = get_settings()
    configure_logging(
        settings.nexus_log_level,
        json_logs=settings.is_production,
        stream=sys.stderr,
    )
    gate = RunGate(settings.nexus_max_concurrent_runs)
    try:
        async with asyncio.timeout(settings.nexus_request_timeout_seconds):
            result = await run_nexus(
                " ".join(args.message),
                session_id=args.session_id,
                dry_run=args.dry_run,
                execution_mode=args.execution_mode,
                expert_tier_override=args.tier_override,
                settings=settings,
                run_gate=gate,
            )
        print(result.model_dump_json(indent=2) if args.as_json else result.response_text)
    finally:
        await sdk_runtime.close()


def main() -> None:
    """Run the synchronous console-script entry point."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
