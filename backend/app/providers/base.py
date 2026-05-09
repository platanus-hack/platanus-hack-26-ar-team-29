"""Provider + Capability ABCs — see 02-1_backend_architechture.md §5."""

from abc import ABC, abstractmethod


class Capability(ABC):  # noqa: B024  -- marker base; concrete capability ABCs subclass this
    pass


class Provider(ABC):
    name: str

    @abstractmethod
    async def healthcheck(self) -> bool: ...
