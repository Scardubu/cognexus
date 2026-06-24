"""Compatibility shim for the previous tracing import path."""

from observability.tracing import configure_tracing, get_trace_id, get_tracer, span

__all__ = ["configure_tracing", "get_trace_id", "get_tracer", "span"]
