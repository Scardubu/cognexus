"""Configuration-driven HTTP server launcher tests."""

from __future__ import annotations

from config.settings import Settings
from server.run import build_uvicorn_options


def test_server_launcher_honors_existing_runtime_environment_contract() -> None:
    settings = Settings(
        nexus_env="test",
        nexus_host="127.0.0.2",
        nexus_port=9123,
        nexus_workers=3,
        nexus_forwarded_allow_ips="10.0.0.0/8,192.168.1.10",
        nexus_graceful_shutdown_seconds=45,
        nexus_http_concurrency_limit=240,
        nexus_http_backlog=512,
        nexus_compaction_enabled=False,
        nexus_model_validation_mode="off",
        nexus_otel_enabled=False,
    )

    assert build_uvicorn_options(settings) == {
        "host": "127.0.0.2",
        "port": 9123,
        "workers": 3,
        "proxy_headers": True,
        "forwarded_allow_ips": "10.0.0.0/8,192.168.1.10",
        "server_header": False,
        "timeout_keep_alive": 5,
        "timeout_graceful_shutdown": 45,
        "limit_concurrency": 240,
        "backlog": 512,
    }
