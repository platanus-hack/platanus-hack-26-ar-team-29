"""ProviderRegistry — see 02-1_backend_architechture.md §5."""

from app.providers.base import Capability, Provider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        return self._providers[name]

    def find_for_capability(
        self, user_id: str, capability: type[Capability]
    ) -> list[Provider]:
        raise NotImplementedError("Implemented when first provider lands.")
