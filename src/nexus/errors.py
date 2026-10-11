"""Typed errors exposed by provider adapters."""


class NexusError(Exception):
    """Base error for expected AI Nexus failures."""


class ProviderError(NexusError):
    """Raised when a provider cannot satisfy a request."""
