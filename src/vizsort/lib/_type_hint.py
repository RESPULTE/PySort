from typing import TypeVar, Any
from abc import ABC, abstractmethod


class ComparableType(ABC):
    @abstractmethod
    def __lt__(self, other: Any) -> bool:
        ...

    @abstractmethod
    def __gt__(self, other: Any) -> bool:
        ...

    @abstractmethod
    def __le__(self, other: Any) -> bool:
        ...

    @abstractmethod
    def __ge__(self, other: Any) -> bool:
        ...


CT = TypeVar("CT", bound=ComparableType)
