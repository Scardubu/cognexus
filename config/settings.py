"""Validated, immutable, environment-driven settings for Cognexus."""

from __future__ import annotations

import ipaddress
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    NoDecode,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from security.policies import looks_like_placeholder_secret

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APP_VERSION = "3.3.1"
SOURCE_SKILLS_ROOT = PROJECT_ROOT / ".agents" / "skills"
PACKAGED_SKILLS_ROOT = PROJECT_ROOT / "skill_runtime" / "bundled_skills"
DEFAULT_SKILLS_ROOT = SOURCE_SKILLS_ROOT if SOURCE_SKILLS_ROOT.is_dir() else PACKAGED_SKILLS_ROOT

Environment = Literal["development", "test", "staging", "production"]
SessionBackend = Literal["sqlite", "redis", "stateless"]
ModelValidationMode = Literal["off", "warn", "strict"]
PromptCacheRetention = Literal["off", "in_memory", "24h"]
CsvList = Annotated[list[str], NoDecode]

_RATE_LIMIT_PATTERN = re.compile(r"^[1-9][0-9]*/(?:second|minute|hour|day)s?$")


class Settings(BaseSettings):
    """Process configuration loaded from environment variables and ``.env``.

    The model is frozen so runtime code cannot mutate safety or routing policy after
    startup. Tests that need different values should construct a new ``Settings``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
        frozen=True,
        str_strip_whitespace=True,
        validate_default=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Allow deterministic test runs to opt out of local .env loading."""
        del settings_cls
        if os.getenv("NEXUS_DISABLE_DOTENV", "").strip().lower() in {"1", "true", "yes", "on"}:
            return init_settings, env_settings, file_secret_settings
        return init_settings, env_settings, dotenv_settings, file_secret_settings

    nexus_env: Environment = "development"
    nexus_log_level: str = "INFO"
    nexus_host: str = "127.0.0.1"
    nexus_port: int = Field(default=8000, ge=1, le=65535)
    nexus_workers: int = Field(default=1, ge=1, le=32)
    nexus_forwarded_allow_ips: str = "127.0.0.1"
    nexus_graceful_shutdown_seconds: int = Field(default=30, ge=5, le=300)
    nexus_http_concurrency_limit: int = Field(default=100, ge=1, le=10_000)
    nexus_http_backlog: int = Field(default=256, ge=16, le=65_535)

    openai_api_key: SecretStr | None = None
    nexus_api_key: SecretStr | None = None
    nexus_orchestrator_model: str = "gpt-5.5"
    nexus_specialist_model: str = "gpt-5.4-mini"
    nexus_guardrail_model: str = "gpt-5.4-mini"
    nexus_compaction_model: str = "gpt-5.4-mini"
    nexus_model_validation_mode: ModelValidationMode = "warn"
    nexus_model_validation_ttl_seconds: int = Field(default=300, ge=30, le=3600)
    nexus_model_validation_error_ttl_seconds: int = Field(default=30, ge=5, le=300)
    nexus_model_validation_max_pages: int = Field(default=20, ge=1, le=100)
    nexus_prompt_cache_retention: PromptCacheRetention = "24h"

    nexus_openai_timeout_seconds: float = Field(default=120.0, ge=5.0, le=600.0)
    nexus_openai_transport_retries: int = Field(default=1, ge=0, le=3)
    nexus_model_retries: int = Field(default=1, ge=0, le=3)
    nexus_max_concurrent_runs: int = Field(default=2, ge=1, le=32)
    nexus_queue_timeout_seconds: float = Field(default=30.0, ge=0.1, le=300.0)

    nexus_session_backend: SessionBackend = "sqlite"
    nexus_allow_sqlite_fallback: bool = True
    nexus_allow_stateless_fallback: bool = False
    nexus_sqlite_path: Path = PROJECT_ROOT / "data" / "nexus_sessions.db"
    nexus_session_cache_max_entries: int = Field(default=128, ge=1, le=4096)
    nexus_session_cache_ttl_seconds: int = Field(default=900, ge=30, le=86_400)

    redis_url: str = "redis://localhost:6379/0"
    nexus_redis_key_prefix: str = "nexus:session"
    nexus_redis_ttl_seconds: int = Field(default=604_800, ge=60)
    nexus_redis_connect_timeout_seconds: float = Field(default=2.0, ge=0.1, le=30.0)
    nexus_redis_socket_timeout_seconds: float = Field(default=5.0, ge=0.1, le=60.0)
    nexus_redis_max_connections: int = Field(default=16, ge=1, le=256)

    nexus_compaction_enabled: bool = True
    nexus_compaction_candidate_items: int = Field(default=10, ge=4, le=500)
    nexus_session_summary_max_chars: int = Field(default=1_200, ge=200, le=10_000)
    nexus_session_summary_item_limit: int = Field(default=24, ge=4, le=500)

    # Portable Agent Skills. Existing NEXUS_* names remain the compatibility contract.
    nexus_skills_enabled: bool = True
    nexus_skills_path: Path = DEFAULT_SKILLS_ROOT
    nexus_skill_max_file_bytes: int = Field(default=256_000, ge=1_024, le=2_000_000)
    nexus_skill_max_resource_bytes: int = Field(default=1_000_000, ge=1_024, le=10_000_000)
    nexus_skill_activation_max_chars: int = Field(default=40_000, ge=1_000, le=200_000)
    nexus_skill_catalog_max_chars: int = Field(default=24_000, ge=1_000, le=100_000)
    nexus_skill_cache_ttl_seconds: int = Field(default=60, ge=1, le=3_600)
    nexus_skill_allowed_names: CsvList = Field(default_factory=list)
    nexus_skill_denied_names: CsvList = Field(default_factory=list)

    nexus_rate_limit: str = "30/minute"
    nexus_rate_limit_storage_uri: str | None = None
    nexus_max_input_chars: int = Field(default=50_000, ge=100, le=1_000_000)
    nexus_max_request_bytes: int = Field(default=262_144, ge=1_024, le=10_000_000)
    nexus_max_output_chars: int = Field(default=200_000, ge=1_000, le=2_000_000)
    nexus_request_timeout_seconds: float = Field(default=180.0, ge=1.0, le=900.0)
    nexus_stream_chunk_chars: int = Field(default=768, ge=128, le=8192)
    nexus_cors_origins: CsvList = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    nexus_trusted_hosts: CsvList = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "testserver"]
    )
    nexus_enable_docs: bool = True

    nexus_otel_enabled: bool = True
    nexus_otel_console: bool = False
    nexus_otel_sample_ratio: float = Field(default=0.25, ge=0.0, le=1.0)
    otel_service_name: str = "cognexus"
    otel_exporter_otlp_endpoint: str | None = None
    trace_include_sensitive: Literal[False] = False

    max_turns: int = Field(default=12, ge=1, le=50)
    max_tool_calls_per_tier: int = Field(default=5, ge=1, le=20)

    @field_validator(
        "nexus_cors_origins",
        "nexus_trusted_hosts",
        "nexus_skill_allowed_names",
        "nexus_skill_denied_names",
        mode="before",
    )
    @classmethod
    def split_csv(cls, value: object) -> object:
        """Accept comma-separated environment values or ordinary lists."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("trace_include_sensitive", mode="before")
    @classmethod
    def reject_sensitive_trace_capture(cls, value: object) -> bool:
        """Accept explicit false spellings while making sensitive tracing impossible."""
        if value is False:
            return False
        if isinstance(value, str) and value.strip().lower() in {"false", "0", "no", "off"}:
            return False
        raise ValueError("TRACE_INCLUDE_SENSITIVE cannot be enabled")

    @field_validator("nexus_log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Normalize and validate the standard Python log levels we support."""
        normalized = value.upper()
        if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("unsupported log level")
        return normalized

    @field_validator("nexus_rate_limit")
    @classmethod
    def validate_rate_limit(cls, value: str) -> str:
        """Reject malformed SlowAPI limits during startup rather than at runtime."""
        if not _RATE_LIMIT_PATTERN.fullmatch(value):
            raise ValueError("rate limit must look like '30/minute'")
        return value

    @field_validator("nexus_forwarded_allow_ips")
    @classmethod
    def validate_forwarded_allow_ips(cls, value: str) -> str:
        """Validate the proxy addresses trusted to supply forwarded client headers."""
        entries = [item.strip() for item in value.split(",") if item.strip()]
        if not entries:
            raise ValueError("NEXUS_FORWARDED_ALLOW_IPS cannot be empty")
        for entry in entries:
            if entry == "*":
                continue
            try:
                ipaddress.ip_network(entry, strict=False)
            except ValueError as exc:
                raise ValueError(
                    "NEXUS_FORWARDED_ALLOW_IPS entries must be IP addresses or CIDR networks"
                ) from exc
        return ",".join(entries)

    @field_validator("nexus_rate_limit_storage_uri")
    @classmethod
    def validate_rate_limit_storage_uri(cls, value: str | None) -> str | None:
        """Accept only storage schemes supported by the synchronous limits backend."""
        if value is None:
            return None
        if not value.startswith(("memory://", "redis://", "rediss://")):
            raise ValueError(
                "NEXUS_RATE_LIMIT_STORAGE_URI must use memory://, redis://, or rediss://"
            )
        return value

    @field_validator("nexus_cors_origins")
    @classmethod
    def validate_cors_origins(cls, values: list[str]) -> list[str]:
        """Require exact HTTP(S) origins and reject credential-bearing URLs."""
        normalized: list[str] = []
        for value in values:
            if value == "*":
                normalized.append(value)
                continue
            parsed = urlsplit(value)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError("CORS origins must be absolute http:// or https:// origins")
            if parsed.username or parsed.password:
                raise ValueError("CORS origins cannot contain credentials")
            if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
                raise ValueError("CORS origins cannot contain paths, queries, or fragments")
            normalized.append(f"{parsed.scheme}://{parsed.netloc}")
        if len(normalized) != len(set(normalized)):
            raise ValueError("CORS origins cannot contain duplicates")
        return normalized

    @field_validator("nexus_trusted_hosts")
    @classmethod
    def validate_trusted_hosts(cls, values: list[str]) -> list[str]:
        """Reject malformed hosts that could weaken host-header protection."""
        normalized: list[str] = []
        for value in values:
            host = value.strip().lower()
            if not host or "://" in host or "/" in host or any(char.isspace() for char in host):
                raise ValueError("trusted hosts must be bare hostnames or wildcard host patterns")
            if "*" in host and host != "*" and (host.count("*") != 1 or not host.startswith("*.")):
                raise ValueError("trusted-host wildcards must use the '*.example.com' form")
            normalized.append(host)
        if len(normalized) != len(set(normalized)):
            raise ValueError("trusted hosts cannot contain duplicates")
        return normalized

    @field_validator("nexus_redis_key_prefix")
    @classmethod
    def redis_prefix_must_be_safe(cls, value: str) -> str:
        """Keep Redis keys within one predictable namespace."""
        normalized = value.strip().strip(":")
        if not normalized or len(normalized) > 80:
            raise ValueError("Redis key prefix must contain 1-80 characters")
        if any(character.isspace() for character in normalized):
            raise ValueError("Redis key prefix cannot contain whitespace")
        return normalized

    @field_validator("redis_url")
    @classmethod
    def redis_url_must_be_supported(cls, value: str) -> str:
        """Accept only Redis URL schemes understood by redis-py."""
        if not value.startswith(("redis://", "rediss://", "unix://")):
            raise ValueError("REDIS_URL must use redis://, rediss://, or unix://")
        return value

    @field_validator(
        "nexus_orchestrator_model",
        "nexus_specialist_model",
        "nexus_guardrail_model",
        "nexus_compaction_model",
    )
    @classmethod
    def model_name_must_be_nonempty(cls, value: str) -> str:
        """Reject blank model configuration without hardcoding a model catalog."""
        if not value:
            raise ValueError("model name cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_cross_field_policy(self) -> Self:
        """Enforce fail-closed production and multi-worker invariants."""
        if self.nexus_session_backend == "stateless" and not self.nexus_allow_stateless_fallback:
            raise ValueError("stateless backend requires NEXUS_ALLOW_STATELESS_FALLBACK=true")

        overlap = set(self.nexus_skill_allowed_names) & set(self.nexus_skill_denied_names)
        if overlap:
            raise ValueError(
                "skill names cannot appear in both NEXUS_SKILL_ALLOWED_NAMES and "
                "NEXUS_SKILL_DENIED_NAMES"
            )

        if self.nexus_skills_enabled and self.nexus_skill_catalog_max_chars < 1_000:
            raise ValueError("NEXUS_SKILL_CATALOG_MAX_CHARS is too small")
        if self.nexus_max_request_bytes < self.nexus_max_input_chars:
            raise ValueError("NEXUS_MAX_REQUEST_BYTES cannot be smaller than NEXUS_MAX_INPUT_CHARS")

        live_environment = self.nexus_env in {"staging", "production"}
        if live_environment:
            if "*" in self.nexus_cors_origins:
                raise ValueError("wildcard CORS is not allowed in staging or production")
            if "*" in self.nexus_trusted_hosts:
                raise ValueError("wildcard trusted hosts are not allowed in staging or production")
            if self.nexus_forwarded_allow_ips == "*":
                raise ValueError(
                    "wildcard forwarded-header trust is not allowed in staging or production"
                )
            if (
                self.nexus_session_backend == "redis"
                and self.effective_rate_limit_storage_uri == "memory://"
            ):
                raise ValueError("live Redis deployments require shared Redis rate-limit storage")
            if self.nexus_workers > 1 and self.nexus_session_backend == "sqlite":
                raise ValueError(
                    "multi-worker staging and production deployments require Redis sessions"
                )
            if (
                self.nexus_workers > 1
                and self.nexus_session_backend == "redis"
                and self.nexus_allow_sqlite_fallback
            ):
                raise ValueError(
                    "multi-worker live Redis deployments require NEXUS_ALLOW_SQLITE_FALLBACK=false"
                )
            if self.nexus_api_key:
                api_key = self.nexus_api_key.get_secret_value()
                if len(api_key) < 32 or looks_like_placeholder_secret(api_key):
                    raise ValueError(
                        "NEXUS_API_KEY must be a non-placeholder secret with at least "
                        "32 characters in staging or production"
                    )
            if self.openai_api_key:
                openai_key = self.openai_api_key.get_secret_value()
                if len(openai_key) < 20 or looks_like_placeholder_secret(openai_key):
                    raise ValueError(
                        "OPENAI_API_KEY must be a non-placeholder secret with at least "
                        "20 characters in staging or production"
                    )
            if (
                self.nexus_api_key
                and self.openai_api_key
                and self.nexus_api_key.get_secret_value() == self.openai_api_key.get_secret_value()
            ):
                raise ValueError("NEXUS_API_KEY must be distinct from OPENAI_API_KEY")

        if self.nexus_env == "production":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required in production")
            if not self.nexus_api_key:
                raise ValueError("NEXUS_API_KEY is required in production")
            if self.nexus_session_backend == "stateless":
                raise ValueError("stateless sessions are not allowed in production")
            if self.nexus_session_backend == "redis" and self.nexus_allow_sqlite_fallback:
                raise ValueError(
                    "production Redis sessions require NEXUS_ALLOW_SQLITE_FALLBACK=false"
                )
        return self

    @property
    def is_production(self) -> bool:
        """Return whether strict production policy applies."""
        return self.nexus_env == "production"

    @property
    def openai_key_value(self) -> str | None:
        """Reveal the OpenAI key only at an integration boundary."""
        return self.openai_api_key.get_secret_value() if self.openai_api_key else None

    @property
    def api_key_value(self) -> str | None:
        """Reveal the service API key only at the authentication boundary."""
        return self.nexus_api_key.get_secret_value() if self.nexus_api_key else None

    @property
    def effective_rate_limit_storage_uri(self) -> str:
        """Return shared Redis storage for live Redis deployments, otherwise memory."""
        if self.nexus_rate_limit_storage_uri is not None:
            return self.nexus_rate_limit_storage_uri
        if (
            self.nexus_env in {"staging", "production"}
            and self.nexus_session_backend == "redis"
            and self.redis_url.startswith(("redis://", "rediss://"))
        ):
            return self.redis_url
        return "memory://"

    @property
    def prompt_cache_retention(self) -> Literal["in_memory", "24h"] | None:
        """Translate the environment-friendly ``off`` value to the SDK's ``None``."""
        if self.nexus_prompt_cache_retention == "off":
            return None
        return self.nexus_prompt_cache_retention


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the immutable process-wide settings instance."""
    return Settings()


def reset_settings_cache() -> None:
    """Clear cached settings for tests and controlled configuration reloads."""
    get_settings.cache_clear()


STACK_MANIFEST_PATH = PROJECT_ROOT / "config" / "stack_manifest.json"
AGENT_REGISTRY_PATH = PROJECT_ROOT / "config" / "agent_registry.json"

TIER_NAMESPACE_MAP: dict[int, tuple[str, ...]] = {
    1: ("security",),
    2: ("correctness",),
    3: ("performance",),
    4: ("architecture",),
    5: ("ai_engineering",),
    6: ("release_tooling",),
    7: ("ux_motion",),
    8: ("compliance",),
}
TIER_NAMES: dict[int, str] = {
    1: "Security & Safety",
    2: "Correctness & Stability",
    3: "Performance & Scalability",
    4: "Architecture & Design",
    5: "AI Engineering",
    6: "Release / Productivity / Tooling",
    7: "UX / UI / Motion",
    8: "Vertical Domain Compliance",
}
VALID_APP_CONTEXTS = frozenset({"TaxBridge", "SabiScore", "Hashablanca", "SwarmX", "None"})
