"""Structured JSON logging configuration."""

from __future__ import annotations

import logging
import sys
from typing import Any, TextIO

import structlog

from observability.privacy import redact_observability_fields


def configure_logging(
    level: str = "INFO",
    *,
    json_logs: bool = True,
    stream: TextIO = sys.stdout,
) -> None:
    """Configure standard logging and structlog exactly once per process."""
    logging.basicConfig(
        format="%(message)s",
        stream=stream,
        level=getattr(logging, level.upper(), logging.INFO),
        force=True,
    )
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_observability_fields,
    ]
    processors.append(
        structlog.processors.JSONRenderer() if json_logs else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(file=stream),
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Return a bound structured logger."""
    return structlog.get_logger(name)
