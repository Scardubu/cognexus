"""OpenAI Agents SDK tools for portable skill discovery and activation."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from agents import FunctionTool, function_tool
from agents.tool_context import ToolContext

from skill_runtime.loader import SkillLoadError, SkillRegistry
from skill_runtime.security import SkillSecurityError


def build_skill_tools(registry: SkillRegistry) -> list[Any]:
    """Build small discovery tools while keeping skill bodies out of base context."""

    @function_tool(
        name_override="search_skills",
        description_override=(
            "Search the installed Cognexus Agent Skills catalog by task or domain. "
            "Returns metadata only; call activate_skill before following a skill."
        ),
        timeout=5.0,
    )
    async def search_skills(query: str, limit: int = 8) -> dict[str, Any]:
        """Search installed skills using a short natural-language query."""
        try:
            results = await asyncio.to_thread(registry.search, query, limit=limit)
            return {"ok": True, "results": [item.model_dump(mode="json") for item in results]}
        except (SkillLoadError, SkillSecurityError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}

    names = [item.name for item in registry.metadata()]
    activate_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "enum": names,
                "description": "Exact installed skill name returned by search_skills.",
            }
        },
        "required": ["name"],
        "additionalProperties": False,
    }

    async def activate(context: ToolContext[Any], arguments: str) -> dict[str, Any]:
        del context
        try:
            payload = json.loads(arguments)
            if not isinstance(payload, dict):
                raise ValueError("arguments must be a JSON object")
            document = await asyncio.to_thread(registry.activate, str(payload.get("name", "")))
            return {
                "ok": True,
                "skill": {
                    "name": document.metadata.name,
                    "description": document.metadata.description,
                    "category": document.metadata.category,
                    "risk": document.metadata.risk,
                    "instructions": document.instructions,
                    "resources": [
                        resource.model_dump(mode="json") for resource in document.resources
                    ],
                    "fingerprint": document.fingerprint,
                },
            }
        except (json.JSONDecodeError, SkillLoadError, SkillSecurityError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}

    activate_skill = FunctionTool(
        name="activate_skill",
        description=(
            "Load one installed Agent Skill after its description matches the current task. "
            "The result contains instructions and a resource inventory; follow the skill before acting."
        ),
        params_json_schema=activate_schema,
        on_invoke_tool=activate,
        strict_json_schema=True,
        timeout_seconds=5.0,
    )

    @function_tool(
        name_override="read_skill_resource",
        description_override=(
            "Read one text reference explicitly named by an activated skill. Paths must be under "
            "references/, examples/, assets/, or scripts/. This tool never executes scripts."
        ),
        timeout=5.0,
        defer_loading=True,
    )
    async def read_skill_resource(name: str, relative_path: str) -> dict[str, Any]:
        """Read a bounded UTF-8 skill resource without executing it."""
        try:
            content = await asyncio.to_thread(registry.read_resource, name, relative_path)
            return {
                "ok": True,
                "name": name,
                "path": relative_path,
                "content": content,
            }
        except (SkillLoadError, SkillSecurityError, ValueError) as exc:
            return {"ok": False, "error": str(exc)}

    return [search_skills, activate_skill, read_skill_resource]
