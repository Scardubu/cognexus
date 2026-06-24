"""Tool Search configuration for deferred OpenAI Agents SDK tools."""

from __future__ import annotations

from agents import ToolSearchTool


def build_tool_search() -> ToolSearchTool:
    """Return the SDK tool-search tool used to load deferred tools."""
    return ToolSearchTool(
        description=(
            "Search the NEXUS specialist tool catalog and load only tools relevant "
            "to the current engineering task."
        )
    )
