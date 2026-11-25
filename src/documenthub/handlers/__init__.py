from documenthub.core.registry import FormatRegistry
from documenthub.handlers.txt import TxtHandler


def build_default_registry()->FormatRegistry:
    registry = FormatRegistry()
    registry.register(TxtHandler())
    return registry


__all__ = ["TxtHandler","build_default_registry"]
