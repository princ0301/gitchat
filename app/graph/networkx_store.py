import json
from pathlib import Path
import networkx as nx

from app.core.interfaces.graph_store import GraphStore
from app.core.types import Symbol, SymbolType, EdgeType


class NetworkXGraphStore(GraphStore):
    def __init__(self):
        self._graph = nx.MultiDiGraph()

    def add_node(self, node_id: str, symbol: Symbol) -> None:
        self._graph.add_node(
            node_id,
            symbol_type=symbol.symbol_type.value,
            name=symbol.name,
            file_path=symbol.file_path,
            start_line=symbol.start_line,
            end_line=symbol.end_line,
            parent_name=symbol.parent_name,
            signature=symbol.signature,
            docstring=symbol.docstring,
        )

    def add_edge(self, source_id: str, target_id: str, edge_type: EdgeType) -> None:
        self._graph.add_edge(source_id, target_id, edge_type=edge_type.value)

    def has_node(self, node_id: str) -> bool:
        return self._graph.has_node(node_id)

    def get_node(self, node_id: str) -> Symbol | None:
        if node_id not in self._graph.nodes:
            return None
        data = self._graph.nodes[node_id]
        return Symbol(
            symbol_type=SymbolType(data["symbol_type"]),
            name=data["name"],
            file_path=data["file_path"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            parent_name=data["parent_name"],
            signature=data["signature"],
            docstring=data["docstring"],
        )

    def get_neighbors(self, node_id: str, edge_type: EdgeType, direction: str) -> list[str]:
        if node_id not in self._graph.nodes:
            return []
        if direction == "out":
            edges = self._graph.out_edges(node_id, data=True)
            return [v for _, v, data in edges if data.get("edge_type") == edge_type.value]
        if direction == "in":
            edges = self._graph.in_edges(node_id, data=True)
            return [u for u, _, data in edges if data.get("edge_type") == edge_type.value]
        raise ValueError(f"direction must be 'in' or 'out', got: {direction}")

    def get_callers(self, node_id: str) -> list[str]:
        return self.get_neighbors(node_id, EdgeType.CALLS, direction="in")

    def get_dependents(self, node_id: str) -> list[str]:
        callers = self.get_neighbors(node_id, EdgeType.CALLS, direction="in")
        importers = self.get_neighbors(node_id, EdgeType.IMPORTS, direction="in")
        return list(set(callers + importers))

    def node_count(self) -> int:
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        return self._graph.number_of_edges()

    def save(self, path: str) -> None:
        data = nx.node_link_data(self._graph, edges="edges")
        Path(path).write_text(json.dumps(data), encoding="utf-8")

    def load(self, path: str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self._graph = nx.node_link_graph(data, edges="edges", multigraph=True, directed=True)