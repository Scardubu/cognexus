"""Typed models for portable Agent Skills discovery and activation."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SkillRisk = Literal["low", "medium", "high"]
SkillSeverity = Literal["error", "warning"]


class SkillMetadata(BaseModel):
    """Validated discovery metadata loaded from one ``SKILL.md`` file."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=1024)
    location: Path
    directory: Path
    license: str | None = None
    compatibility: str | None = Field(default=None, max_length=500)
    metadata: dict[str, str] = Field(default_factory=dict)
    allowed_tools: str | None = None
    category: str = "uncategorized"
    risk: SkillRisk = "medium"


class SkillResource(BaseModel):
    """Safe, relative resource descriptor disclosed during activation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: str
    kind: Literal["reference", "example", "asset", "script"]
    size_bytes: int = Field(ge=0)


class SkillDocument(BaseModel):
    """Activated skill instructions plus its available resource inventory."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    metadata: SkillMetadata
    instructions: str
    resources: tuple[SkillResource, ...] = ()
    fingerprint: str


class SkillIssue(BaseModel):
    """One deterministic validation finding."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    severity: SkillSeverity
    code: str
    message: str
    path: str


class SkillSearchResult(BaseModel):
    """Compact search result safe to expose to a model or API client."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    description: str
    category: str
    risk: SkillRisk
    score: float = Field(ge=0.0)
