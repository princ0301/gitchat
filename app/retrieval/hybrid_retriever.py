from app.core.interfaces.graph_store import GraphStore
from app.core.types import RetrievalResult, EdgeType
from app.retrieval.vector_store import ChunkVectorStore

EXPANSION_EDGE_TYPES = (EdgeType.CALLS, EdgeType.IMPORTS, EdgeType.CONTAINS)
DEFAULT_VECTOR_K = 5
DEFAULT_EXPANSION_HOPS = 1
HOP_DECAY_FACTOR = 0.6


class HybridRetriever:
    def __init__(self, graph_store: GraphStore, vector_store: ChunkVectorStore):
        self._graph_store = graph_store
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        vector_k: int = DEFAULT_VECTOR_K,
        expansion_hops: int = DEFAULT_EXPANSION_HOPS,
    ) -> list[RetrievalResult]:
        vector_hits = self._vector_store.similarity_search(query, k=vector_k)
        results_by_node_id: dict[str, RetrievalResult] = {}

        for hit in vector_hits:
            results_by_node_id[hit["node_id"]] = self._build_vector_result(hit)

        for hit in vector_hits:
            origin_relevance = self._vector_score_to_relevance(hit["score"])
            self._expand_from_node(hit["node_id"], expansion_hops, origin_relevance, results_by_node_id)

        return self._rank(list(results_by_node_id.values()))

    def _build_vector_result(self, hit: dict) -> RetrievalResult:
        return RetrievalResult(
            node_id=hit["node_id"],
            name=hit["name"],
            symbol_type=hit["symbol_type"],
            file_path=hit["file_path"],
            start_line=hit["start_line"],
            end_line=hit["end_line"],
            text=hit["text"],
            vector_score=hit["score"],
            graph_distance=0,
            relevance_score=self._vector_score_to_relevance(hit["score"]),
            source="vector",
        )

    def _expand_from_node(
        self,
        start_node_id: str,
        max_hops: int,
        origin_relevance: float,
        results_by_node_id: dict[str, RetrievalResult],
    ) -> None:
        frontier = [start_node_id]
        visited = {start_node_id}

        for hop in range(1, max_hops + 1):
            next_frontier = []
            hop_relevance = origin_relevance * (HOP_DECAY_FACTOR ** hop)
            for node_id in frontier:
                neighbors = self._get_all_neighbors(node_id)
                for neighbor_id in neighbors:
                    if neighbor_id in visited:
                        continue
                    visited.add(neighbor_id)
                    next_frontier.append(neighbor_id)
                    self._add_or_update_graph_result(neighbor_id, hop, hop_relevance, results_by_node_id)
            frontier = next_frontier

    def _get_all_neighbors(self, node_id: str) -> list[str]:
        neighbors = []
        for edge_type in EXPANSION_EDGE_TYPES:
            neighbors.extend(self._graph_store.get_neighbors(node_id, edge_type, direction="out"))
            neighbors.extend(self._graph_store.get_neighbors(node_id, edge_type, direction="in"))
        return neighbors

    def _add_or_update_graph_result(
        self,
        node_id: str,
        hop_distance: int,
        candidate_relevance: float,
        results_by_node_id: dict[str, RetrievalResult],
    ) -> None:
        symbol = self._graph_store.get_node(node_id)
        if symbol is None:
            return

        if node_id in results_by_node_id:
            existing = results_by_node_id[node_id]
            best_relevance = max(existing.relevance_score, candidate_relevance)
            best_distance = (
                min(existing.graph_distance, hop_distance)
                if existing.graph_distance is not None
                else hop_distance
            )
            results_by_node_id[node_id] = RetrievalResult(
                node_id=existing.node_id,
                name=existing.name,
                symbol_type=existing.symbol_type,
                file_path=existing.file_path,
                start_line=existing.start_line,
                end_line=existing.end_line,
                text=existing.text,
                vector_score=existing.vector_score,
                graph_distance=best_distance,
                relevance_score=best_relevance,
                source="both" if existing.source == "vector" else existing.source,
            )
            return

        results_by_node_id[node_id] = RetrievalResult(
            node_id=node_id,
            name=symbol.name,
            symbol_type=symbol.symbol_type.value,
            file_path=symbol.file_path,
            start_line=symbol.start_line,
            end_line=symbol.end_line,
            text=symbol.docstring or symbol.signature or symbol.name,
            vector_score=None,
            graph_distance=hop_distance,
            relevance_score=candidate_relevance,
            source="graph",
        )

    def _vector_score_to_relevance(self, score: float) -> float:
        return max(0.0, 1.0 - score)

    def _rank(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        return sorted(results, key=lambda r: r.relevance_score, reverse=True)