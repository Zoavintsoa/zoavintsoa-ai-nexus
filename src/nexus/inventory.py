"""Model inventory and capability metadata without guessing unsupported abilities."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from nexus.errors import ProviderError


@dataclass(frozen=True)
class ModelProfile:
    name: str
    size_bytes: int | None = None
    family: str | None = None
    parameter_size: str | None = None
    quantization: str | None = None
    capabilities: tuple[str, ...] = ()
    details_available: bool = True
    details_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = list(self.capabilities)
        return data


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def profile_model(client: Any, model: dict[str, Any]) -> ModelProfile:
    """Build a profile using Ollama's reported metadata, never model-name guesses."""
    name = _text(model.get("name")) or _text(model.get("model"))
    if not name:
        raise ProviderError("Ollama returned a model without a name.")
    size = model.get("size")
    size_bytes = size if isinstance(size, int) and size >= 0 else None
    try:
        details = client.show_model(name)
    except Exception as exc:
        return ModelProfile(
            name=name,
            size_bytes=size_bytes,
            details_available=False,
            details_error=str(exc),
        )

    details = details if isinstance(details, dict) else {}
    details_blob = details.get("details")
    details_blob = details_blob if isinstance(details_blob, dict) else {}
    info = details.get("model_info")
    info = info if isinstance(info, dict) else {}
    capabilities = details.get("capabilities", [])
    capabilities = tuple(
        sorted({item.strip() for item in capabilities if isinstance(item, str) and item.strip()})
    ) if isinstance(capabilities, list) else ()
    return ModelProfile(
        name=name,
        size_bytes=size_bytes,
        family=_text(details_blob.get("family")),
        parameter_size=_text(details_blob.get("parameter_size")),
        quantization=_text(details_blob.get("quantization_level")),
        capabilities=capabilities,
    )


def inventory(client: Any) -> list[ModelProfile]:
    """Return profiles for all locally installed Ollama models."""
    return [profile_model(client, item) for item in client.list_models()]
