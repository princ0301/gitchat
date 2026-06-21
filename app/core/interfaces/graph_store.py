from abc import ABC, abstractmethod
from app.core.types import Symbol, EdgeType


class GraphStore(ABC):
    @abstractmethod
    def add_node(self, node_id: str, symbol: Symbol) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType) -> None:
        raise NotImplementedError

    @abstractmethod
    def has_node(self, node_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_node(self, node_id: str) -> Symbol | None:
        raise NotImplementedError

    @abstractmethod
    def get_neighbors(self, node_id: str, edge_type: EdgeType, direction: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_callers(self, node_id: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def get_dependents(self, node_id: str) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def node_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def edge_count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> None:
        raise NotImplementedError