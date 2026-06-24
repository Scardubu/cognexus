"""Configuration-driven Uvicorn launcher for Cognexus deployments."""

from __future__ import annotations

import argparse

import uvicorn

from config.settings import APP_VERSION, Settings, get_settings


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Cognexus HTTP API")
    parser.add_argument("--version", action="version", version=f"cognexus-server {APP_VERSION}")
    return parser


def build_uvicorn_options(settings: Settings) -> dict[str, object]:
    """Translate validated Cognexus settings into bounded Uvicorn options."""
    return {
        "host": settings.nexus_host,
        "port": settings.nexus_port,
        "workers": settings.nexus_workers,
        "proxy_headers": True,
        "forwarded_allow_ips": settings.nexus_forwarded_allow_ips,
        "server_header": False,
        "timeout_keep_alive": 5,
        "timeout_graceful_shutdown": settings.nexus_graceful_shutdown_seconds,
        "limit_concurrency": settings.nexus_http_concurrency_limit,
        "backlog": settings.nexus_http_backlog,
    }


def main() -> None:
    """Start Uvicorn using only validated environment-backed settings."""
    _parser().parse_args()
    settings = get_settings()
    uvicorn.run(
        "server.app:app",
        host=settings.nexus_host,
        port=settings.nexus_port,
        workers=settings.nexus_workers,
        proxy_headers=True,
        forwarded_allow_ips=settings.nexus_forwarded_allow_ips,
        server_header=False,
        timeout_keep_alive=5,
        timeout_graceful_shutdown=settings.nexus_graceful_shutdown_seconds,
        limit_concurrency=settings.nexus_http_concurrency_limit,
        backlog=settings.nexus_http_backlog,
    )


if __name__ == "__main__":
    main()
