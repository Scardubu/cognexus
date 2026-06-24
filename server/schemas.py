"""Strict HTTP request and response schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from orchestrator.execution_modes import ExecutionMode
from orchestrator.skill_recommender import SkillRecommendation
from security.identifiers import validate_session_id


class RunRequest(BaseModel):
    """A single Cognexus execution request."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1)
    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9._:-]+$",
    )
    dry_run: bool = False
    execution_mode: ExecutionMode = "focus"
    expert_tier_override: int | None = Field(default=None, ge=1, le=8)

    @field_validator("session_id")
    @classmethod
    def normalize_session_id(cls, value: str | None) -> str | None:
        """Apply the same identifier policy used by HTTP paths and session storage."""
        return validate_session_id(value) if value is not None else None

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        """Normalize leading/trailing whitespace and reject blank input."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("message cannot be blank")
        return normalized


class RunResponse(BaseModel):
    """Stable HTTP representation of a Cognexus result."""

    model_config = ConfigDict(extra="forbid")
    run_id: str
    session_id: str
    response_text: str
    tier: int
    tier_name: str
    app_context: str
    execution_mode: ExecutionMode = "focus"
    classification_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    classification_ambiguity: str = "low"
    supporting_tiers: list[int] = Field(default_factory=list)
    model: str
    trace_id: str | None
    trace_validation: dict[str, Any]
    constraint_violations: list[dict[str, str]]
    token_usage: dict[str, int] | None
    session_backend: str
    degraded: bool
    warnings: list[str]
    next_actions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    recommended_skills: list[SkillRecommendation] = Field(default_factory=list)
    session_intelligence: dict[str, Any] = Field(default_factory=dict)
    queue_wait_ms: float
    duration_ms: float


class HealthResponse(BaseModel):
    """Liveness or readiness response."""

    model_config = ConfigDict(extra="forbid")
    status: Literal["ok", "ready", "not_ready"]
    service: str = "cognexus"
    details: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """Safe session metadata response."""

    model_config = ConfigDict(extra="forbid")
    session_id: str
    requested_backend: str
    effective_backend: str
    degraded: bool
    warnings: list[str]
    item_count: int
    item_types: list[str]
    rolling_summary: str = "No retained conversational items."
    continuity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    context_item_count: int = Field(default=0, ge=0)
    represented_item_count: int = Field(default=0, ge=0)
    role_counts: dict[str, int] = Field(default_factory=dict)
    compaction_recommended: bool = False
    context_optimization: str = "empty_session"


class SkillSummary(BaseModel):
    """Public discovery metadata for one installed Agent Skill."""

    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    category: str
    risk: Literal["low", "medium", "high"]


class SkillCatalogResponse(BaseModel):
    """Authenticated skill catalog response without instruction bodies."""

    model_config = ConfigDict(extra="forbid")
    count: int = Field(ge=0)
    skills: list[SkillSummary]


class SkillResourceSummary(BaseModel):
    """Safe resource metadata for one activated skill."""

    model_config = ConfigDict(extra="forbid")
    path: str
    kind: Literal["reference", "example", "asset", "script"]
    size_bytes: int = Field(ge=0)


class SkillDetailResponse(BaseModel):
    """Authenticated skill metadata and resource inventory."""

    model_config = ConfigDict(extra="forbid")
    name: str
    description: str
    category: str
    risk: Literal["low", "medium", "high"]
    fingerprint: str
    resources: list[SkillResourceSummary]


class SkillRecommendationRequest(BaseModel):
    """Deterministic skill recommendation request."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=50_000)
    execution_mode: ExecutionMode = "focus"
    expert_tier_override: int | None = Field(default=None, ge=1, le=8)

    @field_validator("message")
    @classmethod
    def normalize_message(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("message cannot be blank")
        return normalized


class SkillRecommendationResponse(BaseModel):
    """Explainable mode-aware skill recommendations."""

    model_config = ConfigDict(extra="forbid")
    execution_mode: ExecutionMode
    tier: int = Field(ge=1, le=8)
    tier_name: str
    classification_confidence: float = Field(ge=0.0, le=1.0)
    classification_ambiguity: str
    recommended_skills: list[SkillRecommendation]


class ErrorResponse(BaseModel):
    """Structured JSON error envelope."""

    model_config = ConfigDict(extra="forbid")
    error: str
    message: str
    request_id: str | None = None
    details: dict[str, Any] | None = None
