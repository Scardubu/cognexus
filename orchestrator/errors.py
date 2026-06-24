"""Stable orchestration-domain exceptions for CLI and HTTP adapters."""


class NexusExecutionError(RuntimeError):
    """Base class for failures safe to map at an application boundary."""


class NexusOutputValidationError(NexusExecutionError):
    """Raised when final model output violates deterministic production policy."""


class NexusOutputTooLargeError(NexusExecutionError):
    """Raised when final model output exceeds the configured response limit."""
